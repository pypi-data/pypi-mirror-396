__all__ = [
    "DomoTrigger_Schedule",
    "DomoTrigger",
    "DomoJob_Base",
    # Route exceptions
    "ApplicationNoJobRetrievedError",
    "Application_CRUD_Error",
]

import datetime as dt
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base import DomoEntity
from ...base.exceptions import DomoError
from ...client.context import RouteContext
from ...routes import application as application_routes
from ...routes.application import (
    Application_CRUD_Error,
    ApplicationNoJobRetrievedError,
)
from ...utils import convert as cc


@dataclass
class DomoTrigger_Schedule:
    schedule_text: str = None
    schedule_type: str = "scheduleTriggered"

    minute: int = None
    hour: int = None
    minute_str: str = None
    hour_str: str = None

    @classmethod
    def _from_str(cls, s_text, s_type):
        sched = cls(schedule_type=s_type, schedule_text=s_text)

        try:
            parsed_hour = s_text.split(" ")[2]
            parsed_minute = s_text.split(" ")[1]

            if "*" in parsed_hour or "/" in parsed_hour:
                sched.hour_str = parsed_hour
            else:
                sched.hour = int(float(parsed_hour))
            if "*" in parsed_minute:
                sched.minute_str = parsed_minute
            else:
                sched.minute = int(float(parsed_minute))

            return sched

        except DomoError as e:
            print(f"unable to parse schedule {s_text}")
            print(e)

    def to_obj(self):
        return {"hour": int(self.hour), "minute": int(self.minute)}

    def to_dict(self):
        minute = self.minute_str if self.minute_str is not None else str(self.minute)
        hour = self.hour_str if self.hour_str is not None else str(self.hour)
        return {
            "eventEntity": f"0 {minute} {hour} ? * *",
            # old value on Jan 13
            # "eventEntity": f'0 {minute} {hour} 1/1 * ? *',
            "eventType": self.schedule_type,
        }


@dataclass
class DomoTrigger:
    id: str
    job_id: str
    schedule: list[DomoTrigger_Schedule] = None

    @classmethod
    def from_dict(cls, obj):
        return cls(
            id=obj["triggerId"],
            job_id=obj["jobId"],
            schedule=DomoTrigger_Schedule._from_str(
                s_text=obj.get("eventEntity"), s_type=obj.get("eventType")
            ),
        )


