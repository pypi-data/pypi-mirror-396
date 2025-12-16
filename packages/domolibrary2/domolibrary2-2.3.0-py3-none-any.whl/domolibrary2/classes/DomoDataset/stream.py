from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base import (
    DomoEntity,
    DomoManager,
    exceptions as dmde,
)
from ...client.context import RouteContext
from ...routes.dataset import stream as stream_routes
from ...routes.dataset.stream import Stream_CRUD_Error, Stream_GET_Error
from ...utils import chunk_execution as dmce
from ...utils.logging import get_colored_logger
from ..subentity.schedule import DomoSchedule
from .stream_configs import StreamConfig

__all__ = [
    "DomoStream",
    "DomoStreams",
    # Stream Route Exceptions
    "Stream_GET_Error",
    "Stream_CRUD_Error",
]

logger = get_colored_logger()


@dataclass(eq=False)
class DomoStream(DomoEntity):
    """A class for interacting with a Domo Stream (dataset connector)"""

    id: str
    parent: Any = field(repr=False)  # DomoDataset

    transport_description: str = None
    transport_version: int = None
    update_method: str = None
    data_provider_name: str = None
    data_provider_key: str = None
    account_id: str = None
    account_display_name: str = None
    account_userid: str = None

    has_mapping: bool = False
    configuration: list[StreamConfig] = field(default_factory=list)
    configuration_tables: list[str] = field(default_factory=list)
    configuration_query: str = None

    Schedule: DomoSchedule = None  # DomoDataset_Schedule
    Account: Any = field(
        default=None, repr=False
    )  # DomoAccount - set via get_account()

    def __post_init__(self):
        """Post-initialization to extract schedule if present"""
        self.extract_schedule_from_raw()

    def extract_schedule_from_raw(self):
        """Extract schedule from stream configuration if available"""

        if self.raw:
            self.Schedule = DomoSchedule.from_parent(parent=self, obj=self.raw)

        return self.Schedule

    @classmethod
    def from_parent(cls, parent, stream_id: str = None):
        return cls(
            parent=parent,
            id=stream_id or parent.raw.get("streamId"),
            raw=parent.raw,
            auth=parent.auth,
        )

    @property
    def entity_type(self):
        return "STREAM"

    @property
    def display_url(self):
        """Generate URL to view this stream in the Domo UI"""
        return f"https://{self.auth.domo_instance}.domo.com/datasources/{self.dataset_id}/details/data/table"

    @property
    def typed_config(self):
        """Convert list-based configuration to typed StreamConfig object.

        Returns the appropriate typed config class based on data_provider_key:
        - SnowflakeKeyPairAuth_StreamConfig for 'snowflakekeypairauthentication'
        - Snowflake_StreamConfig for 'snowflake'
        - AWSAthena_StreamConfig for 'aws-athena'
        - etc.

        Provides type-safe access to config parameters:
            stream.typed_config.query
            stream.typed_config.database_name
            stream.typed_config.warehouse

        Returns None if provider type is not recognized or config is empty.
        """
        from .stream_configs._base import _CONFIG_REGISTRY

        if not self.configuration or not self.data_provider_key:
            return None

        # Get the typed config class for this provider
        config_class = _CONFIG_REGISTRY.get(self.data_provider_key)
        if not config_class:
            return None

        # Convert list of StreamConfig to dict
        config_dict = {
            cfg.name: cfg.value
            for cfg in self.configuration
            if cfg.name and cfg.value is not None
        }

        # Create typed config instance
        return config_class.from_dict(config_dict)

    def _get_conformed_value(self, property_name: str) -> str | None:
        """Generic helper to extract conformed property value.

        Uses the CONFORMED_PROPERTIES registry to map semantic property names
        to platform-specific typed_config attributes.

        Args:
            property_name: Name of conformed property (e.g., "query", "database")

        Returns:
            Value from typed_config if available, None otherwise

        Example:
            >>> stream._get_conformed_value("query")
            "SELECT * FROM my_table"
        """
        from .stream_configs._conformed import CONFORMED_PROPERTIES

        typed = self.typed_config
        if typed is None:
            return None

        # Get the conformed property definition
        conformed_prop = CONFORMED_PROPERTIES.get(property_name)
        if not conformed_prop:
            return None

        # Get the attribute name for this provider
        attr_name = conformed_prop.get_key_for_provider(self.data_provider_key)
        if not attr_name:
            return None

        # Get the value from typed config
        return getattr(typed, attr_name, None)

    @property
    def sql(self) -> str | None:
        """Get SQL query from stream configuration (cross-platform).

        Works across providers that use SQL queries:
        - Snowflake (all variants)
        - AWS Athena
        - Amazon Athena High Bandwidth
        - PostgreSQL

        Returns:
            SQL query string or None if not available

        Example:
            >>> stream = await DomoStream.get_by_id(auth, stream_id)
            >>> print(stream.sql)
            "SELECT * FROM my_table"
        """
        # Try standard query property first
        result = self._get_conformed_value("query")
        if result:
            return result

        # Fall back to custom_query for some Snowflake variants
        return self._get_conformed_value("custom_query")

    @property
    def database(self) -> str | None:
        """Get database name from stream configuration (cross-platform).

        Works across database providers:
        - Snowflake (all variants)
        - AWS Athena
        - PostgreSQL

        Returns:
            Database name or None if not available

        Example:
            >>> stream.database
            "SA_PRD"
        """
        return self._get_conformed_value("database")

    @property
    def schema(self) -> str | None:
        """Get schema name from stream configuration (cross-platform).

        Works for providers that support schemas:
        - Snowflake (with keypair auth)
        - PostgreSQL

        Returns:
            Schema name or None if not available

        Example:
            >>> stream.schema
            "PUBLIC"
        """
        return self._get_conformed_value("schema")

    @property
    def warehouse(self) -> str | None:
        """Get warehouse/compute resource from stream configuration.

        Works for Snowflake variants that use compute warehouses.

        Returns:
            Warehouse name or None if not available

        Example:
            >>> stream.warehouse
            "COMPUTE_WH"
        """
        return self._get_conformed_value("warehouse")

    @property
    def table(self) -> str | None:
        """Get table name from stream configuration (cross-platform).

        Works for providers that operate on specific tables:
        - AWS Athena
        - Snowflake Writeback

        Returns:
            Table name or None if not available

        Example:
            >>> stream.table
            "my_table"
        """
        return self._get_conformed_value("table")

    @property
    def report_id(self) -> str | None:
        """Get report identifier from stream configuration (cross-platform).

        Works for reporting/analytics platforms:
        - Adobe Analytics (report suite ID)
        - Qualtrics (survey ID)

        Returns:
            Report/survey identifier or None if not available

        Example:
            >>> stream.report_id
            "report_suite_12345"
        """
        return self._get_conformed_value("report_id")

    @property
    def spreadsheet(self) -> str | None:
        """Get spreadsheet identifier from stream configuration.

        Works for Google connectors:
        - Google Sheets
        - Google Spreadsheets

        Returns:
            Spreadsheet ID/filename or None if not available

        Example:
            >>> stream.spreadsheet
            "1A2B3C4D5E6F7G8H9I"
        """
        return self._get_conformed_value("spreadsheet")

    @property
    def bucket(self) -> str | None:
        """Get S3 bucket or cloud storage location from stream configuration.

        Works for AWS S3 connectors.

        Returns:
            Bucket name/path or None if not available

        Example:
            >>> stream.bucket
            "my-s3-bucket"
        """
        return self._get_conformed_value("bucket")

    @property
    def dataset_id(self) -> str:
        """Get dataset ID for this stream.

        For Domo-to-Domo dataset copy connectors, returns the source dataset ID.
        For all other streams, returns the parent dataset ID.

        Returns:
            Dataset ID string

        Example:
            >>> stream.dataset_id
            "abc123"
        """
        # Check for dataset-copy connector first
        dataset_copy_id = self._get_conformed_value("dataset_id")
        if dataset_copy_id:
            return dataset_copy_id

        # Return parent dataset ID
        return self.parent.id

    @property
    def file_url(self) -> str | None:
        """Get file URL from stream configuration.

        Works for file-based connectors like Domo CSV.

        Returns:
            File URL or None if not available

        Example:
            >>> stream.file_url
            "https://example.com/data.csv"
        """
        return self._get_conformed_value("file_url")

    @property
    def host(self) -> str | None:
        """Get host/server address from stream configuration.

        Works for database and API connectors:
        - PostgreSQL (database host)
        - SharePoint Online (site URL)

        Returns:
            Host address/URL or None if not available

        Example:
            >>> stream.host
            "mydb.example.com"
        """
        return self._get_conformed_value("host")

    @property
    def port(self) -> str | None:
        """Get port number from stream configuration.

        Works for database connectors like PostgreSQL.

        Returns:
            Port number as string or None if not available

        Example:
            >>> stream.port
            "5432"
        """
        return self._get_conformed_value("port")

    def __repr__(self) -> str:
        """Custom repr that includes conformed properties.

        Shows ID, provider, and relevant conformed properties based on
        the stream's data provider type. Only shows properties where
        is_repr=True in CONFORMED_PROPERTIES registry.

        Example:
            >>> stream
            DomoStream(id='123', provider='snowflake', sql='SELECT...', database='SA_PRD')
        """
        from .stream_configs._repr import create_stream_repr

        return create_stream_repr(self)

    @property
    def _missing_mappings(self) -> list[str]:
        """Get list of conformed properties that don't have mappings for this provider.

        Useful for debugging and understanding which properties are not applicable
        for a given stream's data provider.

        Returns:
            List of property names (where is_repr=True) that don't support this provider

        Example:
            >>> stream.data_provider_key = "google-sheets"
            >>> stream._missing_mappings
            ['query', 'database', 'warehouse']  # SQL properties not supported

            >>> stream.data_provider_key = "snowflake"
            >>> stream._missing_mappings
            ['report_id', 'spreadsheet']  # Analytics properties not supported
        """
        from .stream_configs._repr import get_missing_mappings

        return get_missing_mappings(self)

    @property
    def _available_config_keys(self) -> list[str]:
        """Get list of typed_config keys that are NOT mapped to conformed properties.

        This helps identify gaps in conformed property mappings - keys that exist
        in the typed_config but don't have a corresponding conformed property yet.

        Useful for:
        - Discovering new properties to add to CONFORMED_PROPERTIES
        - Understanding provider-specific configuration options
        - Identifying unmapped configuration parameters

        Returns:
            List of typed_config attribute names not mapped to conformed properties

        Example:
            >>> stream.data_provider_key = "snowflake"
            >>> stream._available_config_keys
            ['role', 'authenticator', 'private_key']
            # These keys exist in config but aren't mapped to conformed properties yet

            >>> # Add missing keys to CONFORMED_PROPERTIES registry
            >>> # Then they'll disappear from _available_config_keys
        """
        from .stream_configs._repr import get_available_config_keys

        return get_available_config_keys(self)

    @classmethod
    def from_dict(cls, auth, obj, parent: Any | None = None, **kwargs):  # DomoDataset
        data_provider = obj.get("dataProvider", {})
        transport = obj.get("transport", {})
        obj.get("dataSource", {})

        account = obj.get("account", {})

        sd = cls(
            auth=auth,
            parent=parent,  # Will be set by caller if needed
            id=obj.get("id") or kwargs.get("stream_id"),
            transport_description=transport.get("description"),
            transport_version=transport.get("version"),
            update_method=obj.get("updateMethod"),
            data_provider_name=data_provider.get("name"),
            data_provider_key=data_provider.get("key"),
            raw=obj,
            **{k: v for k, v in kwargs.items() if k != "stream_id"},
        )

        if account:
            sd.account_id = account.get("id")
            sd.account_display_name = account.get("displayName")
            sd.account_userid = account.get("userId")

        sd.configuration = [
            StreamConfig.from_json(
                obj=c_obj, data_provider_type=data_provider.get("key"), parent_stream=sd
            )
            for c_obj in obj.get("configuration", [])
        ]

        return sd

    def generate_config_rpt(self):
        res = {}

        for config in self.configuration:
            if config.stream_category != "default" and config.stream_category:
                obj = config.to_dict()
                res.update({obj["field"]: obj["value"]})

        return res

    async def refresh(
        self,
        is_get_account: bool = True,
        is_suppress_no_account_config: bool = True,
        *,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        # Only refresh if stream has an ID (some datasets don't have streams)
        if not self.id:
            return self

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if is_get_account:
            await self.get_account(
                force_refresh=True,
                context=context,
                is_suppress_no_account_config=is_suppress_no_account_config,
            )

        await super().refresh(
            context=context,
            is_suppress_no_account_config=is_suppress_no_account_config,
        )

        return self

    async def get(self, **kwargs):
        return await self.refresh(**kwargs)

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        stream_id: str,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        is_get_account: bool = True,
        is_suppress_no_account_config: bool = True,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Get a stream by its ID.

        Args:
            auth: Authentication object
            stream_id: Unique stream identifier
            return_raw: Return raw response without processing
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            debug_api: Enable API debugging
            session: HTTP client session
            is_get_account: If True and account_id is present, retrieve full Account object
            is_suppress_no_account_config: If True, suppress errors when account config is not found
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            DomoStream instance or ResponseGetData if return_raw=True

        Raises:
            Stream_GET_Error: If stream retrieval fails
        """
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

        res = await stream_routes.get_stream_by_id(
            auth=auth,
            stream_id=stream_id,
            context=context,
        )

        if return_raw:
            return res

        stream = cls.from_dict(auth=auth, obj=res.response)

        # Retrieve Account if account_id is present
        if is_get_account and stream.account_id:
            await stream.get_account(
                context=context,
                force_refresh=True,
                is_suppress_no_account_config=is_suppress_no_account_config,
            )
        return stream

    @classmethod
    async def get_entity_by_id(cls, entity_id: str, auth: DomoAuth, **kwargs):
        return await cls.get_by_id(stream_id=entity_id, auth=auth, **kwargs)

    @classmethod
    async def create(
        cls,
        cnfg_body,
        auth: DomoAuth = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
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
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        return await stream_routes.create_stream(
            auth=auth, body=cnfg_body, context=context
        )

    async def update(
        self,
        cnfg_body,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
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

        res = await stream_routes.update_stream(
            auth=self.auth,
            stream_id=self.id,
            body=cnfg_body,
            context=context,
        )
        return res

    async def get_account(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        force_refresh: bool = False,
        is_suppress_no_account_config: bool = True,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> Any | None:  # DomoAccount
        """Retrieve the Account associated with this stream.

        Args:
            session: HTTP client session
            debug_api: Enable API debugging
            force_refresh: If True, refresh even if Account is already set
            is_suppress_no_account_config: If True, suppress errors when account config is not found
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            DomoAccount instance or None if no account_id

        Example:
            >>> stream = await DomoStream.get_by_id(auth=auth, stream_id="123")
            >>> account = await stream.get_account()
            >>> print(f"Account: {account.name}")
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if not self.account_id:
            return None

        if self.Account is not None and not force_refresh:
            return self.Account

        from ..DomoAccount import DomoAccount

        try:
            self.Account = await DomoAccount.get_by_id(
                auth=self.auth,
                account_id=self.account_id,
                context=context,
                is_use_default_account_class=False,
                is_suppress_no_config=is_suppress_no_account_config,
            )
        except dmde.DomoError as e:
            if is_suppress_no_account_config:
                await logger.warning(
                    f"Warning: Could not retrieve account {self.account_id}: {e}"
                )
                self.Account = None
            else:
                raise e from e

        return self.Account


@dataclass
class DomoStreams(DomoManager):
    streams: list[DomoStream] = field(default=None)

    async def get(
        self,
        search_dataset_name: str = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        from ...routes import dataset as dataset_routes

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await dataset_routes.search_datasets(
            auth=self.auth,
            search_text=search_dataset_name,
            context=context,
        )

        self.streams = await dmce.gather_with_concurrency(
            *[
                DomoStream.get_by_id(
                    self.auth, stream_id=obj["streamId"], context=context
                )
                for obj in res.response
            ],
            n=10,
        )

        return self.streams

    async def upsert(
        self,
        cnfg_body,
        match_name=None,
        auth: DomoAuth = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        from ...routes import datacenter as datacenter_routes

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await datacenter_routes.search_datacenter(
            auth=auth or self.auth,
            entity_type=datacenter_routes.Datacenter_Enum.DATASET,
            search_text=match_name,
            context=context,
        )
        datasets = res.response

        existing_ds = next((ds for ds in datasets if ds.name == match_name), None)

        if existing_ds:
            domo_stream = await DomoStream.get_by_id(
                auth=auth, stream_id=existing_ds.stream_id, context=context
            )

            return await domo_stream.update(
                cnfg_body,
                context=context,
            )

        else:
            return await DomoStream.create(cnfg_body, auth=auth, context=context)
