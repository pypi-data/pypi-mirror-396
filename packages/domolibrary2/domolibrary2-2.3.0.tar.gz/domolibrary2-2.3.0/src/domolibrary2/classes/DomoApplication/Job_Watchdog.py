__all__ = [
    "Watchdog_Config",
    "Watchdog_Config_MaxIndexingTime",
    "Watchdog_Config__Variance",
    "Watchdog_Config_RowCountVariance",
    "Watchdog_Config_ExecutionVariance",
    "Watchdog_Config_ErrorDetection",
    "Watchdog_Config_LastDataUpdated",
    "Watchdog_Config_CustomQuery",
    "Watchdog_ConfigFactory",
    "DomoJob_Watchdog",
]

import datetime as dt
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum

import httpx

from ...auth import DomoAuth
from ...client.context import RouteContext
from ...routes import application as application_routes
from .Job_Base import DomoJob_Base, DomoTrigger_Schedule


@dataclass
class Watchdog_Config(ABC):
    entity_ids: list[str]
    entity_type: str  # dataflow or dataset
    watcher_parameters: dict
    report_type: str

    """base class for the different watchdog report types"""

    @classmethod
    def from_dict(cls, watcher_parameters_obj):  # executionPayload
        return cls(
            entity_ids=watcher_parameters_obj["entityIds"],
            entity_type=watcher_parameters_obj["entityType"],
            report_type=watcher_parameters_obj["type"],
            watcher_parameters=watcher_parameters_obj,
        )

    def to_dict(self):
        return {
            "entityIds": self.entity_ids,
            "entityType": self.entity_type,
            "type": self.report_type,
        }


@dataclass
class Watchdog_Config_MaxIndexingTime(Watchdog_Config):
    report_type = "max_indexing_time"
    max_indexing_time_mins = 30

    def __post_init__(self):
        self.max_indexing_time_mins = self.watcher_parameters[
            "maxIndexingTimeInMinutes"
        ]

    def to_dict(self, **kwargs):
        if kwargs.get("max_indexing_time_mins"):
            self.max_indexing_time_mins = kwargs["max_indexing_time_mins"]

        return {
            **super().to_dict(),
            "maxIndexingTimeInMinutes": self.max_indexing_time_mins,
        }


@dataclass
class Watchdog_Config__Variance(Watchdog_Config):
    report_type: str
    variance_percent: int = 10

    def __post_init__(self):
        self.variance_percent = self.watcher_parameters["variancePercent"]

    def to_dict(self, **kwargs):
        if kwargs.get("variance_percent"):
            self.variance_percent = kwargs["variance_percent"]

        return {
            **super().to_dict(),
            "variancePercent": self.variance_percent,
        }


@dataclass
class Watchdog_Config_RowCountVariance(Watchdog_Config__Variance):
    report_type = "row_count_variance"


@dataclass
class Watchdog_Config_ExecutionVariance(Watchdog_Config__Variance):
    report_type = "execution_variance"


@dataclass
class Watchdog_Config_ErrorDetection(Watchdog_Config):
    report_type: str = "error_detection"

    def to_dict(self, **kwargs):
        return {
            **self.super().to_dict(),
        }


@dataclass
class Watchdog_Config_LastDataUpdated(Watchdog_Config):
    report_type: str = "last_data_updated"
    min_data_update_frequency_in_mins: int = 10

    def __post_init__(self):
        self.min_data_update_frequency_in_mins = self.watcher_parameters[
            "minDataUpdateFrequencyInMinutes"
        ]

    def to_dict(self, **kwargs):
        if kwargs.get("min_data_update_frequency_in_mins"):
            self.min_data_update_frequency_in_mins = kwargs[
                "min_data_update_frequency_in_mins"
            ]

        return {
            **super().to_dict(),
            "minDataUpdateFrequencyInMinutes": self.min_data_update_frequency_in_mins,
        }


@dataclass
class Watchdog_Config_CustomQuery(Watchdog_Config):
    report_type: str = "custom_query"
    sql_query: str = ""

    def __post_init__(self):
        self.sql_query = self.watcher_parameters["sqlQuery"]

    def to_dict(self, **kwargs):
        if kwargs.get("sql_query"):
            self.sql_query = kwargs["sql_query"]

        return {
            **super().to_dict(),
            "sqlQuery": self.sql_query,
        }


