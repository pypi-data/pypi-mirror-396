from dataclasses import dataclass, field
from typing import Any

from ....base.entities import DomoBase
from ....base.exceptions import ClassError
from ....utils import convert as dmcv


class AccountConfig_SerializationMismatchError(ClassError):
    def __init__(
        self,
        cls_instance,
        data_provider_type: str,
        account_id: str,
        only_in_to_dict: dict,
        only_in_raw: dict,
        value_mismatches: dict,
    ):
        errors = []
        if only_in_to_dict:
            errors.append(f"Only in to_dict(): {', '.join(only_in_to_dict.keys())}")
        if only_in_raw:
            errors.append(f"Only in raw: {', '.join(only_in_raw.keys())}")
        if value_mismatches:
            mismatch_details = []
            for k, v in value_mismatches.items():
                mismatch_details.append(
                    f"{k} (to_dict={v['to_dict']!r}, raw={v['raw']!r})"
                )
            errors.append(f"Value mismatches: {', '.join(mismatch_details)}")

        error_msg = " | ".join(errors)
        super().__init__(
            cls_instance=cls_instance,
            message=f"Serialization mismatch for {data_provider_type} (account_id={account_id}): {error_msg}",
        )


@dataclass
class DomoAccount_Config(DomoBase):
    """DomoAccount Config abstract base class"""

    data_provider_type: str
    is_oauth: bool

    allow_external_use: bool = True

    parent: Any = field(repr=False, default=None)  # DomoAccount
    raw: dict = field(repr=False, default=None)  # from api response

    # Custom field mapping for serialization/deserialization
    _field_map: dict = field(
        default_factory=dict, repr=False, init=False
    )  # e.g. {"passPhrase": "password"}

    # REQUIRED: Subclasses must define this field with their serialization mapping
    _fields_for_serialization: list[str] = field(
        default_factory=list, repr=False, init=False
    )

    def __post_init__(self):
        """Validate serialization after initialization."""
        # Only validate if we have raw data (i.e., created via from_dict)
        if self.raw:
            self.validate_compare_serialization()

    @property
    def allow_external_use_from_raw(self):
        if not self.raw:
            return None

        allow_external_use = self.raw.get("allowExternalUse")

        if isinstance(allow_external_use, str):
            allow_external_use = dmcv.convert_string_to_bool(allow_external_use)

        return allow_external_use

    @classmethod
    def from_parent(cls, parent, **kwargs):
        return cls.from_dict(
            obj=kwargs,
            parent=parent,
        )

    @classmethod
    def from_dict(cls, obj: dict[str, Any], parent: Any = None, **kwargs):
        """
        Create instance from dict, handling camelCase, snake_case, and _field_map.
        Robust to missing or None _field_map. Uses _field_map for both directions.
        """
        # Get _field_map from dataclass field's default_factory if it exists
        field_map = {}
        if (
            hasattr(cls, "__dataclass_fields__")
            and "_field_map" in cls.__dataclass_fields__
        ):
            field_def = cls.__dataclass_fields__["_field_map"]
            if field_def.default_factory:
                field_map = field_def.default_factory()

        # Build a reverse map for input keys that are snake_case but need to be mapped to camelCase
        reverse_map = {
            v: k for k, v in field_map.items()
        }  # {"passphrase" : "passPhrase"}

        init_kwargs = {}

        init_kwargs.update(kwargs)

        for k, v in obj.items():
            if k in ["_search_metadata"]:
                continue

            # Try direct field_map, then reverse_map, then camel_to_snake
            if k in field_map:
                attr = field_map[k]

            elif k in reverse_map:
                attr = reverse_map[k]

            else:
                attr = cls._camel_to_snake(k)

            init_kwargs[attr] = v

        return cls(parent=parent, raw=obj, **init_kwargs)

    def validate_compare_serialization(self, raise_on_mismatch: bool = True) -> bool:
        """
        Validate that to_dict() output matches raw data keys (ignoring values).

        Args:
            raise_on_mismatch: If True, raises AccountConfig_SerializationMismatchError on mismatch.
                             If False, returns False on mismatch.

        Returns:
            True if keys match, False otherwise (only if raise_on_mismatch=False)

        Raises:
            AccountConfig_SerializationMismatchError: If keys don't match and raise_on_mismatch=True
        """
        if not self.raw:
            return True

        to_dict_keys = set(self.to_dict(return_snake_case=False).keys())
        raw_keys = set(self.raw.keys()) - {"_search_metadata", "data_provider_type"}

        only_in_to_dict = to_dict_keys - raw_keys
        only_in_raw = raw_keys - to_dict_keys

        has_mismatch = bool(only_in_to_dict or only_in_raw)

        if has_mismatch and raise_on_mismatch:
            account_id = self.raw.get("_search_metadata", {}).get(
                "account_id", "unknown"
            )
            raise AccountConfig_SerializationMismatchError(
                cls_instance=self,
                data_provider_type=self.data_provider_type,
                account_id=str(account_id),
                only_in_to_dict={k: None for k in only_in_to_dict},
                only_in_raw={k: None for k in only_in_raw},
                value_mismatches={},
            )

        return not has_mismatch

    @staticmethod
    def _camel_to_snake(name):
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def _snake_to_camel(name):
        parts = name.split("_")
        return parts[0] + "".join(x.title() for x in parts[1:])

    def to_dict(
        self,
        export_fields: list[str] = None,
        override_fn: callable = None,
        return_snake_case: bool = False,
        **kwargs,
    ) -> dict:
        """
        Convert config to dictionary using provided fields or all _fields_for_serialization.
        """
        result = {"allowExternalUse": self.allow_external_use}

        # Use all fields_for_serialization if not provided
        export_fields = [
            key
            for key in (
                export_fields
                or self._fields_for_serialization
                or self.__dataclass_fields__.keys()
            )
            if key
            not in [
                "raw",
                "_field_map",
                "_fields_for_serialization",
                "is_oauth",
                "data_provider_type",
                "__serialize_properties__",
            ]
        ]

        reverse_map = {v: k for k, v in self._field_map.items()}

        for attr in export_fields:
            val = getattr(self, attr, None)
            if val is not None:
                key = reverse_map.get(attr, self._snake_to_camel(attr))
                result[key] = val

        result.update(kwargs)

        if return_snake_case:
            result = {self._camel_to_snake(k): v for k, v in result.items()}

        if override_fn:
            result = override_fn(self)

        return result
