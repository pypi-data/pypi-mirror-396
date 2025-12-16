# Helix Admin SDK
# For Helix internal use to manage customers and platform

from typing import Dict, List, Optional

import requests

from .consumer import API_TIMEOUT, HelixConsumer
from .exceptions import *


class HelixAdmin(HelixConsumer):
    """
    SDK for Helix administrators to manage the platform.
    Inherits consumer capabilities plus admin operations.

    Args:
        aws_access_key_id: Admin AWS access key ID
        aws_secret_access_key: Admin AWS secret access key
        customer_id: Admin customer ID
        api_endpoint: API Gateway endpoint (default: production endpoint)
        region: AWS region (default: us-east-1)
    """

    def create_customer(
        self,
        company_name: str,
        business_email: str,
        customer_type: str = "consumer",
        phone: Optional[str] = None,
        address: Optional[Dict] = None,
    ) -> Dict:
        """
        Create a new customer account.

        Args:
            company_name: Company name
            business_email: Business contact email
            customer_type: 'consumer' or 'producer'
            phone: Optional phone number
            address: Optional address dict with keys: street, city, state, zip, country

        Returns:
            Customer object with customer_id, status, and credential_delivery_url
        """
        payload = {
            "company_name": company_name,
            "business_email": business_email,
            "customer_type": customer_type,
        }

        if phone:
            payload["phone"] = phone
        if address:
            payload["address"] = address

        return self._make_api_request("POST", "/v1/customers/onboard", json=payload)

    def list_all_customers(self) -> List[Dict]:
        """
        List all customers in the system.

        Returns:
            List of customer objects
        """
        response = self._make_api_request("GET", "/v1/customers")
        return response.get("customers", [])

    def get_customer(self, customer_id: str) -> Dict:
        """
        Get details about a specific customer.

        Args:
            customer_id: Customer ID

        Returns:
            Customer object
        """
        return self._make_api_request("GET", f"/v1/customers/{customer_id}")

    def update_customer(
        self,
        customer_id: str,
        company_name: Optional[str] = None,
        company_url: Optional[str] = None,
        email: Optional[str] = None,
        customer_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict:
        """
        Update a customer's information.

        Args:
            customer_id: Customer ID
            company_name: Optional company name update
            company_url: Optional company URL update
            email: Optional email update
            customer_type: Optional customer type update ('consumer', 'producer', or 'both')
            status: Optional status update ('active', 'suspended', etc.)

        Returns:
            Updated customer object
        """
        payload = {}
        if company_name is not None:
            payload["company_name"] = company_name
        if company_url is not None:
            payload["company_url"] = company_url
        if email is not None:
            payload["email"] = email
        if customer_type is not None:
            payload["customer_type"] = customer_type
        if status is not None:
            payload["status"] = status

        return self._make_api_request(
            "PATCH", f"/v1/customers/{customer_id}", json=payload
        )

    def upgrade_customer(self, customer_id: str, new_type: str) -> Dict:
        """
        Upgrade a customer (e.g., consumer -> producer).

        Args:
            customer_id: Customer ID
            new_type: New customer type ('producer' or 'both')

        Returns:
            Updated customer object
        """
        return self.update_customer(customer_id, customer_type=new_type)

    def list_all_datasets(self) -> List[Dict]:
        """
        List all datasets in the system (admin view).

        Returns:
            List of all dataset objects
        """
        return self.list_datasets()  # No producer_id filter = all datasets

    def get_customer_credentials(self, customer_id: str) -> Dict:
        """
        Retrieve AWS credentials for a customer from SSM Parameter Store.
        Admin-only operation to retrieve credentials after customer creation.

        Args:
            customer_id: Customer ID (format: customer-{uuid} or company-{timestamp}-{name})

        Returns:
            Dictionary with keys:
                - aws_access_key_id: AWS access key ID
                - aws_secret_access_key: AWS secret access key
                - customer_id: Customer ID
                - metadata: Customer metadata (JSON parsed)

        Raises:
            HelixError: If SSM parameters cannot be retrieved
        """
        try:
            # Retrieve AWS credentials from SSM Parameter Store
            access_key_param = f"/helix/customers/{customer_id}/aws_access_key_id"
            secret_key_param = f"/helix/customers/{customer_id}/aws_secret_access_key"
            metadata_param = f"/helix/customers/{customer_id}/metadata"

            # Get access key
            access_key_response = self.ssm.get_parameter(
                Name=access_key_param, WithDecryption=True
            )
            aws_access_key_id = access_key_response["Parameter"]["Value"]

            # Get secret key
            secret_key_response = self.ssm.get_parameter(
                Name=secret_key_param, WithDecryption=True
            )
            aws_secret_access_key = secret_key_response["Parameter"]["Value"]

            # Get metadata (optional, may not exist for all customers)
            metadata = None
            try:
                metadata_response = self.ssm.get_parameter(
                    Name=metadata_param, WithDecryption=True
                )
                import json

                metadata = json.loads(metadata_response["Parameter"]["Value"])
            except self.ssm.exceptions.ParameterNotFound:
                # Metadata parameter doesn't exist, that's okay
                pass
            except Exception as e:
                # Log warning but don't fail the whole operation
                print(f"Warning: Could not parse metadata: {e}")

            return {
                "customer_id": customer_id,
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
                "metadata": metadata,
            }

        except self.ssm.exceptions.ParameterNotFound as e:
            raise HelixError(
                f"Credentials not found for customer {customer_id}. "
                f"Customer may not be fully provisioned yet. Error: {e}"
            )
        except Exception as e:
            raise HelixError(
                f"Failed to retrieve credentials for customer {customer_id}: {e}"
            )

    # Credential Management Methods (Admin Operations)

    def create_credential(self, customer_id: Optional[str] = None) -> Dict:
        """
        Create initial IAM credentials for a customer (admin-only operation).
        This endpoint is protected and requires admin role in JWT token.

        IMPORTANT: This returns a portal URL to view the new credentials.
        The actual credentials are NOT returned in the API response for security.
        Use this when a customer needs their first set of credentials created by an admin.

        Args:
            customer_id: Optional customer ID. If not provided, creates credentials for admin's account.

        Returns:
            Dict containing:
                - success: True if successful
                - message: Success message
                - credential_portal_url: Secure one-time portal link to view credentials
                - portal_expires_at: When the portal link expires (24 hours)
                - credential: New credential info (without secret key)

        Raises:
            HelixError: If customer already has credentials or if not admin

        Example:
            >>> admin = HelixAdmin(...)
            >>> # Create initial credentials for a new customer
            >>> response = admin.create_credential(customer_id="customer-123")
            >>> print(f"Portal URL: {response['credential_portal_url']}")
            >>> # Send this portal URL to the customer to retrieve their credentials
        """
        if customer_id:
            # Admin creating credentials for another customer
            return self._make_api_request(
                "POST", f"/v1/customers/{customer_id}/credentials"
            )
        else:
            # Admin creating their own credentials
            return self._make_api_request("POST", "/v1/credentials")

    def list_credentials(self, customer_id: Optional[str] = None) -> Dict:
        """
        List credentials for a specific customer or all customers (admin only).

        Args:
            customer_id: Optional customer ID to filter credentials.
                        If not provided, returns credentials for the admin's own account.

        Returns:
            Dict with 'credentials' list and 'count'. Each credential contains:
                - id: Credential ID
                - customer_id: Customer ID
                - access_key_id: AWS Access Key ID
                - status: active, rotating, inactive, or deleted
                - created_at: Creation timestamp
                - rotation_count: Number of times rotated
                - expires_at: Expiration timestamp (if rotating)
                - days_until_expiry: Days until expiration (if applicable)

        Example:
            >>> admin = HelixAdmin(...)
            >>> # List all credentials for a specific customer
            >>> creds = admin.list_credentials(customer_id="customer-123")
            >>> print(f"Found {creds['count']} credentials")
        """
        if customer_id:
            # Admin viewing another customer's credentials
            return self._make_api_request(
                "GET", f"/v1/customers/{customer_id}/credentials"
            )
        else:
            # Admin viewing their own credentials
            return self._make_api_request("GET", "/v1/credentials")

    def regenerate_credential(
        self,
        customer_id: Optional[str] = None,
        reason: Optional[str] = None,
        old_key_expiration_days: int = 7,
    ) -> Dict:
        """
        Rotate credentials for a customer (admin operation).
        Old key remains active during transition period (7-30 days).

        IMPORTANT: This returns a portal URL to view the new credentials.
        The actual credentials are NOT returned in the API response for security.

        Args:
            customer_id: Optional customer ID. If not provided, rotates admin's own credentials.
            reason: Optional reason for rotation (e.g., "Security audit", "Compromised key")
            old_key_expiration_days: Days until old key expires (default: 7, max: 30)

        Returns:
            Dict containing:
                - success: True if successful
                - message: Success message
                - credential_portal_url: Secure one-time portal link to view new credentials
                - portal_expires_at: When the portal link expires (24 hours)
                - new_credential: New credential info (without secret)
                - old_credential: Old credential info
                - expires_old_key_at: When old key will be disabled

        Example:
            >>> admin = HelixAdmin(...)
            >>> # Rotate credentials for a specific customer
            >>> response = admin.regenerate_credential(
            ...     customer_id="customer-123",
            ...     reason="Security incident - key potentially compromised",
            ...     old_key_expiration_days=7
            ... )
            >>> print(f"Portal URL: {response['credential_portal_url']}")
            >>> print(f"Old key expires: {response['expires_old_key_at']}")
        """
        payload = {}
        if reason:
            payload["reason"] = reason
        if old_key_expiration_days:
            payload["old_key_expiration_days"] = old_key_expiration_days

        if customer_id:
            # Admin rotating another customer's credentials
            return self._make_api_request(
                "POST",
                f"/v1/customers/{customer_id}/credentials/regenerate",
                json=payload,
            )
        else:
            # Admin rotating their own credentials
            return self._make_api_request(
                "POST", "/v1/credentials/regenerate", json=payload
            )

    def delete_credential(
        self, access_key_id: str, customer_id: Optional[str] = None
    ) -> Dict:
        """
        Delete a specific credential (admin operation).

        Note: Cannot delete the last active credential for a customer.

        Args:
            access_key_id: The AWS Access Key ID to delete (e.g., "AKIAIOSFODNN7EXAMPLE")
            customer_id: Optional customer ID. If not provided, deletes from admin's account.

        Returns:
            Dict with success status and message

        Raises:
            HelixError: If credential not found or cannot be deleted

        Example:
            >>> admin = HelixAdmin(...)
            >>> # Delete a credential for a specific customer
            >>> result = admin.delete_credential(
            ...     access_key_id="AKIAIOSFODNN7OLDKEY",
            ...     customer_id="customer-123"
            ... )
            >>> print(result['message'])
        """
        if customer_id:
            # Admin deleting another customer's credential
            return self._make_api_request(
                "DELETE", f"/v1/customers/{customer_id}/credentials/{access_key_id}"
            )
        else:
            # Admin deleting their own credential
            return self._make_api_request("DELETE", f"/v1/credentials/{access_key_id}")

    @staticmethod
    def forgot_credentials(
        email: str,
        api_endpoint: str = "https://z94fkomfij.execute-api.us-east-1.amazonaws.com",
    ) -> Dict:
        """
        Request credentials recovery for a customer with forgotten credentials.
        This is a public endpoint that doesn't require authentication.

        SECURITY NOTE: This endpoint always returns success to prevent email enumeration.
        If the email exists in the system, a secure portal link will be sent to that email.

        Args:
            email: Business email address associated with the customer account
            api_endpoint: API endpoint (default: production)

        Returns:
            Dict with success message (always returns success for security)

        Example:
            >>> # Customer or admin can call this to recover credentials
            >>> HelixAdmin.forgot_credentials("customer@example.com")
            {
                'success': True,
                'message': 'If the email address is associated with an account, you will receive instructions to retrieve your credentials.'
            }
        """
        url = f"{api_endpoint.rstrip('/')}/v1/credentials/forgot"
        response = requests.post(
            url,
            json={"email": email},
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