class Watchdog_ConfigFactory(Enum):
    MAX_INDEXING_TIME = Watchdog_Config_MaxIndexingTime
    ROW_COUNT_VARIANCE = Watchdog_Config_RowCountVariance
    EXECUTION_VARIANCE = Watchdog_Config_ExecutionVariance
    ERROR_DETECTION = Watchdog_Config_ErrorDetection
    LAST_DATA_UPDATED = Watchdog_Config_LastDataUpdated
    CUSTOM_QUERY = Watchdog_Config_CustomQuery


@dataclass
class DomoJob_Watchdog(DomoJob_Base):
    custom_message: str = None
    remote_instance: str = None

    notify_emails: list[str] = field(default_factory=lambda: [])
    notify_group_ids: list[str] = field(default_factory=lambda: [])
    notify_user_ids: list[str] = field(default_factory=lambda: [])

    Config: Watchdog_Config = None
    webhooks: list[str] = None

    @classmethod
    def from_dict(cls, obj, auth):
        remote_instance = cls._format_remote_instance(
            obj["executionPayload"].get("domain")
        )

        watchdog_parameters_obj = obj["executionPayload"]["watcherParameters"]

        config = Watchdog_ConfigFactory[
            watchdog_parameters_obj["type"].upper()
        ].value.from_dict(watchdog_parameters_obj)

        return cls(
            **cls._convert_API_res_to_DomoJob_base_obj(obj),
            remote_instance=remote_instance,
            custom_message=obj["executionPayload"]["customMessage"],
            Config=config,
            notify_emails=obj["executionPayload"]["notifyEmailAddresses"],
            notify_group_ids=obj["executionPayload"]["notifyGroupIds"],
            notify_user_ids=obj["executionPayload"]["notifyUserIds"],
            webhooks=obj["executionPayload"]["webhooks"],
            auth=auth,
        )

    @classmethod
    async def get_by_id(
        cls,
        application_id,
        job_id,
        auth: DomoAuth,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
    ):
        return await cls._get_by_id(
            application_id=application_id,
            job_id=job_id,
            auth=auth,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            return_raw=return_raw,
            new_cls=cls,
            parent_class=cls.__name__,
        )

    def to_dict(self):
        return {
            **super().to_dict(),
            "executionPayload": {
                "customMessage": self.custom_message,
                "domain": self.remote_instance,
                "notifyEmailAddresses": self.notify_emails,
                "notifyGroupIds": self.notify_group_ids,
                "notifyUserIds": self.notify_user_ids,
                "watcherParameters": self.Config.to_dict(),
                "webhooks": self.webhooks,
            },
        }

    @classmethod
    async def create(
        cls,
        auth: DomoAuth,
        name: str,
        application_id: str,
        config: Watchdog_Config,
        logs_dataset_id: str,
        notify_user_ids: list = None,
        notify_group_ids: list = None,
        notify_emails: list = None,
        triggers: list[DomoTrigger_Schedule] = None,
        description: str = f"created via domolibrary - {dt.date.today()}",
        execution_timeout=1440,
        accounts: list[int] = None,
        remote_instance=None,
        custom_message: str = None,
        webhooks: list[str] = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        domo_job = cls(
            auth=auth,
            name=name,
            description=description,
            application_id=application_id,
            execution_timeout=execution_timeout,
            notify_user_ids=notify_user_ids or [],
            notify_group_ids=notify_group_ids or [],
            notify_emails=notify_emails or [],
            triggers=triggers or [],
            accounts=accounts or [],
            logs_dataset_id=logs_dataset_id,
            remote_instance=remote_instance,
            Config=config,
            custom_message=custom_message,
            webhooks=webhooks,
        )

        body = domo_job.to_dict()

        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await application_routes.create_application_job(
            auth=auth,
            application_id=application_id,
            body=body,
            context=context,
        )

        if return_raw:
            return res

        return cls.from_dict(res.response, auth=auth)


async def update(
    self: DomoJob_Base,
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    debug_num_stacks_to_drop=2,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    base_context = self._build_route_context(
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        **context_kwargs,
    )
    context = RouteContext.build_context(context=context or base_context)

    res = await application_routes.update_application_job(
        auth=self.auth,
        body=self.to_dict(),
        application_id=self.application_id,
        job_id=self.id,
        context=context,
    )

    return res


async def execute(
    self,
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    debug_num_stacks_to_drop=2,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    base_context = self._build_route_context(
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        **context_kwargs,
    )
    context = RouteContext.build_context(context=context or base_context)

    res = await application_routes.execute_application_job(
        auth=self.auth,
        application_id=self.application_id,
        job_id=self.id,
        context=context,
    )

    return res
