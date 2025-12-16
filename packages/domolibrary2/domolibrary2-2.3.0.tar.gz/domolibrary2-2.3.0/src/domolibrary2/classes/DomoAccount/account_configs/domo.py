"""Domo-specific account configurations."""

from dataclasses import dataclass, field

from ..config import register_account_config
from ._base import DomoAccount_Config

__all__ = [
    "DomoAccount_Config_AbstractCredential",
    "DomoAccount_Config_DatasetCopy",
    "DomoAccount_Config_DomoAccessToken",
    "DomoAccount_Config_Governance",
]


@register_account_config("abstract-credential-store")
@dataclass
class DomoAccount_Config_AbstractCredential(DomoAccount_Config):
    credentials: dict = None
    data_provider_type: str = "abstract-credential-store"
    is_oauth: bool = False

    @classmethod
    def from_dict(cls, obj, parent=None, **kwargs):
        # Don't use from_parent - directly instantiate to avoid recursion
        return cls(
            parent=parent,
            raw=obj,
            credentials=obj.get("credentials"),
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["credentials", "raw", "parent"]
            },
        )


@register_account_config("dataset-copy")
@dataclass
class DomoAccount_Config_DatasetCopy(DomoAccount_Config):
    data_provider_type: str = "dataset-copy"
    is_oauth: bool = False

    domo_instance: str = None
    access_token: str = field(repr=False, default=None)

    _field_map: dict = field(
        default_factory=lambda: {
            "instance": "domo_instance",
            "accessToken": "access_token",
        },
        repr=False,
        init=False,
    )

    _fields_for_serialization: list[str] = field(
        default_factory=lambda: ["domo_instance", "access_token"]
    )


@register_account_config("domo-access-token")
@dataclass
class DomoAccount_Config_DomoAccessToken(DomoAccount_Config):
    data_provider_type: str = "domo-access-token"
    is_oauth: bool = False

    domo_access_token: str = field(repr=False, default=None)
    username: str = None
    password: str = field(repr=False, default=None)

    _fields_for_serialization: list[str] = field(
        default_factory=lambda: ["domo_access_token", "username", "password"]
    )


@register_account_config("domo-governance-d14c2fef-49a8-4898-8ddd-f64998005600")
@dataclass
class DomoAccount_Config_Governance(DomoAccount_Config):
    is_oauth: bool = False
    data_provider_type: str = "domo-governance-d14c2fef-49a8-4898-8ddd-f64998005600"

    domo_instance: str = None
    access_token: str = field(repr=False, default=None)

    _field_map: dict = field(
        default_factory=lambda: {
            "apikey": "access_token",
            "customer": "domo_instance",
        },
        repr=False,
        init=False,
    )

    _fields_for_serialization: list[str] = field(
        default_factory=lambda: ["access_token", "domo_instance"]
    )