@dataclass(eq=False)
class DomoJob_Base(DomoEntity):
    """
    the base class only captures attributes applicable to all jobs (i.e. does not destructure execution_payload onto the class)
    build Application / Job extensions by creating children of the DomoJob_Base class
    """

    auth: DomoAuth = field(repr=False)
    id: str = None
    raw: dict = field(default_factory=dict, repr=False)

    name: str = None
    application_id: str = None

    logs_dataset_id: str = None
    user_id: str = None
    execution_timeout: int = 1440

    is_enabled: bool = False  # based on triggers
    customer_id: str = None
    created_dt: dt.datetime = None
    updated_dt: dt.datetime = None

    description: str = None

    execution_payload: dict = field(default_factory=lambda: {})
    share_state: dict = field(default_factory=lambda: {})
    accounts: list[str] = field(default_factory=list)
    triggers: list[DomoTrigger] = field(default_factory=list)

    @property
    def display_url(self) -> str:
        """Generate the URL to display this job in the Domo interface.

        Returns:
            str: Complete URL to view the job in Domo
        """
        return f"https://{self.auth.domo_instance}.domo.com/admin/apps/{self.application_id}/jobs/{self.id}"

    @staticmethod
    def _format_remote_instance(remote_instance):
        if not remote_instance:
            return remote_instance

        return remote_instance.replace(".domo.com", "")

    @staticmethod
    def _convert_API_res_to_DomoJob_base_obj(obj) -> dict:
        """base class for converting an API response into a dictionary with parameters that DomoJob_Base expects"""

        triggers_ls = obj.get("triggers")
        domo_triggers = (
            [DomoTrigger.from_dict(tg) for tg in triggers_ls] if triggers_ls else []
        )

        return {
            "id": obj["jobId"],
            "name": obj["jobName"],
            "user_id": obj["userId"],
            "application_id": obj["applicationId"],
            "customer_id": obj["customerId"],
            "execution_timeout": obj["executionTimeout"],
            "execution_payload": obj["executionPayload"],
            "logs_dataset_id": obj["executionPayload"]["metricsDatasetId"],
            "share_state": obj.get("shareState", {}),
            "created_dt": cc.convert_epoch_millisecond_to_datetime(obj["created"]),
            "updated_dt": cc.convert_epoch_millisecond_to_datetime(obj["updated"]),
            "is_enabled": True if triggers_ls else False,
            "description": obj.get("jobDescription"),
            "accounts": obj.get("accounts"),
            "triggers": domo_triggers,
        }

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict[str, Any],
    ):
        """Create a DomoJob_Base instance from an API response dictionary.

        Args:
            auth: Authentication object for API requests
            obj: Dictionary representation of the job from API response

        Returns:
            DomoJob_Base instance
        """

        base_obj = cls._convert_API_res_to_DomoJob_base_obj(obj=obj)

        return cls(
            auth=auth,
            raw=obj,
            **base_obj,
        )

    @classmethod
    async def _get_by_id(
        cls,
        auth: DomoAuth,
        application_id: str,
        job_id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        parent_class: str | None = None,
        return_raw: bool = False,
        new_cls: "DomoJob_Base" = None,  # pass in a child class which has the mandatory "from_dict" function
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """
        Internal method to retrieve a job by ID with support for inheritance.

        This function receives the parent_class as an input_parameter (instead of relying on the actual class DomoJob_Base)
        to call the `new_class.from_dict()`

        This process handles converting the JSON obj into 'the correct' class

        Args:
            auth: Authentication object for API requests
            application_id: The ID of the application containing the job
            job_id: The ID of the job to retrieve
            session: Optional HTTP session for connection pooling
            debug_api: Enable API debugging output
            debug_num_stacks_to_drop: Number of stack frames to drop in debugging
            parent_class: Name of the calling class for error reporting
            return_raw: Return raw response without processing
            new_cls: Child class to instantiate (defaults to cls)

        Returns:
            DomoJob_Base instance or ResponseGetData if return_raw=True

        Raises:
            ApplicationNoJobRetrievedError: If job retrieval fails
        """
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await application_routes.get_application_job_by_id(
            auth=auth,
            application_id=application_id,
            job_id=job_id,
            context=context,
        )

        if return_raw:
            return res

        if not res.is_success:
            raise ApplicationNoJobRetrievedError(
                res=res,
                application_id=application_id,
            )

        cls = new_cls or cls

        return cls.from_dict(
            auth=auth,
            obj=res.response,
        )

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        application_id: str,
        job_id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """
        Retrieve a job by its ID from a specific application.

        Args:
            auth: Authentication object for API requests
            application_id: The ID of the application containing the job
            job_id: The ID of the job to retrieve
            session: Optional HTTP session for connection pooling
            debug_api: Enable API debugging output
            debug_num_stacks_to_drop: Number of stack frames to drop in debugging
            return_raw: Return raw response without processing

        Returns:
            DomoJob_Base instance or ResponseGetData if return_raw=True

        Raises:
            ApplicationNoJobRetrievedError: If job retrieval fails
        """

        return await cls._get_by_id(
            auth=auth,
            application_id=application_id,
            job_id=job_id,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            return_raw=return_raw,
            new_cls=cls,
            context=context,
            **context_kwargs,
        )

    def _generate_to_dict(self) -> dict:
        """returns a base dictionary representation of the DomoJob_Base class"""

        trigger_ls = (
            [self.triggers[0].schedule.to_dict()] if len(self.triggers) > 0 else []
        )

        execution_payload = self.execution_payload or {}
        execution_payload.update({"metricsDatasetId": self.logs_dataset_id})

        return {
            "jobId": self.id,
            "jobName": self.name,
            "userId": self.user_id,
            "applicationId": self.application_id,
            "customerId": self.customer_id,
            "executionTimeout": self.execution_timeout,
            "executionPayload": execution_payload,
            "shareState": self.share_state,
            # created / excluded because generated metadata
            # updated / excluded because generated metadata
            "triggers": trigger_ls,
            "jobDescription": self.description,
            "accounts": self.accounts,
        }

    def to_dict(self):
        """this is an abstract method, each DomoJob_Base implementation must define a to_dict() function"""
        return self._generate_to_dict()
