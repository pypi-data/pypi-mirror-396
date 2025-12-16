"""class based approach for interacting with the activity log"""

__all__ = ["ActivityLog_ObjectType", "DomoActivityLog"]

import datetime as dt
from enum import Enum

import httpx

from ..auth import DomoAuth
from ..client.context import RouteContext
from ..routes import activity_log as activity_log_routes
from ..utils import convert


class ActivityLog_ObjectType(Enum):
    """enumerates valid object types to pass to activity log api"""

    ACCESS_TOKEN = "ACCESS_TOKEN"
    ACCOUNT = "ACCOUNT"
    ACTIVITY_LOG = "ACTIVITY_LOG"
    ALERT = "ALERT"
    APP = "APP"
    APPDB_COLLECTION = "MAGNUM_COLLECTION"
    APPDB_DATASTORE = "MAGNUM_DATASTORE"
    AUTHORITY = "AUTHORITY"
    BEAST_MODE_FORMULA = "BEAST_MODE_FORMULA"
    BUZZ_CHANNEL = "CHANNEL"
    BUZZ_GROUP_CHAT = "GROUP_CHAT"
    BUZZ_THREAD = "HUDDLE"
    CARD = "CARD"
    CHART_COLOR_PALETTE = "CHART_COLOR_PALETTE"
    COLLECTION = "COLLECTION"
    CUSTOMER = "CUSTOMER"
    CUSTOMER_STATE = "CUSTOMER_STATE"
    CUSTOMER_TIER = "CUSTOMER_TIER"
    DATA_SCIENCE_NOTEBOOK = "DATA_SCIENCE_NOTEBOOK"
    DATAFLOW = "DATAFLOW_TYPE"
    DATASET = "DATA_SOURCE"
    DATASOURCE = "DATASOURCE"
    DEPLOYMENT = "DEPLOYMENT"
    DRILL_VIEW = "DRILL_VIEW"
    EASY_INVITE_LINK = "EASY_INVITE_LINK"
    ENABLED = "ENABLED"
    FILE = "FILE"
    FILE_VERSION = "FILE_REVISION"
    GROUP = "GROUP"
    LICENSE_PAGE = "LICENSE_PAGE"
    LOGIN_SETTINGS = "LOGIN_SETTINGS"
    NAME = "NAME"
    PDP_FILTER = "ADC_FILTER"
    PDP_POLICY = "ADC_POLICY"
    PAGE = "PAGE"
    PAGE_ANALYZER = "PAGE_ANALYZER"
    PAGE_COLLECTION = "PAGE_COLLECTION"
    PROJECT = "PROJECT"
    PROJECT_LIST = "PROJECT_LIST"
    PROJECT_TASK = "PROJECT_TASK"
    PROJECT_TASK_ATTACHMENT = "PROJECT_TASK_ATTACHMENT"
    PROJECT_TASK_OWNER = "PROJECT_TASK_OWNER"
    PROXIER_EMAIL = "PROXIER_EMAIL"
    PUBLIC_EMBED_URL = "PUBLIC_URL"
    PUBLICATION = "PUBLICATION"
    REPOSITORY = "REPOSITORY"
    REPOSITORY_AUTHORIZATION = "REPOSITORY_AUTHORIZATION"
    ROLE = "ROLE"
    SEGMENT = "SEGMENT"
    SSO_PAGE = "SSO_PAGE"
    SUBSCRIBER = "PROXY_USER"
    USER = "USER"
    USER_STATE = "USER_STATE"
    VARIABLE = "VARIABLE"
    VARIABLE_CONTROL = "VARIABLE_CONTROL"
    NOTEBOOK_VIEW = "CONTAINER_VIEW"
    VIEW = "VIEW"
    VIRTUAL_USER = "VIRTUAL_USER"
    WORKBENCH_AGENT = "Workbench_AGENT"
    WORKBENCH_JOB = "Workbench_JOB"
    WORKBENCH_SCHEDULE = "Workbench_SCHEDULE"


class DomoActivityLog:
    @staticmethod
    def _process_activity_log_row(row):
        if row.get("time"):
            row.update(
                {
                    "time_dt": convert.convert_epoch_millisecond_to_datetime(
                        row.get("time")
                    )
                }
            )

            row.update({"date": row.get("time_dt").date()})

        return row

    @classmethod
    async def get_activity_log(
        cls,
        auth: DomoAuth,
        start_time: dt.datetime,
        end_time: dt.datetime,
        object_type: ActivityLog_ObjectType | None = None,
        maximum: int = 1000,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_loop: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """queries the activity log"""

        start_time_epoch = convert.convert_datetime_to_epoch_millisecond(start_time)
        end_time_epoch = convert.convert_datetime_to_epoch_millisecond(end_time)

        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=2,
            parent_class=cls.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res_activity_log = await activity_log_routes.search_activity_log(
            auth=auth,
            start_time=start_time_epoch,
            end_time=end_time_epoch,
            maximum=maximum,
            object_type=object_type.value,
            debug_loop=debug_loop,
            context=context,
        )

        if res_activity_log.is_success:
            return [
                cls._process_activity_log_row(row) for row in res_activity_log.response
            ]

        return None
