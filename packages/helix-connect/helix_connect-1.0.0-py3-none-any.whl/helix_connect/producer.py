# Helix Producer SDK
# For data producers who want to upload and manage datasets

import copy
import gzip
import io
import json
import os
import re
import struct
import tempfile
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional
from urllib.parse import quote

import boto3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from genson import SchemaBuilder

from .consumer import HelixConsumer
from .exceptions import HelixError, UploadError


class HelixProducer(HelixConsumer):
    """
    SDK for data producers to upload and manage datasets on Helix Connect.
    Inherits from HelixConsumer, so producers can also consume data.

    Args:
        aws_access_key_id: AWS access key ID from customer onboarding
        aws_secret_access_key: AWS secret access key from customer onboarding
        customer_id: Unique customer ID (UUID)
        api_endpoint: API Gateway endpoint (default: production endpoint)
        region: AWS region (default: us-east-1)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Re-export boto3 via an instance attribute so legacy tests that patch
        # helix_connect.producer.boto3 keep working without touching consumer.py.
        self._boto3 = boto3

        # Get producer-specific resources from SSM
        try:
            bucket_param = f"/helix/customers/{self.customer_id}/s3_bucket"
            response = self.ssm.get_parameter(Name=bucket_param)
            self.bucket_name = response["Parameter"]["Value"]
        except Exception as e:
            raise HelixError(
                f"S3 bucket not found for producer {self.customer_id}: {e}"
            )

        # Get producer KMS key for encryption
        try:
            kms_param = f"/helix/customers/{self.customer_id}/kms_key_id"
            response = self.ssm.get_parameter(Name=kms_param)
            self.kms_key_id = response["Parameter"]["Value"]
        except Exception as e:
            print(f"Warning: KMS key not found, encryption will be disabled: {e}")
            self.kms_key_id = None

        # Initialize KMS client using session (not direct boto3.client)
        # This ensures the producer's credentials are used for KMS operations
        self.kms = self.session.client("kms")

    def _encrypt_data(self, data: bytes) -> bytes:
        """
        Encrypt data using envelope encryption to support files > 4KB.

        Process:
        1. Generate random data key (32 bytes for AES-256)
        2. Encrypt data with the data key (no size limit)
        3. Encrypt the data key with KMS (only 32 bytes)
        4. Return: [key_length][encrypted_key][iv][tag][encrypted_data]

        Args:
            data: Raw data bytes

        Returns:
            Encrypted data bytes with envelope encryption format
        """
        if not self.kms_key_id:
            raise HelixError("KMS key not configured, cannot encrypt data")

        try:
            # Generate random data key and IV
            data_key = os.urandom(32)  # 256-bit key for AES-256
            iv = os.urandom(16)  # 128-bit IV for GCM mode

            # Encrypt data with data key using AES-256-GCM
            cipher = Cipher(
                algorithms.AES(data_key), modes.GCM(iv), backend=default_backend()
            )
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(data) + encryptor.finalize()
            auth_tag = encryptor.tag

            # Encrypt the data key with KMS (only 32 bytes, well under 4KB limit)
            response = self.kms.encrypt(KeyId=self.kms_key_id, Plaintext=data_key)
            encrypted_key = response["CiphertextBlob"]

            # Package: [4 bytes: key length][encrypted key][16 bytes: IV][16 bytes: tag][encrypted data]
            result = struct.pack(
                ">I", len(encrypted_key)
            )  # 4 bytes: encrypted key length
            result += encrypted_key
            result += iv
            result += auth_tag
            result += encrypted_data

            return result
        except Exception as e:
            raise HelixError(f"Encryption failed: {e}")

    def _compress_data(self, data: bytes, level: int = 6) -> bytes:
        """
        Compress data using gzip.

        Args:
            data: Data to compress
            level: Compression level (1-9, default 6)

        Returns:
            Compressed data bytes
        """
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="wb", compresslevel=level) as gz:
            gz.write(data)
        return out.getvalue()

    def _is_empty_value(self, value: Any) -> bool:
        """
        Check if a value is considered empty.

        Empty values include: None, empty string, empty list, empty dict,
        and strings containing only whitespace.

        Args:
            value: The value to check

        Returns:
            True if the value is considered empty
        """
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False

    def _analyze_data(
        self, file_path: str, schema_sample_limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Analyze dataset to extract schema and field emptiness statistics.

        This method efficiently streams through the file to:
        1. Infer JSON schema by sampling multiple records (default: first 1000)
        2. Calculate the percentage of records where each field is missing or empty

        Memory efficiency is achieved by processing line-by-line rather than
        loading the entire file into memory.

        Args:
            file_path: Path to the NDJSON file to analyze
            schema_sample_limit: Number of records to sample for schema inference
                                 (default: 1000, use 0 for all records)

        Returns:
            Dict containing:
                - schema: JSON Schema inferred from sampled records
                - field_emptiness: Dict mapping field names to empty/missing percentages
                - record_count: Total number of records analyzed
                - analysis_errors: Count of records that failed to parse

        Example:
            >>> result = producer._analyze_data("/path/to/data.ndjson")
            >>> print(result['schema'])
            {'type': 'object', 'properties': {'name': {'type': 'string'}, ...}}
            >>> print(result['field_emptiness'])
            {'phone': 15.3, 'email': 5.2, 'name': 0.0}  # % of records missing/empty
        """
        schema_builder = SchemaBuilder()
        all_fields: set = set()  # All discovered field paths
        field_present_count: Dict[str, int] = (
            {}
        )  # Records where field is present & non-empty
        record_count = 0
        analysis_errors = 0

        print("📊 Analyzing dataset for schema and field statistics...")

        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    analysis_errors += 1
                    if analysis_errors <= 5:
                        print(f"  Warning: Failed to parse line {line_num}: {e}")
                    continue

                record_count += 1

                # Infer schema from first N records for complete type coverage
                if schema_sample_limit == 0 or record_count <= schema_sample_limit:
                    schema_builder.add_object(record)

                # Collect all fields and which are present/non-empty in this record
                discovered, present = self._get_field_status(record, "")

                # Track all discovered fields across all records
                all_fields.update(discovered)

                # Count records where each field is present and non-empty
                for field in present:
                    field_present_count[field] = field_present_count.get(field, 0) + 1

        # Calculate emptiness: % of records where field is missing OR empty
        # emptiness = (total_records - present_non_empty_count) / total_records * 100
        field_emptiness: Dict[str, float] = {}
        for field in all_fields:
            present = field_present_count.get(field, 0)
            missing_or_empty = record_count - present
            percentage = (
                (missing_or_empty / record_count * 100) if record_count > 0 else 0.0
            )
            field_emptiness[field] = round(percentage, 2)

        # Sort by emptiness percentage (highest first) for easier review
        field_emptiness = dict(
            sorted(field_emptiness.items(), key=lambda x: x[1], reverse=True)
        )

        # Build the final schema
        schema = schema_builder.to_schema() if record_count > 0 else {}

        result = {
            "schema": schema,
            "field_emptiness": field_emptiness,
            "record_count": record_count,
            "analysis_errors": analysis_errors,
        }

        # Print summary
        non_empty_fields = sum(1 for v in field_emptiness.values() if v == 0.0)
        partially_empty = sum(1 for v in field_emptiness.values() if 0 < v < 100)
        fully_empty = sum(1 for v in field_emptiness.values() if v == 100)

        print(f"  Records analyzed: {record_count}")
        print(
            f"  Schema sampled from: {min(record_count, schema_sample_limit) if schema_sample_limit else record_count} records"
        )
        print(f"  Fields discovered: {len(field_emptiness)}")
        print(f"    - Complete (0% empty): {non_empty_fields}")
        print(f"    - Partial (1-99% empty): {partially_empty}")
        print(f"    - Empty (100% empty): {fully_empty}")
        if analysis_errors > 0:
            print(f"  Parse errors: {analysis_errors}")

        return result

    def _get_field_status(self, obj: Any, prefix: str) -> tuple:
        """
        Recursively collect field paths and their presence status.

        Handles nested objects using dot notation (e.g., "address.city").

        Args:
            obj: The object to analyze (dict, list, or primitive)
            prefix: Current field path prefix

        Returns:
            Tuple of (all_fields, present_non_empty_fields):
                - all_fields: Set of all discovered field paths
                - present_non_empty_fields: Set of fields that have non-empty values
        """
        all_fields: set = set()
        present_fields: set = set()

        if isinstance(obj, dict):
            for key, value in obj.items():
                field_path = f"{prefix}.{key}" if prefix else key

                # Always track discovered fields
                all_fields.add(field_path)

                # Only count as present if value is non-empty
                if not self._is_empty_value(value):
                    present_fields.add(field_path)

                    # Recurse into nested objects
                    if isinstance(value, dict):
                        nested_all, nested_present = self._get_field_status(
                            value, field_path
                        )
                        all_fields.update(nested_all)
                        present_fields.update(nested_present)
                    elif isinstance(value, list) and value:
                        # For arrays of objects, analyze each item
                        if isinstance(value[0], dict):
                            for item in value:
                                if isinstance(item, dict):
                                    nested_all, nested_present = self._get_field_status(
                                        item, f"{field_path}[]"
                                    )
                                    all_fields.update(nested_all)
                                    present_fields.update(nested_present)

        return all_fields, present_fields

    def _slugify(self, value: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9-]+", "-", value.lower()).strip("-")
        return cleaned or "dataset"

    def _generate_dataset_id(
        self, dataset_name: str, explicit_id: Optional[str] = None
    ) -> str:
        if explicit_id:
            return explicit_id
        slug = self._slugify(dataset_name)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"{self.customer_id}-{slug}-{timestamp}"

    def _default_pricing(self) -> Dict[str, Any]:
        return {
            "basic": {"amount": 0, "currency": "USD", "interval": "monthly"},
            "professional": {"amount": 0, "currency": "USD", "interval": "monthly"},
            "enterprise": {"amount": 0, "currency": "USD", "interval": "monthly"},
        }

    def _default_stats(self) -> Dict[str, Any]:
        return {
            "subscriber_count": 0,
            "download_count": 0,
            "download_count_7d": 0,
            "download_count_30d": 0,
            "view_count": 0,
            "last_downloaded_at": None,
            "avg_download_size_mb": 0,
        }

    def _default_validation(self, record_count: int) -> Dict[str, Any]:
        return {
            "validated": False,
            "validation_errors": [],
            "row_count": record_count,
            "data_quality_score": 0,
        }

    def _deep_merge_dict(
        self, base: Dict[str, Any], overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        for key, value in overrides.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_dict(base[key], value)
            else:
                base[key] = value
        return base

    def _build_dataset_payload(
        self,
        dataset_name: str,
        description: str,
        category: str,
        data_freshness: str,
        s3_key: str,
        final_size: int,
        combined_metadata: Dict[str, Any],
        analysis: Optional[Dict[str, Any]] = None,
        dataset_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        dataset_overrides = copy.deepcopy(dataset_overrides or {})
        explicit_id = dataset_overrides.pop("_id", None) or dataset_overrides.pop(
            "id", None
        )
        dataset_id = self._generate_dataset_id(dataset_name, explicit_id)

        record_count = analysis.get("record_count", 0) if analysis else 0
        schema = analysis.get("schema", {}) if analysis else {}
        field_emptiness = analysis.get("field_emptiness", {}) if analysis else {}

        metadata_payload = copy.deepcopy(combined_metadata)
        metadata_payload.setdefault("file_format", "json")
        metadata_payload.setdefault("encoding", "utf-8")
        metadata_payload["schema"] = schema
        metadata_payload["field_emptiness"] = field_emptiness
        metadata_payload["record_count"] = record_count
        if analysis and analysis.get("analysis_errors"):
            metadata_payload["analysis_errors"] = analysis["analysis_errors"]

        now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        date_version = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        pricing = self._default_pricing()
        if "pricing" in dataset_overrides:
            pricing = self._deep_merge_dict(pricing, dataset_overrides.pop("pricing"))

        stats = self._default_stats()
        if "stats" in dataset_overrides:
            stats = self._deep_merge_dict(stats, dataset_overrides.pop("stats"))

        validation = self._default_validation(record_count)
        if "validation" in dataset_overrides:
            validation = self._deep_merge_dict(
                validation, dataset_overrides.pop("validation")
            )

        tags = dataset_overrides.pop("tags", []) or []
        last_updated = dataset_overrides.get("last_updated", now_iso)
        created_at = dataset_overrides.get("created_at", now_iso)
        updated_at = dataset_overrides.get("updated_at", now_iso)

        payload = {
            "_id": dataset_id,
            "id": dataset_id,
            "name": dataset_name,
            "description": description,
            "producer_id": self.customer_id,
            "category": category,
            "data_freshness": data_freshness,
            "visibility": dataset_overrides.get("visibility", "private"),
            "status": dataset_overrides.get("status", "active"),
            "s3_key": s3_key,
            "s3_bucket": self.bucket_name,
            "size_bytes": final_size,
            "record_count": record_count,
            "version": dataset_overrides.get("version", date_version),
            "version_notes": dataset_overrides.get("version_notes", ""),
            "parent_dataset_id": dataset_overrides.get("parent_dataset_id"),
            "is_latest_version": dataset_overrides.get("is_latest_version", True),
            "metadata": metadata_payload,
            "schema": schema,
            "validation": validation,
            "tags": tags,
            "pricing": pricing,
            "stats": stats,
            "last_updated": last_updated,
            "created_at": created_at,
            "created_by": dataset_overrides.get("created_by", self.customer_id),
            "updated_at": updated_at,
            "updated_by": dataset_overrides.get("updated_by", self.customer_id),
            "deleted_at": dataset_overrides.get("deleted_at"),
            "deleted_by": dataset_overrides.get("deleted_by"),
        }

        # Allow remaining overrides (including future schema fields)
        for key, value in dataset_overrides.items():
            if (
                key in payload
                and isinstance(payload[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge_dict(payload[key], value)
            else:
                payload[key] = value

        return payload

    def upload_dataset(
        self,
        file_path: str,
        dataset_name: str,
        description: str = "",
        category: str = "general",
        data_freshness: str = "4x-per-day",
        metadata: Optional[Dict[str, Any]] = None,
        dataset_overrides: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        encrypt: bool = True,
        compress: bool = True,
        compression_level: int = 6,
    ) -> Dict:
        """
        Upload a dataset with encryption and compression.

        Security and Performance Defaults (v2.0+):
            - Encryption is ENABLED by default (KMS envelope encryption)
            - Compression is ENABLED by default (gzip compression level 6)
            - This provides security by default and reduces S3 storage costs

        To disable (not recommended for sensitive data):
            producer.upload_dataset(..., encrypt=False, compress=False)

        Args:
            file_path: Local path to the dataset file
            dataset_name: Name for the dataset
            description: Description of the dataset
            category: Dataset category (default: "general")
            data_freshness: How often data is updated (default: "4x-per-day")
            metadata: Optional additional metadata
            dataset_overrides: Optional dict of dataset schema fields to override
            progress_callback: Optional callback function(bytes_uploaded, total_bytes)
            encrypt: Enable KMS encryption (default: True for security)
            compress: Enable gzip compression (default: True for cost optimization)
            compression_level: Gzip compression level 1-9 (default: 6, balanced speed/size)

        Returns:
            Dataset object with ID and metadata

        Raises:
            UploadError: If file not found or upload fails
            HelixError: If encryption/compression fails

        Example:
            >>> producer = HelixProducer(...)
            >>> # Upload with secure defaults (encrypted + compressed)
            >>> dataset = producer.upload_dataset(
            ...     file_path="/path/to/data.ndjson",
            ...     dataset_name="my-dataset",
            ...     description="My dataset"
            ... )
            >>> print(f"Uploaded: {dataset['s3_key']}")
        """
        if not os.path.exists(file_path):
            raise UploadError(f"File not found: {file_path}")

        original_size = os.path.getsize(file_path)

        # Analyze data before compression/encryption (memory-efficient streaming)
        # This extracts JSON schema and field emptiness statistics
        try:
            analysis = self._analyze_data(file_path)
        except Exception as e:
            print(f"Warning: Data analysis failed, continuing without analysis: {e}")
            analysis = None

        # Read original file
        with open(file_path, "rb") as f:
            data = f.read()

        # Track sizes for metadata
        sizes = {
            "original_size_bytes": original_size,
            "compressed_size_bytes": original_size,
            "encrypted_size_bytes": original_size,
            "encryption_enabled": encrypt,
            "compression_enabled": compress,
        }

        # Step 1: Compress FIRST (if enabled)
        # Compression works best on unencrypted data due to patterns/redundancy
        if compress:
            print(
                f"📦 Compressing {len(data)} bytes with gzip (level {compression_level})..."
            )
            data = self._compress_data(data, level=compression_level)
            sizes["compressed_size_bytes"] = len(data)
            compression_ratio = (1 - len(data) / original_size) * 100
            print(f"Compressed: {len(data)} bytes ({compression_ratio:.1f}% reduction)")

        # Step 2: Encrypt SECOND (if enabled)
        # Encrypt the compressed data for security
        if encrypt:
            if not self.kms_key_id:
                print(
                    "Warning: Encryption requested but KMS key not found. Skipping encryption."
                )
                encrypt = False
                sizes["encryption_enabled"] = False
            else:
                print(f"Encrypting {len(data)} bytes with KMS key...")
                data = self._encrypt_data(data)
                sizes["encrypted_size_bytes"] = len(data)
                print(f"Encrypted: {len(data)} bytes")

        # Generate S3 key with consistent filename (no date, no randomness)
        # This enables in-place updates - same dataset name = same S3 key = file overwrite
        file_name = "data.ndjson"
        if compress:
            file_name += ".gz"
        s3_key = f"datasets/{dataset_name}/{file_name}"

        # Build S3 object tags for cost tracking
        # Format: CustomerID=value&Component=storage&Purpose=dataset-storage&DatasetName=value
        tags = (
            f"CustomerID={quote(self.customer_id)}"
            f"&Component={quote('storage')}"
            f"&Purpose={quote('dataset-storage')}"
            f"&DatasetName={quote(dataset_name)}"
        )

        # Write processed file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        try:
            # Upload to S3 with tags
            print(f"Uploading {len(data)} bytes to S3...")
            if progress_callback:
                self.s3.upload_file(
                    tmp_path,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={"Tagging": tags},
                    Callback=lambda bytes_transferred: progress_callback(
                        bytes_transferred, len(data)
                    ),
                )
            else:
                self.s3.upload_file(
                    tmp_path, self.bucket_name, s3_key, ExtraArgs={"Tagging": tags}
                )

            print(
                f"Uploaded to s3://{self.bucket_name}/{s3_key} (tagged: CustomerID={self.customer_id})"
            )

        except Exception as e:
            raise UploadError(f"Failed to upload file: {e}")
        finally:
            # Clean up temp file - use try/finally to ensure cleanup even on error
            try:
                os.unlink(tmp_path)
            except Exception as cleanup_error:
                print(
                    f"Warning: Failed to clean up temp file {tmp_path}: {cleanup_error}"
                )

        # Build metadata with analysis results
        combined_metadata = {**(metadata or {}), **sizes}

        # Determine final size (what's actually stored in S3)
        # If encrypted, use encrypted size; otherwise use compressed size
        final_size = (
            sizes["encrypted_size_bytes"]
            if sizes["encryption_enabled"]
            else sizes["compressed_size_bytes"]
        )

        dataset_payload = self._build_dataset_payload(
            dataset_name=dataset_name,
            description=description,
            category=category,
            data_freshness=data_freshness,
            s3_key=s3_key,
            final_size=final_size,
            combined_metadata=combined_metadata,
            analysis=analysis,
            dataset_overrides=dataset_overrides,
        )

        try:
            dataset = self._make_api_request(
                "POST", "/v1/datasets", json=dataset_payload
            )
            return dataset
        except Exception as e:
            # Upload succeeded but registration failed - log warning
            print(f"Warning: File uploaded but catalog registration failed: {e}")
            return {
                "status": "uploaded_unregistered",
                "s3_key": s3_key,
                "error": str(e),
                "payload": dataset_payload,
            }

    def update_dataset(
        self,
        dataset_id: str,
        file_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict:
        """
        Update an existing dataset with new data.

        Args:
            dataset_id: ID of the dataset to update
            file_path: Local path to the new dataset file
            progress_callback: Optional callback function(bytes_uploaded, total_bytes)

        Returns:
            Updated dataset object
        """
        # Get existing dataset
        dataset = self.get_dataset(dataset_id)

        # Upload new file using the same key pattern
        return self.upload_dataset(
            file_path=file_path,
            dataset_name=dataset["name"],
            description=dataset.get("description", ""),
            category=dataset.get("category", "general"),
            data_freshness=dataset.get("data_freshness", "daily"),
            metadata=dataset.get("metadata"),
            progress_callback=progress_callback,
        )

    def list_my_datasets(self) -> list:
        """
        List all datasets uploaded by this producer.

        Returns:
            List of dataset objects
        """
        return self.list_datasets(producer_id=self.customer_id)

    def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete a dataset (marks as deleted, doesn't remove from S3 immediately).

        Args:
            dataset_id: Dataset ID to delete

        Returns:
            True if successful
        """
        # TODO: Implement DELETE /v1/datasets/{id} endpoint
        raise NotImplementedError("Dataset deletion not yet implemented")

    def list_subscription_requests(self, status: Optional[str] = None) -> Dict:
        """
        List subscription requests from consumers wanting access to this producer's data.

        Args:
            status: Filter by status ('pending', 'approved', 'rejected') - optional

        Returns:
            Dict with 'requests' list and 'count'

        Example:
            >>> producer = HelixProducer(...)
            >>> result = producer.list_subscription_requests(status='pending')
            >>> for req in result['requests']:
            ...     print(f"Consumer: {req['consumer_id']}")
            ...     print(f"Dataset: {req.get('dataset_id', 'All datasets')}")
            ...     print(f"Message: {req.get('message', 'No message')}")
        """
        endpoint = "/v1/producers/subscription-requests"
        if status:
            endpoint += f"?status={status}"

        return self._make_api_request("GET", endpoint)

    def approve_subscription_request(
        self, request_id: str, notes: Optional[str] = None
    ) -> Dict:
        """
        Approve a subscription request from a consumer.
        This will create the subscription, grant KMS decrypt permissions, and set up notifications.

        Args:
            request_id: The subscription request ID to approve
            notes: Optional notes about the approval

        Returns:
            Dict containing the created subscription details

        Example:
            >>> producer = HelixProducer(...)
            >>> subscription = producer.approve_subscription_request(
            ...     request_id="req-123-456",
            ...     notes="Welcome! Approved for premium tier."
            ... )
            >>> print(f"Subscription ID: {subscription['_id']}")
            >>> print(f"Status: {subscription['status']}")  # 'active'
        """
        payload = {"action": "approve"}
        if notes:
            payload["notes"] = notes

        return self._make_api_request(
            "POST", f"/v1/subscription-requests/{request_id}", data=payload
        )

    def reject_subscription_request(
        self, request_id: str, reason: Optional[str] = None
    ) -> Dict:
        """
        Reject a subscription request from a consumer.

        Args:
            request_id: The subscription request ID to reject
            reason: Optional reason for rejection

        Returns:
            Dict containing the updated request details

        Example:
            >>> producer = HelixProducer(...)
            >>> result = producer.reject_subscription_request(
            ...     request_id="req-123-456",
            ...     reason="Data not available for your use case"
            ... )
            >>> print(f"Status: {result['status']}")  # 'rejected'
        """
        payload = {"action": "reject"}
        if reason:
            payload["reason"] = reason

        return self._make_api_request(
            "POST", f"/v1/subscription-requests/{request_id}", data=payload
        )

    def list_subscribers(self) -> Dict:
        """
        List all active subscribers to this producer's datasets.

        Returns:
            Dict with 'subscribers' list and 'count'

        Example:
            >>> producer = HelixProducer(...)
            >>> result = producer.list_subscribers()
            >>> for subscriber in result['subscribers']:
            ...     print(f"Consumer: {subscriber['consumer_id']}")
            ...     print(f"Subscriptions: {subscriber['subscription_count']}")
        """
        return self._make_api_request("GET", "/v1/producers/subscribers")
