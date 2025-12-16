# Helix Consumer SDK
# For data consumers who want to download and access datasets

import gzip
import io
import struct
from typing import Callable, Dict, List, Optional
from urllib.parse import quote

import boto3
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .exceptions import (
    AuthenticationError,
    DatasetNotFoundError,
    HelixError,
    PermissionDeniedError,
    RateLimitError,
)

# Timeout constants
API_TIMEOUT = (10, 30)  # (connect timeout, read timeout) for API calls
DOWNLOAD_TIMEOUT = (10, None)  # (connect timeout, unlimited read) for downloads


class HelixConsumer:
    """
    SDK for data consumers to access and download datasets from Helix Connect.

    Args:
        aws_access_key_id: AWS access key ID from customer onboarding
        aws_secret_access_key: AWS secret access key from customer onboarding
        customer_id: Unique customer ID (UUID)
        api_endpoint: API Gateway endpoint (default: production endpoint)
        region: AWS region (default: us-east-1)
    """

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        customer_id: str,
        api_endpoint: str = "https://z94fkomfij.execute-api.us-east-1.amazonaws.com",
        region: str = "us-east-1",
    ):
        self.customer_id = customer_id
        self.api_endpoint = api_endpoint.rstrip("/")
        self.region = region

        # Initialize AWS clients
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region,
        )

        self.s3 = self.session.client("s3")
        self.sqs = self.session.client("sqs")
        self.ssm = self.session.client("ssm")
        self.kms = self.session.client("kms")  # For decryption

        # Initialize API client with AWS SigV4 authentication
        from botocore.auth import SigV4Auth

        self.sigv4 = SigV4Auth(self.session.get_credentials(), "execute-api", region)

        # Cache for per-consumer queue URL
        self.queue_url: Optional[str] = None

        # Validate AWS credentials immediately (fail fast)
        self._validate_credentials()

    def _validate_credentials(self) -> None:
        """
        Validate AWS credentials by making a test call to STS.
        Raises AuthenticationError if credentials are invalid.
        """
        try:
            sts = self.session.client("sts")
            sts.get_caller_identity()
            # Credentials are valid
        except Exception as e:
            raise AuthenticationError(
                f"Invalid AWS credentials. Please check your access key and secret key. "
                f"Error: {str(e)}"
            )

    def _decompress_data(self, data: bytes) -> bytes:
        """
        Decompress gzipped data.

        Args:
            data: Compressed data bytes

        Returns:
            Decompressed data bytes
        """
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
                return gz.read()
        except Exception as e:
            raise HelixError(f"Decompression failed: {e}")

    def _decompress_data_stream(self, data: bytes, output_path: str) -> None:
        """
        Decompress gzipped data using streaming to avoid memory limits.
        Used for large files that would exceed Python's memory limits.

        Args:
            data: Compressed data bytes
            output_path: Path to write decompressed data
        """
        try:
            # Decompress in chunks to avoid loading entire file in memory
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
                with open(output_path, "wb") as f:
                    # Read and write in 10MB chunks
                    chunk_size = 10 * 1024 * 1024
                    while True:
                        chunk = gz.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)

            # Get final file size
            import os

            file_size = os.path.getsize(output_path)
            size_gb = file_size / (1024**3)
            if size_gb > 1:
                print(f"Decompressed to {size_gb:.2f} GB")
            else:
                print(f"Decompressed to {file_size} bytes")
        except Exception as e:
            raise HelixError(f"Stream decompression failed: {e}")

    def _decrypt_data(self, data: bytes) -> bytes:
        """
        Decrypt data using envelope encryption (reverse of producer's _encrypt_data).
        Consumer must have KMS grant to decrypt producer's data key.

        Format: [4 bytes: key length][encrypted key][16 bytes: IV][16 bytes: tag][encrypted data]

        Args:
            data: Encrypted data bytes in envelope encryption format

        Returns:
            Decrypted data bytes
        """
        try:
            # Unpack the envelope encryption format
            offset = 0

            # Read encrypted key length (4 bytes)
            key_length = struct.unpack(">I", data[offset : offset + 4])[0]
            offset += 4

            # Read encrypted data key
            encrypted_key = data[offset : offset + key_length]
            offset += key_length

            # Read IV (16 bytes)
            iv = data[offset : offset + 16]
            offset += 16

            # Read authentication tag (16 bytes)
            auth_tag = data[offset : offset + 16]
            offset += 16

            # Remaining bytes are the encrypted data
            encrypted_data = data[offset:]

            # Decrypt the data key using KMS
            response = self.kms.decrypt(CiphertextBlob=encrypted_key)
            data_key = response["Plaintext"]

            # Decrypt the data using the data key with AES-256-GCM
            cipher = Cipher(
                algorithms.AES(data_key),
                modes.GCM(iv, auth_tag),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(encrypted_data) + decryptor.finalize()

            return plaintext
        except Exception as e:
            raise HelixError(
                f"Decryption failed: {e}. Ensure you have KMS grant for this dataset."
            )

    def _make_api_request(self, method: str, path: str, **kwargs) -> Dict:
        """Make an authenticated API request using AWS SigV4"""
        url = f"{self.api_endpoint}{path}"

        # Convert json parameter to data for AWS signing
        request_kwargs = kwargs.copy()
        if "json" in request_kwargs:
            import json as json_module

            request_kwargs["data"] = json_module.dumps(request_kwargs.pop("json"))
            if "headers" not in request_kwargs:
                request_kwargs["headers"] = {}
            request_kwargs["headers"]["Content-Type"] = "application/json"

        # Create AWS request for signing
        from botocore.awsrequest import AWSRequest

        request = AWSRequest(method=method, url=url, **request_kwargs)
        self.sigv4.add_auth(request)

        # Make the actual request with timeout
        response = requests.request(
            method=method,
            url=url,
            headers=dict(request.headers),
            timeout=API_TIMEOUT,
            **kwargs,
        )

        if response.status_code >= 400:
            if response.status_code == 401:
                raise AuthenticationError(f"Authentication failed: {response.text}")
            elif response.status_code == 403:
                raise PermissionDeniedError(f"Permission denied: {response.text}")
            elif response.status_code == 404:
                raise DatasetNotFoundError(f"Dataset not found: {response.text}")
            elif response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {response.text}")
            else:
                raise HelixError(
                    f"API request failed: {response.status_code} - {response.text}"
                )

        return response.json()

    def list_datasets(self, producer_id: Optional[str] = None) -> List[Dict]:
        """
        List all available datasets (that the customer has access to).

        Args:
            producer_id: Optional filter by producer ID

        Returns:
            List of dataset objects
        """
        params = {}
        if producer_id:
            params["producer_id"] = producer_id

        response = self._make_api_request("GET", "/v1/datasets", params=params)
        return response.get("datasets", [])

    def get_dataset(self, dataset_id: str) -> Dict:
        """
        Get details about a specific dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dataset object with metadata
        """
        # URL-encode the dataset ID to handle spaces and special characters
        dataset_id_encoded = quote(dataset_id, safe="")
        return self._make_api_request("GET", f"/v1/datasets/{dataset_id_encoded}")

    def get_download_url(self, dataset_id: str) -> Dict:
        """
        Get a signed download URL for a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dict with 'download_url' and 'expires_at' keys
        """
        # URL-encode the dataset ID to handle spaces and special characters
        dataset_id_encoded = quote(dataset_id, safe="")
        return self._make_api_request(
            "GET", f"/v1/datasets/{dataset_id_encoded}/download"
        )

    def download_dataset(
        self,
        dataset_id: str,
        output_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        auto_decompress: bool = True,
        auto_decrypt: bool = True,
    ) -> str:
        """
        Download a dataset with automatic decompression and decryption.

        Optimized for large files (>1GB) using streaming when possible.

        Args:
            dataset_id: Dataset ID
            output_path: Local file path to save the dataset
            progress_callback: Optional callback function(bytes_downloaded, total_bytes)
            auto_decompress: Automatically decompress .gz files (default: True)
            auto_decrypt: Automatically decrypt encrypted files (default: True)

        Returns:
            Path to the downloaded file
        """
        # Get dataset metadata first
        dataset = self.get_dataset(dataset_id)

        # Check if file is compressed/encrypted
        metadata = dataset.get("metadata", {})
        is_compressed = metadata.get("compression_enabled", False)
        is_encrypted = metadata.get("encryption_enabled", False)

        print(f"Downloading dataset {dataset_id}...")
        print(f"   Compressed: {is_compressed}")
        print(f"   Encrypted: {is_encrypted}")

        # Get signed URL
        url_info = self.get_download_url(dataset_id)
        download_url = url_info["download_url"]

        # Download file with unlimited read timeout
        response = requests.get(download_url, stream=True, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        bytes_downloaded = 0

        # For large files (>100MB) or when no processing is needed, stream directly to disk
        large_file_threshold = 100 * 1024 * 1024  # 100MB

        # Stream directly for unencrypted/uncompressed large files
        if not (is_encrypted or is_compressed) and total_size > large_file_threshold:
            size_gb = total_size / (1024**3)
            print(f"Streaming large file directly to disk ({size_gb:.2f} GB)...")
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):  # 1MB chunks
                    if chunk:
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(bytes_downloaded, total_size)
            print(f"Downloaded {bytes_downloaded} bytes")
            print(f"Saved to {output_path}")
            return output_path

        # Download to memory for processing (encrypted/compressed files)
        data = io.BytesIO()
        chunk_size = (
            1024 * 1024 if total_size > large_file_threshold else 8192
        )  # Use larger chunks for large files

        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                data.write(chunk)
                bytes_downloaded += len(chunk)

                if progress_callback:
                    progress_callback(bytes_downloaded, total_size)

        size_gb = bytes_downloaded / (1024**3)
        if size_gb > 1:
            print(f"Downloaded {bytes_downloaded} bytes ({size_gb:.2f} GB)")
        else:
            print(f"Downloaded {bytes_downloaded} bytes")

        # Get data
        data = data.getvalue()

        # Step 1: Decrypt FIRST (if needed and enabled)
        # Must decrypt before decompressing (reverse of upload order)
        if is_encrypted and auto_decrypt:
            print(f"Decrypting {len(data)} bytes with KMS...")
            data = self._decrypt_data(data)
            print(f"Decrypted to {len(data)} bytes")

        # Step 2: Decompress SECOND (if needed and enabled) - use streaming for large files
        if is_compressed and auto_decompress:
            # Estimate decompressed size (typically 10-20x for text data)
            estimated_decompressed = len(data) * 20

            # Use streaming decompression for large files to avoid memory issues
            if (
                len(data) > large_file_threshold
                and estimated_decompressed > 2 * 1024**3
            ):  # >2GB estimated
                estimated_gb = estimated_decompressed / (1024**3)
                print(
                    f"Large file detected (estimated {estimated_gb:.2f} GB decompressed) - using streaming decompression"
                )
                self._decompress_data_stream(data, output_path)
                print(f"Streamed to {output_path}")
                return output_path
            else:
                # Small files - use in-memory decompression
                print(f"Decompressing {len(data)} bytes...")
                data = self._decompress_data(data)
                decompressed_size_gb = len(data) / (1024**3)
                if decompressed_size_gb > 1:
                    print(f"Decompressed to {decompressed_size_gb:.2f} GB")
                else:
                    print(f"Decompressed to {len(data)} bytes")

        # Write final data to file
        with open(output_path, "wb") as f:
            f.write(data)

        print(f"Saved to {output_path}")
        return output_path

    def list_subscriptions(self) -> List[Dict]:
        """
        List all active subscriptions for this customer.

        Returns:
            List of subscription objects
        """
        response = self._make_api_request("GET", "/v1/subscriptions")
        return response.get("subscriptions", [])

    def subscribe_to_dataset(self, dataset_id: str, tier: str = "basic") -> Dict:
        """
        Subscribe to a dataset to receive updates.

        Args:
            dataset_id: Dataset ID to subscribe to
            tier: Subscription tier (basic, standard, premium)

        Returns:
            Subscription object
        """
        payload = {"dataset_id": dataset_id, "tier": tier}
        return self._make_api_request("POST", "/v1/subscriptions", json=payload)

    def create_subscription_request(
        self,
        producer_id: str,
        dataset_id: Optional[str] = None,
        tier: str = "basic",
        message: Optional[str] = None,
    ) -> Dict:
        """
        Request subscription to a producer's dataset(s).

        Args:
            producer_id: The producer's customer ID
            dataset_id: Specific dataset ID (optional - if None, requests access to all datasets)
            tier: Subscription tier (basic, premium, enterprise)
            message: Optional message to the producer explaining the request

        Returns:
            Dict containing subscription request details including request_id

        Example:
            >>> consumer = HelixConsumer(...)
            >>> request = consumer.create_subscription_request(
            ...     producer_id="company-1234567890123-example",
            ...     tier="premium",
            ...     message="We need phone data for our marketing campaign"
            ... )
            >>> print(f"Request ID: {request['request_id']}")
            >>> print(f"Status: {request['status']}")  # 'pending'
        """
        payload = {
            "producer_id": producer_id,
            "tier": tier,
        }

        if dataset_id:
            payload["dataset_id"] = dataset_id

        if message:
            payload["message"] = message

        return self._make_api_request("POST", "/v1/subscription-requests", data=payload)

    def list_subscription_requests(self, status: Optional[str] = None) -> Dict:
        """
        List all subscription requests created by this consumer.

        Args:
            status: Filter by status ('pending', 'approved', 'rejected') - optional

        Returns:
            Dict with 'requests' list and 'count'

        Example:
            >>> consumer = HelixConsumer(...)
            >>> result = consumer.list_subscription_requests(status='pending')
            >>> for req in result['requests']:
            ...     print(f"{req['producer_id']}: {req['status']}")
        """
        endpoint = "/v1/subscription-requests"
        if status:
            endpoint += f"?status={status}"

        return self._make_api_request("GET", endpoint)

    def get_subscription_request(self, request_id: str) -> Dict:
        """
        Get details of a specific subscription request.

        Args:
            request_id: The subscription request ID

        Returns:
            Dict containing subscription request details

        Example:
            >>> consumer = HelixConsumer(...)
            >>> request = consumer.get_subscription_request("req-123-456")
            >>> print(f"Status: {request['status']}")
            >>> print(f"Producer: {request['producer_id']}")
        """
        return self._make_api_request("GET", f"/v1/subscription-requests/{request_id}")

    def poll_notifications(
        self,
        max_messages: int = 10,
        wait_time_seconds: int = 20,
        visibility_timeout: int = 300,
        auto_acknowledge: bool = True,
        subscription_ids: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Poll per-consumer SQS queue for dataset upload notifications.

        IMPORTANT: This uses a DEDICATED queue for this consumer. SNS filter policies
        ensure only relevant notifications reach this queue. You can optionally filter
        by subscription IDs for advanced use cases.

        Messages are automatically acknowledged (deleted) by default after retrieval.
        This prevents duplicate processing and simplifies the developer experience.
        Set auto_acknowledge to False if you need manual control over message deletion.

        This method retrieves messages from your dedicated notification queue.
        Each message contains information about a newly uploaded dataset from subscribed producers.

        Args:
            max_messages: Maximum number of messages to retrieve (1-10, default: 10)
            wait_time_seconds: Long polling wait time (0-20 seconds, default: 20)
            visibility_timeout: How long messages are hidden after retrieval (default: 300s)
            auto_acknowledge: Automatically acknowledge (delete) messages after receiving (default: True)
                            Set to False for manual acknowledgment with custom retry logic.
            subscription_ids: Optional list of subscription IDs to filter notifications (default: None = all)

        Returns:
            List of notification dictionaries, each containing:
            - message_id: SQS message ID
            - receipt_handle: Handle for deleting the message
            - event_type: Type of event (e.g., 'dataset_updated')
            - producer_id: ID of the producer who uploaded it
            - dataset_id: ID of the uploaded dataset
            - dataset_name: Human-readable dataset name (optional)
            - s3_bucket: S3 bucket name
            - s3_key: S3 object key
            - size_bytes: Size of the dataset file
            - timestamp: Upload timestamp
            - subscriber_id: ID of the subscriber
            - subscription_id: ID of the subscription
            - raw_message: Raw SQS message body for debugging

        Raises:
            HelixError: If queue URL is not configured or polling fails

        Example:
            >>> consumer = HelixConsumer(...)
            >>>
            >>> # Simple usage - messages auto-deleted after poll
            >>> notifications = consumer.poll_notifications(
            ...     subscription_ids=['sub-123'],
            ...     max_messages=5
            ... )
            >>> for notif in notifications:
            ...     print(f"New dataset: {notif['dataset_name']}")
            ...     consumer.download_dataset(notif['dataset_id'], './output.json')
            ...     # No need to delete - already handled automatically!
            >>>
            >>> # Advanced usage - manual acknowledgment for custom retry logic
            >>> notifications = consumer.poll_notifications(
            ...     auto_acknowledge=False,
            ...     max_messages=5
            ... )
            >>> for notif in notifications:
            ...     try:
            ...         consumer.download_dataset(notif['dataset_id'], './output.json')
            ...         # Manually acknowledge only after successful processing
            ...         consumer.delete_notification(notif['receipt_handle'])
            ...     except Exception as e:
            ...         print(f'Processing failed, message will retry: {e}')
            ...         # Message not deleted, will become visible again after visibility timeout
        """
        # Get per-consumer queue URL from first active subscription
        if not self.queue_url:
            try:
                subscriptions = self.list_subscriptions()

                if not subscriptions:
                    raise HelixError(
                        "No active subscriptions found. Create a subscription first using create_subscription_request()"
                    )

                # Get queue URL from first subscription (all subscriptions for same consumer share same queue)
                subscription = next(
                    (sub for sub in subscriptions if sub.get("sqs_queue_url")), None
                )

                if not subscription or not subscription.get("sqs_queue_url"):
                    raise HelixError(
                        "Per-consumer queue not provisioned. This may be a legacy subscription. "
                        "Please contact support or create a new subscription to get a dedicated queue."
                    )

                self.queue_url = subscription["sqs_queue_url"]
            except HelixError:
                raise
            except Exception as e:
                raise HelixError(f"Failed to get per-consumer queue URL: {e}")

        # Poll SQS for messages from per-consumer queue
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=min(max_messages, 10),  # AWS limit is 10
                WaitTimeSeconds=min(wait_time_seconds, 20),  # AWS limit is 20
                VisibilityTimeout=visibility_timeout,
                MessageAttributeNames=["All"],
            )
        except Exception as e:
            raise HelixError(f"Failed to poll SQS queue: {e}")

        messages = response.get("Messages", [])
        notifications = []

        for message in messages:
            try:
                import json

                # Parse SNS message to get the custom notification payload
                sns_message = json.loads(message["Body"])
                notification_data = json.loads(sns_message["Message"])

                # SNS filter policy ensures only messages for this consumer reach this queue
                # No need for subscriber_id filtering - it's already guaranteed by SNS

                # Optional filter by subscription IDs if provided (advanced use case)
                if subscription_ids is not None and len(subscription_ids) > 0:
                    if notification_data.get("subscription_id") not in subscription_ids:
                        continue  # Skip this notification - doesn't match our subscriptions

                notification = {
                    "message_id": message["MessageId"],
                    "receipt_handle": message["ReceiptHandle"],
                    "event_type": notification_data.get("event_type"),
                    "producer_id": notification_data.get("producer_id"),
                    "dataset_id": notification_data.get("dataset_id"),
                    "dataset_name": notification_data.get("dataset_name"),
                    "s3_bucket": notification_data.get("s3_bucket"),
                    "s3_key": notification_data.get("s3_key"),
                    "size_bytes": notification_data.get("size_bytes"),
                    "timestamp": notification_data.get("timestamp"),
                    "subscriber_id": notification_data.get("subscriber_id"),
                    "subscription_id": notification_data.get("subscription_id"),
                    "raw_message": message["Body"],
                }

                notifications.append(notification)

                # Auto-acknowledge (delete) message by default
                if auto_acknowledge:
                    self.delete_notification(message["ReceiptHandle"])

            except Exception as e:
                print(
                    f"Warning: Failed to parse notification message {message.get('MessageId')}: {e}"
                )
                continue

        return notifications

    def delete_notification(self, receipt_handle: str) -> None:
        """
        Delete a notification message from the SQS queue after processing.

        Args:
            receipt_handle: The receipt handle from poll_notifications()

        Raises:
            HelixError: If deletion fails

        Example:
            >>> consumer = HelixConsumer(...)
            >>> notifications = consumer.poll_notifications()
            >>> for notif in notifications:
            ...     # Process notification...
            ...     consumer.delete_notification(notif['receipt_handle'])
        """
        if not self.queue_url:
            raise HelixError(
                "Queue URL not available. Call poll_notifications() first to initialize the queue URL."
            )

        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url, ReceiptHandle=receipt_handle
            )
        except Exception as e:
            raise HelixError(f"Failed to delete notification: {e}")

    def _extract_producer_id(self, s3_key: str) -> str:
        """
        Extract producer ID from S3 key path.

        S3 keys follow the pattern: datasets/{dataset_name}/{date}/{file}
        Dataset name typically contains the producer company ID.

        Args:
            s3_key: S3 object key

        Returns:
            Extracted producer ID (or 'unknown' if not found)
        """
        try:
            # Example key: datasets/company-123-producer-Dataset Name/2025-11-01/file.json.gz
            parts = s3_key.split("/")
            if len(parts) >= 2:
                dataset_name = parts[1]
                # Extract company ID from dataset name
                if "company-" in dataset_name:
                    company_id = dataset_name.split("-")[1]
                    return f"company-{company_id}"
            return "unknown"
        except Exception:
            return "unknown"
