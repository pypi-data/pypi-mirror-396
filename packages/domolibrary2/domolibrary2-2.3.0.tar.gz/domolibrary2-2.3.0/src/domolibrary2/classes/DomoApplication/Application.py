__all__ = ["DomoApplication"]

from dataclasses import dataclass, field
from typing import Any

import httpx
import pandas as pd

from ...auth import DomoAuth
from ...client.context import RouteContext
from ...routes import application as application_routes
from ...utils import (
    DictDot as util_dd,
)
from . import Job as dmdj

# @jaewilson07 — DomoJob_RemoteDomoStats and DomoJob_Watchdog does not exist.
# class DomoJob_Types(Enum):
#     REMOTE_DOMO_STATS = dmdj.DomoJob_RemoteDomoStats
#     DATA_WATCHDOG = dmdj.DomoJob_Watchdog

#     default = dmdj.DomoJob

#     @staticmethod
#     def _convert_api_name_to_member_name(api_name):
#         return (
#             cc.convert_str_to_snake_case(api_name, is_only_alphanumeric=True)
#             .upper()
#             .replace("TOOLKIT_", "")
#         )

#     @classmethod
#     def get_from_api_name(cls, api_name):
#         member_name = cls._convert_api_name_to_member_name(api_name)

#         if member_name not in cls.__members__:
#             return cls["default"].value

#         return cls[member_name].value


# DomoJob_Types.get_from_api_name("Toolkit: Remote Domo Stat")


@dataclass
class DomoApplication:
    auth: DomoAuth = field(repr=False)
    id: str
    version: str = None
    name: str = None
    customer_id: str = None
    description: str = None
    execution_class: str = None
    grants: list[str] = None
    jobs: list[dmdj.DomoJob] = field(default=None)
    jobs_schedule: list[dmdj.DomoTrigger_Schedule] = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]):
        dd = util_dd.DictDot(obj)

        return cls(
            id=dd.applicationId,
            customer_id=dd.customerId,
            name=dd.name,
            description=dd.description,
            version=dd.version,
            execution_class=dd.executionClass,
            grants=dd.authorities,
            auth=auth,
        )

    # def _get_job_class(self):
    #     return DomoJob_Types.get_from_api_name(self.name)

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        application_id,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await application_routes.get_application_by_id(
            application_id=application_id,
            auth=auth,
            context=context,
        )

        if return_raw:
            return res

        return cls.from_dict(auth=auth, obj=res.response)

    async def get_jobs(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await application_routes.get_application_jobs(
            auth=self.auth,
            application_id=self.id,
            context=context,
        )

        if return_raw:
            return res

        job_cls = self._get_job_class()
        # print(job_cls)

        self.jobs = [job_cls.from_dict(job, auth=self.auth) for job in res.response]
        return self.jobs

    async def get_schedules(self) -> pd.DataFrame:
        if not self.jobs:
            await self.get_jobs()

        if not self.jobs:
            return

        triggered_jobs = [job for job in self.jobs if len(job.triggers) > 0]

        if not triggered_jobs:
            self.jobs_schedule = None
            return self.jobs_schedule

        schedules = pd.DataFrame(
            [
                {
                    **trigger.schedule.to_obj(),
                    "job_name": job.name,
                    "job_id": job.id,
                    "description": job.description,
                    "remote_instance": job.remote_instance,
                    "application": self.name,
                }
                for job in triggered_jobs
                for trigger in job.triggers
                if job and trigger
            ]
        )

        # return schedules

        self.jobs_schedule = schedules.sort_values(
            ["hour", "minute"], ascending=True
        ).reset_index(drop=True)
        return self.jobs_schedule

    async def find_next_job_schedule(
        self, return_raw: bool = False
    ) -> dmdj.DomoTrigger_Schedule:
        await self.get_jobs()
        await self.get_schedules()

        if self.jobs_schedule is None:
            return dmdj.DomoTrigger_Schedule(hour=0, minute=0)

        df_all_hours = pd.DataFrame(range(0, 23), columns=["hour"])
        df_all_minutes = pd.DataFrame(range(0, 60), columns=["minute"])

        df_all_hours["tmp"] = 1
        df_all_minutes["tmp"] = 1
        df_all = pd.merge(df_all_hours, df_all_minutes, on="tmp").drop(columns=["tmp"])

        # get the number of occurencies of each hour and minutes
        schedules_grouped = (
            self.jobs_schedule.groupby(["hour", "minute"])
            .size()
            .reset_index(name="cnt_schedule")
        )

        # print(schedules_grouped)
        # print(df_all)

        schedules_interpolated = pd.merge(
            df_all, schedules_grouped, how="left", on=["hour", "minute"]
        )

        schedules_interpolated["cnt_schedule"] = schedules_interpolated[
            "cnt_schedule"
        ].fillna(value=0)
        schedules_interpolated.sort_values(
            ["cnt_schedule", "hour", "minute"], ascending=True, inplace=True
        )

        schedules_interpolated.reset_index(drop=True, inplace=True)

        if return_raw:
            return schedules_interpolated

        return dmdj.DomoTrigger_Schedule(
            hour=int(schedules_interpolated.loc[0].get("hour")),
            minute=int(schedules_interpolated.loc[0].get("minute")),
        )
