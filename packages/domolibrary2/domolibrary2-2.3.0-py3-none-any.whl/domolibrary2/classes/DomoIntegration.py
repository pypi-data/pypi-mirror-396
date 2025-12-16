__all__ = [
    "CloudAmplifier_PollingSchedule",
    "CloudAmplifier_Warehouse",
    "DomoIntegration_OwnerEntity",
    "DomoIntegration_PropertyConfig",
    "DomoIntegration",
]

from dataclasses import dataclass
from typing import Any

import httpx

from ..auth import DomoAuth
from ..base.entities import DomoEntity
from ..client.context import RouteContext
from ..routes import cloud_amplifier as cloud_amplifier_routes


@dataclass
class CloudAmplifier_PollingSchedule:
    days_of_week: list[int]
    interval: str
    months_of_year: list[int]
    once_a_day: bool
    timezone: str
    type: str

    def to_dict(self):
        return {
            "daysOfWeek": self.days_of_week,
            "interval": self.interval,
            "monthsOfYear": self.months_of_year,
            "onceADay": self.once_a_day,
            "timezone": self.timezone,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            days_of_week=d.get("daysOfWeek", []),
            interval=d.get("interval"),
            months_of_year=d.get("monthsOfYear", []),
            once_a_day=d.get("onceADay"),
            timezone=d.get("timezone"),
            type=d.get("type"),
        )


@dataclass
class CloudAmplifier_Warehouse:
    activities: list[str]
    activity: str
    device: str
    device_name: str
    domo_useable: bool
    instance_size: int
    warehouse: str
    warehouse_size_friendly_name: str

    def to_dict(self):
        return {
            "activities": self.activities,
            "activity": self.activity,
            "device": self.device,
            "deviceName": self.device_name,
            "domoUseable": self.domo_useable,
            "instanceSize": self.instance_size,
            "warehouse": self.warehouse,
            "warehouseSizeFriendlyName": self.warehouse_size_friendly_name,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            activities=d.get("activities", []),
            activity=d.get("activity"),
            device=d.get("device"),
            device_name=d.get("deviceName"),
            domo_useable=d.get("domoUseable"),
            instance_size=d.get("instanceSize"),
            warehouse=d.get("warehouse"),
            warehouse_size_friendly_name=d.get("warehouseSizeFriendlyName"),
        )


@dataclass
class DomoIntegration_OwnerEntity:
    id: str
    type: Any

    def to_dict(self):
        return {"id": self.id, "type": self.type}

    @classmethod
    def from_dict(cls, d: dict):
        return cls(id=d.get("id"), type=d.get("type"))


@dataclass
class DomoIntegration_PropertyConfig:
    config_type: str
    key: str
    value: Any

    def to_dict(self):
        return {"configType": self.config_type, "key": self.key, "value": self.value}

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            config_type=d.get("configType"), key=d.get("key"), value=d.get("value")
        )


@dataclass(eq=False)
class DomoIntegration(DomoEntity):
    id: str

    admin_auth_method: str
    auth_method: str
    description: str
    enable_native_transform: bool
    engine: str
    friendly_name: str
    initialized: bool
    owner_entity: DomoIntegration_OwnerEntity
    polling_rate_min: int
    polling_schedule: CloudAmplifier_PollingSchedule
    properties: dict[str, DomoIntegration_PropertyConfig]
    service_account_id: str
    ttl_minutes: int
    warehouses: list[CloudAmplifier_Warehouse]
    warehouses_valid_configuration: bool
    writeable: bool

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        integration_id: str,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> "DomoIntegration":
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await cloud_amplifier_routes.get_integration_by_id(
            integration_id=integration_id,
            auth=auth,
            context=context,
        )

        if return_raw:
            return res

        return cls.from_dict(res.response)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            id=d.get("id"),
            admin_auth_method=d.get("adminAuthMethod"),
            auth_method=d.get("authMethod"),
            description=d.get("description"),
            enable_native_transform=d.get("enableNativeTransform"),
            engine=d.get("engine"),
            friendly_name=d.get("friendlyName"),
            initialized=d.get("initialized"),
            owner_entity=DomoIntegration_OwnerEntity.from_dict(
                d.get("ownerEntity", {})
            ),
            polling_rate_min=d.get("pollingRateMin"),
            polling_schedule=CloudAmplifier_PollingSchedule.from_dict(
                d.get("pollingSchedule", {})
            ),
            properties={
                k: DomoIntegration_PropertyConfig.from_dict(v)
                for k, v in d.get("properties", {}).items()
            },
            service_account_id=d.get("serviceAccountId"),
            ttl_minutes=d.get("ttlMinutes"),
            warehouses=[
                CloudAmplifier_Warehouse.from_dict(w) for w in d.get("warehouses", [])
            ],
            warehouses_valid_configuration=d.get("warehousesValidConfiguration"),
            writeable=d.get("writeable"),
        )

    def to_dict(self):
        return {
            "adminAuthMethod": self.admin_auth_method,
            "authMethod": self.auth_method,
            "description": self.description,
            "enableNativeTransform": self.enable_native_transform,
            "engine": self.engine,
            "friendlyName": self.friendly_name,
            "id": self.id,
            "initialized": self.initialized,
            "ownerEntity": self.owner_entity.to_dict() if self.owner_entity else None,
            "pollingRateMin": self.polling_rate_min,
            "pollingSchedule": (
                self.polling_schedule.to_dict() if self.polling_schedule else None
            ),
            "properties": (
                {k: v.to_dict() for k, v in self.properties.items()}
                if self.properties
                else {}
            ),
            "serviceAccountId": self.service_account_id,
            "ttlMinutes": self.ttl_minutes,
            "warehouses": (
                [w.to_dict() for w in self.warehouses] if self.warehouses else []
            ),
            "warehousesValidConfiguration": self.warehouses_valid_configuration,
            "writeable": self.writeable,
        }
