"""AWS-specific account configurations."""

from dataclasses import dataclass, field

from ..config import register_account_config
from ._base import DomoAccount_Config

__all__ = [
    "DomoAccount_Config_AmazonS3",
    "DomoAccount_Config_AmazonS3Advanced",
    "DomoAccount_Config_AwsAthena",
    "DomoAccount_Config_HighBandwidthConnector",
    "DomoAccount_Config_DomoToS3",
]


@register_account_config("domo-to-s3")
@dataclass
class DomoAccount_Config_DomoToS3(DomoAccount_Config):
    """Domo to S3 export connector configuration."""

    data_provider_type: str = "domo-to-s3"
    is_oauth: bool = False

    client_id: str = None
    client_secret: str = field(repr=False, default=None)
    # access_key: str = None
    # secret_key: str = field(repr=False, default=None)
    bucket: str = None
    region: str = "us-west-2"

    _field_map: list[dict[str:str]] = field(
        default_factory=lambda: {
            "client_id": "access_key",
            "client_secret": "secret_Key",
        }
    )

    def __post_init__(self):
        if self.bucket:
            self.bucket = self._clean_bucket()
        super().__post_init__()

    def _clean_bucket(self):
        bucket = self.bucket

        if bucket and bucket.lower().startswith("s3://"):
            bucket = bucket[5:]

        return bucket


@register_account_config("amazon-s3")
@dataclass
class DomoAccount_Config_AmazonS3(DomoAccount_Config):
    data_provider_type: str = "amazon-s3"
    is_oauth: bool = False

    access_key: str = None
    secret_key: str = field(repr=False, default=None)
    bucket: str = None
    region: str = "us-west-2"

    def __post_init__(self):
        self.bucket = self._clean_bucket()
        super().__post_init__()

    def _clean_bucket(self):
        bucket = self.bucket

        if bucket and bucket.lower().startswith("s3://"):
            bucket = bucket[5:]

        return bucket


@register_account_config("amazons3-advanced")
@dataclass
class DomoAccount_Config_AmazonS3Advanced(DomoAccount_Config):
    data_provider_type: str = "amazons3-advanced"
    is_oauth: bool = False

    access_key: str = None
    secret_key: str = field(repr=False, default=None)

    bucket: str = None
    region: str = "us-west-2"

    def _clean_bucket(self):
        bucket = self.bucket

        if bucket and bucket.lower().startswith("s3://"):
            bucket = bucket[5:]

        return bucket


@register_account_config("aws-athena")
@dataclass
class DomoAccount_Config_AwsAthena(DomoAccount_Config):
    data_provider_type: str = "aws-athena"
    is_oauth: bool = False

    access_key: str = None
    secret_key: str = field(repr=False, default=None)
    bucket: str = None
    workgroup: str = None

    region: str = "us-west-2"

    _field_map: dict = field(
        default_factory=lambda: {
            "awsAccessKey": "access_key",
            "awsSecretKey": "secret_key",
            "s3StagingDir": "bucket",
        },
        repr=False,
        init=False,
    )

    _fields_for_serialization: list[str] = field(
        default_factory=lambda: [
            "access_key",
            "secret_key",
            "bucket",
            "region",
            "workgroup",
        ]
    )


@register_account_config("amazon-athena-high-bandwidth")
@dataclass
class DomoAccount_Config_HighBandwidthConnector(DomoAccount_Config):
    """this connector is not enabled by default contact your CSM / AE"""

    data_provider_type: str = "amazon-athena-high-bandwidth"
    is_oauth: bool = False

    access_key: str = None
    secret_key: str = field(repr=False, default=None)
    bucket: str = None

    region: str = "us-west-2"
    workgroup: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "awsAccessKey": "access_key",
            "awsSecretKey": "secret_key",
            "s3StagingDir": "bucket",
        },
        repr=False,
        init=False,
    )
