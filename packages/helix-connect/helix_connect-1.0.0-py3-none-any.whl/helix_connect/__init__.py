# Helix Connect Python SDK
# Stream 3: SDKs & Developer Experience - Python SDK (Weeks 1-3)

"""
Helix Connect - Data Marketplace SDK

A Python SDK for interacting with the Helix Connect data marketplace.
Supports both data producers (uploading datasets) and data consumers (downloading datasets).

Example usage:

    # For Consumers
    from helix_connect import HelixConsumer

    consumer = HelixConsumer(
        aws_access_key_id="AKIA...",
        aws_secret_access_key="...",
        customer_id="uuid-here"
    )

    # List available datasets
    datasets = consumer.list_datasets()

    # Download a dataset
    consumer.download_dataset(dataset_id="dataset-123", output_path="./data.zip")

    # Poll for notifications
    consumer.poll_notifications(auto_download=True)


    # For Producers
    from helix_connect import HelixProducer

    producer = HelixProducer(
        aws_access_key_id="AKIA...",
        aws_secret_access_key="...",
        customer_id="uuid-here"
    )

    # Upload a dataset
    producer.upload_dataset(
        file_path="./dataset.zip",
        dataset_name="phone-numbers",
        description="Daily phone number dataset"
    )
"""

__version__ = "1.0.0"
__author__ = "Helix Tools"
__license__ = "MIT"

from .admin import HelixAdmin
from .consumer import HelixConsumer
from .exceptions import (
    AuthenticationError,
    DatasetNotFoundError,
    HelixError,
    PermissionDeniedError,
    RateLimitError,
)
from .producer import HelixProducer

__all__ = [
    "HelixConsumer",
    "HelixProducer",
    "HelixAdmin",
    "HelixError",
    "AuthenticationError",
    "PermissionDeniedError",
    "DatasetNotFoundError",
    "RateLimitError",
]
