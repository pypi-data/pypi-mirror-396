from __future__ import annotations

from ...base import exceptions as dmde

__all__ = [
    "DJW_Search_Error",
    "DJW_InvalidClass",
    "DomoJupyterWorkspace",
    "DomoJupyterWorkspaces",
]

import datetime as dt
import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import (
    DomoAuth,
    DomoFullAuth,
    DomoJupyterAuth,
    DomoJupyterFullAuth,
    DomoJupyterTokenAuth,
    DomoTokenAuth,
)
from ...base.entities import DomoEntity, DomoManager
from ...client.context import RouteContext
from ...routes import jupyter as jupyter_routes
from ...routes.jupyter import JupyterAPI_Error
from ...utils import (
    chunk_execution as dmce,
    files as defi,
)
from .. import DomoUser as dmdu
from ..DomoDataset import DomoDataset as dmds
from . import (
    Account as dmac,
)
from .Account import DomoJupyter_Account
from .Content import DomoJupyter_Content
from .DataSource import DomoJupyter_DataSource


class DJW_Search_Error(dmde.ClassError):
    def __init__(
        self,
        cls=None,
        cls_instance=None,
        search_name=None,
        message=None,
        domo_instance=None,
    ):
        super().__init__(
            cls=cls,
            cls_instance=cls_instance,
            message=message or f"unable to find {search_name}",
            entity_id=domo_instance
            or (cls_instance and cls_instance.auth.domo_instance),
        )


class DJW_InvalidClass(dmde.ClassError):
    def __init__(self, cls_instance, message):
        super().__init__(cls_instance=cls_instance, message=message)


@dataclass(eq=False)
class DomoJupyterWorkspace(DomoEntity):
    auth: DomoJupyterAuth = field(repr=False)
    id: str

    name: str
    description: str

    created_dt: dt.datetime
    updated_dt: dt.datetime

    owner: dict
    cpu: str
    memory: int

    last_run_dt: dt.datetime = None
    instances: list[dict] = None

    input_configuration: list[DomoJupyter_DataSource] = field(
        default_factory=lambda: []
    )
    output_configuration: list[DomoJupyter_DataSource] = field(
        default_factory=lambda: []
    )
    account_configuration: list[DomoJupyter_Account] = field(default_factory=lambda: [])
    content: list[DomoJupyter_Content] = field(default_factory=lambda: [])

    collection_configuration: list[dict] = None
    fileshare_configuration: list[dict] = None

    service_location: str = None
    service_prefix: str = None
    raw: dict

    def __post_init__(self):
        self._update_auth_params()

        self.account_configuration.sort()
        self.output_configuration.sort()
        self.input_configuration.sort()

    def __eq__(self, other) -> bool:
        """Check equality based on workspace ID.

        Args:
            other: Object to compare with

        Returns:
            bool: True if both are DomoJupyterWorkspace instances with the same ID
        """
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return self.id == other.id

    def _update_auth_params(self):
        """extracts service location and prefix from "instance" object"""

        if self.instances:
            res = jupyter_routes.parse_instance_service_location_and_prefix(
                self.instances[0], self.auth.domo_instance
            )
            self.service_location = res["service_location"]
            self.service_prefix = res["service_prefix"]

    @property
    def entity_type(self):
        return "jupyter_workspace"

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/ai-services/jupyter"

    def update_auth_to_jupyter_auth(self, jupyter_token: str):
        """
        interacting with jupyter notebook content requires an additional authentication against the jupyter server (jupyter_token)
        currently we must manually scrape the token from the browser
        """

        self._update_auth_params()

        if isinstance(self.auth, DomoJupyterAuth):
            pass

        elif isinstance(self.auth, DomoFullAuth):
            self.auth = DomoJupyterFullAuth.convert_auth(
                auth=self.auth,
                service_location=self.service_location,
                jupyter_token=jupyter_token,
                service_prefix=self.service_prefix,
            )

        elif isinstance(self.auth, DomoTokenAuth):
            self.auth = DomoJupyterTokenAuth.convert_auth(
                auth=self.auth,
                service_location=self.service_location,
                jupyter_token=jupyter_token,
                service_prefix=self.service_prefix,
            )
        return self.auth

    @classmethod
    def from_dict(
        cls,
        obj,
        auth,
        jupyter_token: str = None,
    ):
        dj_workspace = cls(
            auth=auth,
            id=obj["id"],
            name=obj["name"],
            description=obj["description"],
            created_dt=obj["created"],
            updated_dt=obj["updated"],
            last_run_dt=obj.get("lastRun"),
            instances=obj["instances"],
            owner=obj["owner"],
            memory=obj["memory"],
            cpu=obj["cpu"],
            fileshare_configuration=obj["collectionConfiguration"],
            raw=obj,
        )

        if jupyter_token:
            dj_workspace.update_auth_to_jupyter_auth(jupyter_token=jupyter_token)

        return dj_workspace

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "memory": int(self.memory),
            "cpu": self.cpu,
            "inputConfiguration": [
                confg.to_dict() for confg in self.input_configuration or []
            ],
            "outputConfiguration": [
                confg.to_dict() for confg in self.output_configuration or []
            ],
            "accountConfiguration": [
                confg.to_api() for confg in self.account_configuration or []
            ],
            "fileshareConfiguration": self.collection_configuration or [],
        }

    @classmethod
    async def get_by_id(
        cls,
        workspace_id,
        auth: DomoAuth,  # this API does not require the jupyter_token, but activities inside the workspace will require additional authentication
        jupyter_token=None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        is_get_config_entities: bool = True,
        is_use_default_account_class: bool = False,
        is_suppress_errors: bool = False,
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

        res = await jupyter_routes.get_jupyter_workspace_by_id(
            workspace_id=workspace_id,
            auth=auth,
            context=context,
        )

        if return_raw:
            return res

        djw = cls.from_dict(
            auth=auth,
            obj=res.response,
            jupyter_token=jupyter_token,
        )

        if not is_get_config_entities:
            return djw

        # Load configurations asynchronously
        await djw.get_output_configuration(
            context=context,
            is_suppress_errors=is_suppress_errors,
            is_use_default_account_class=is_use_default_account_class,
        )
        await djw.get_input_configuration(
            context=context,
            is_suppress_errors=is_suppress_errors,
        )
        await djw.get_account_configuration(
            context=context,
            is_suppress_errors=is_suppress_errors,
            is_use_default_account_class=is_use_default_account_class,
        )

        return djw

    async def get_entity_by_id(self, entity_id: str, **kwargs) -> DomoJupyterWorkspace:
        return await self.get_by_id(workspace_id=entity_id, auth=self.auth, **kwargs)

    @classmethod
    async def get_current_workspace(
        cls,
        auth: DomoJupyterAuth,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
    ):
        workspace_id = os.getenv("DOMO_WORKSPACE_ID")

        if not workspace_id:
            raise DJW_Search_Error(
                cls=cls,
                message=f"workspace id {workspace_id} not found.  This only works in Domo's Jupyter Workspaces environment",
            )

        return await cls.get_by_id(
            workspace_id=workspace_id, auth=auth, context=context
        )

    async def get_account_configuration(
        self: DomoJupyterWorkspace,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        is_suppress_errors: bool = False,
        is_use_default_account_class: bool = False,
    ):
        """Load account configuration from raw data."""
        if self.raw.get("accountConfiguration"):
            from ...base.exceptions import DomoError
            from ...routes.account.exceptions import AccountNoMatchError
            from .. import DomoAccount as dmac

            # Fetch accounts first
            async def fetch_account(ac):
                try:
                    return await dmac.DomoAccount.get_by_id(
                        auth=self.auth,
                        account_id=ac["account_id"],
                        is_use_default_account_class=is_use_default_account_class,
                        is_suppress_no_config=is_suppress_errors,
                        session=session,
                        debug_api=debug_api,
                    )
                except (AccountNoMatchError, DomoError):
                    return None

            accounts = await dmce.gather_with_concurrency(
                *[fetch_account(ac) for ac in self.raw["accountConfiguration"]],
                n=10,
            )

            # Create DomoJupyter_Account instances with fetched accounts
            self.account_configuration = [
                DomoJupyter_Account.from_dict(
                    obj=ac,
                    dj_workspace=self,
                    domo_account=account,
                )
                for ac, account in zip(self.raw["accountConfiguration"], accounts)
            ]
        return self.account_configuration

    async def get_input_configuration(
        self: DomoJupyterWorkspace,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        is_suppress_errors: bool = False,
    ):
        """Load input configuration from raw data."""
        if self.raw.get("inputConfiguration"):
            import domolibrary2.routes.dataset as dataset_route

            # Fetch datasets first
            async def fetch_dataset(ic):
                try:
                    return await dmds.DomoDataset.get_by_id(
                        auth=self.auth,
                        dataset_id=ic["dataSourceId"],
                        is_suppress_no_config=is_suppress_errors,
                        session=session,
                        debug_api=debug_api,
                    )
                except dataset_route.DatasetNotFoundError:
                    return None

            datasets = await dmce.gather_with_concurrency(
                *[fetch_dataset(ic) for ic in self.raw["inputConfiguration"]],
                n=10,
            )

            # Create DomoJupyter_DataSource instances with fetched datasets
            self.input_configuration = [
                DomoJupyter_DataSource.from_dict(
                    obj=ic,
                    dj_workspace=self,
                    domo_dataset=dataset,
                )
                for ic, dataset in zip(self.raw["inputConfiguration"], datasets)
            ]
        return self.input_configuration

    async def get_output_configuration(
        self: DomoJupyterWorkspace,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        is_suppress_errors: bool = False,
    ):
        """Load output configuration from raw data."""
        if self.raw.get("outputConfiguration"):
            import domolibrary2.routes.dataset as dataset_route

            # Fetch datasets first
            async def fetch_dataset(oc):
                try:
                    return await dmds.DomoDataset.get_by_id(
                        auth=self.auth,
                        dataset_id=oc["dataSourceId"],
                        is_suppress_no_config=is_suppress_errors,
                        session=session,
                        debug_api=debug_api,
                    )
                except dataset_route.DatasetNotFoundError:
                    return None

            datasets = await dmce.gather_with_concurrency(
                *[fetch_dataset(oc) for oc in self.raw["outputConfiguration"]],
                n=10,
            )

            # Create DomoJupyter_DataSource instances with fetched datasets
            self.output_configuration = [
                DomoJupyter_DataSource.from_dict(
                    obj=oc,
                    dj_workspace=self,
                    domo_dataset=dataset,
                )
                for oc, dataset in zip(self.raw["outputConfiguration"], datasets)
            ]
        return self.output_configuration

    def _add_config(self, config, attribute):
        # print(config.alias)
        config_ls = getattr(self, attribute)

        if config in config_ls:
            for i, ex in enumerate(config_ls):
                if ex == config:
                    config_ls[i] = config

        else:
            config_ls.append(config)

        config_ls.sort()

    def add_config_input_datasource(self, dja_datasource: DomoJupyter_DataSource):
        if not isinstance(dja_datasource, DomoJupyter_DataSource):
            raise DJW_InvalidClass(
                message="must pass instance of DomoJupyter_DataSource",
                cls_instance=self,
            )

        return self._add_config(dja_datasource, attribute="input_configuration")

    def add_config_output_datasource(self, dja_datasource: DomoJupyter_DataSource):
        if not isinstance(dja_datasource, DomoJupyter_DataSource):
            raise DJW_InvalidClass(
                message="must pass instance of DomoJupyter_DataSource",
                cls_instance=self,
            )
        return self._add_config(dja_datasource, attribute="output_configuration")

    def add_config_account(self, dja_account: DomoJupyter_Account):
        if not isinstance(dja_account, DomoJupyter_Account):
            raise DJW_InvalidClass(
                message="must pass instance of DomoJupyter_Account", cls_instance=self
            )
        return self._add_config(dja_account, attribute="account_configuration")

    async def get_content(
        self,
        debug_api: bool = False,
        return_raw: bool = False,
        is_recursive: bool = True,
        content_path: str = "",
        ignore_folders: list[str] = None,
        included_filetypes: list[str] = None,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=2,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await jupyter_routes.get_content(
            auth=self.auth,
            content_path=content_path,
            ignore_folders=ignore_folders,
            included_filetypes=included_filetypes,
            is_recursive=is_recursive,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        self.content = [
            DomoJupyter_Content.from_dict(obj, auth=self.auth) for obj in res.response
        ]
        return self.content

    async def download_workspace_content(
        self,
        base_export_folder=None,
        replace_folder: bool = True,
        ignore_folders: list[str] = None,
        included_filetypes: list[str] = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
    ) -> str:
        """Retrieves content from Domo Jupyter Workspace and downloads to a local folder.

        Args:
            base_export_folder: Base folder path for exports
            replace_folder: Whether to replace existing folder
            ignore_folders: List of folder names to exclude from download
            included_filetypes: List of file extensions to include (e.g., ['.ipynb', '.py', '.md'])
            debug_api: Enable API debugging
            session: Optional httpx client session
        """

        base_export_folder = (
            base_export_folder or f"{self.auth.domo_instance}/{self.name}"
        )

        all_content = await self.get_content(
            ignore_folders=ignore_folders,
            included_filetypes=included_filetypes,
            context=context,
        )
        all_content = [
            content for content in all_content if content.file_type != "directory"
        ]
        defi.upsert_folder(base_export_folder, replace_folder=replace_folder)

        return [
            content.export(default_export_folder=base_export_folder)
            for content in all_content
        ]

    def _test_config_duplicates(self, config_name):
        configuration = getattr(self, config_name)

        if len(set([cfg.alias.lower() for cfg in configuration])) == len(configuration):
            return None

        return f"aliases are not unique for {config_name}"

    async def update_config(
        self,
        config: dict = None,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
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

        config = config or self.to_dict()
        try:
            return await jupyter_routes.update_jupyter_workspace_config(
                auth=self.auth,
                workspace_id=self.id,
                config=config,
                context=context,
            )

        except dmde.DomoError as e:
            print(self._test_config_duplicates("account_configuration"))
            print(self._test_config_duplicates("output_configuration"))
            print(self._test_config_duplicates("input_configuration"))
            raise e from e

    async def add_account(
        self,
        domo_account: dmac.DomoAccount,
        dja_account: Any = None,
        domo_user: dmdu.DomoUser = None,
        is_update_config: bool = True,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
    ):
        if not dja_account and not isinstance(domo_account, dmac.DomoAccount_Default):
            raise DJW_InvalidClass(
                message="must pass domo_account as class DomoAccount", cls_instance=self
            )

        dja_account = dja_account or DomoJupyter_Account(
            alias=domo_account.name, account_id=domo_account.id, dj_workspace=self
        )

        self.add_config_account(dja_account)

        if not is_update_config:
            return self.account_configuration

        retry = 0
        last_error = None

        while retry <= 1:
            try:
                res = await self.update_config(context=context)

                if return_raw:
                    return res

                account_obj = next(
                    obj
                    for obj in res.response["accountConfiguration"]
                    if obj["alias"] == domo_account.name
                )

                return DomoJupyter_Account(
                    account_id=account_obj["account_id"],
                    alias=account_obj["alias"],
                    dj_workspace=self,
                    domo_account=domo_account,
                )

            except JupyterAPI_Error as e:
                last_error = e
                share_user_id = (domo_user and domo_user.id) or (
                    await self.auth.who_am_i()
                ).response["id"]

                await domo_account.Access.share(
                    user_id=share_user_id,
                    debug_api=debug_api,
                    session=session,
                )

                if retry == 1:
                    raise e from e

                retry += 1

        # This should never be reached due to the logic above, but ensures no implicit None return
        raise (
            last_error
            if last_error
            else JupyterAPI_Error(message="Unexpected error in add_account retry loop")
        )

    async def add_input_dataset(
        self,
        domo_dataset: dmds.DomoDataset,
        domojupyter_ds: DomoJupyter_DataSource = None,
        domo_user: dmdu.DomoUser = None,
        is_update_config: bool = True,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
    ):
        """adds a domo_dataset or domojupyter_dataset to workspace and conditionally updates config"""
        if not domojupyter_ds and not isinstance(domo_dataset, dmds.DomoDataset):
            raise DJW_InvalidClass(
                message="must pass domo_dataset as class DomoDataset", cls_instance=self
            )

        if not domojupyter_ds:
            domojupyter_ds = DomoJupyter_DataSource(
                alias=domo_dataset.name, dataset_id=domo_dataset.id, dj_workspace=self
            )

        self.add_config_input_datasource(domojupyter_ds)

        if not is_update_config:
            return self.input_configuration

        retry = 0
        last_error = None

        while retry <= 1:
            try:
                return await self.update_config(context=context)

            except JupyterAPI_Error as e:
                last_error = e
                domo_user = domo_user or await dmdu.DomoUser.get_by_id(
                    auth=self.auth,
                    user_id=(await self.auth.who_am_i()).response["id"],
                    debug_api=debug_api,
                    session=session,
                )

                await domo_dataset.share(
                    member=domo_user,
                    auth=self.auth,
                    debug_api=debug_api,
                    session=session,
                )

                if retry == 1:
                    raise e from e

                retry += 1

        # This should never be reached due to the logic above, but ensures no implicit None return
        raise (
            last_error
            if last_error
            else JupyterAPI_Error(
                message="Unexpected error in add_input_dataset retry loop"
            )
        )

    async def add_output_dataset(
        self,
        domo_dataset: dmds.DomoDataset,
        domojupyter_ds: DomoJupyter_DataSource = None,
        domo_user: dmdu.DomoUser = None,
        is_update_config: bool = True,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
    ):
        if not domojupyter_ds and not isinstance(domo_dataset, dmds.DomoDataset):
            raise DJW_InvalidClass(
                message="must pass domo_dataset as class DomoDataset", cls_instance=self
            )

        domojupyter_ds = domojupyter_ds or DomoJupyter_DataSource(
            alias=domo_dataset.name, dataset_id=domo_dataset.id, dj_workspace=self
        )

        self.add_config_output_datasource(domojupyter_ds)

        if not is_update_config:
            return self.output_configuration

        retry = 0
        last_error = None

        while retry <= 1:
            try:
                return await self.update_config(context=context)

            except JupyterAPI_Error as e:
                last_error = e
                domo_user = domo_user or await dmdu.DomoUser.get_by_id(
                    auth=self.auth,
                    user_id=(await self.auth.who_am_i()).response["id"],
                    debug_api=debug_api,
                    session=session,
                )

                await domo_dataset.share(
                    member=domo_user,
                    auth=self.auth,
                    debug_api=debug_api,
                    session=session,
                )

                if retry == 1:
                    raise e from e

                retry += 1

        # This should never be reached due to the logic above, but ensures no implicit None return
        raise (
            last_error
            if last_error
            else JupyterAPI_Error(
                message="Unexpected error in add_output_dataset retry loop"
            )
        )


@dataclass
class DomoJupyterWorkspaces(DomoManager):
    auth: DomoAuth
    workspaces: list[DomoJupyterWorkspace] = None

    parent: Any = None

    @classmethod
    def from_parent(cls, parent):
        return cls(parent=parent, auth=parent.auth)

    async def get(
        self,
        is_use_default_account_class: bool = False,
        is_suppress_errors: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
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

        res = await jupyter_routes.get_jupyter_workspaces(
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        self.workspaces = await dmce.gather_with_concurrency(
            *[
                DomoJupyterWorkspace.get_by_id(
                    auth=self.auth,
                    workspace_id=workspace["id"],
                    context=context,
                    is_use_default_account_class=is_use_default_account_class,
                    is_suppress_errors=is_suppress_errors,
                )
                for workspace in res.response
            ],
            n=10,
        )

        return self.workspaces

    async def search_workspace_by_name(
        self,
        workspace_name: str,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
        is_use_default_account_class: bool = False,
        is_suppress_errors: bool = False,
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

        res = await self.get(
            context=context,
            return_raw=True,
            is_suppress_errors=is_suppress_errors,
        )

        workspace = next(
            (
                workspace
                for workspace in res.response
                if workspace["name"].lower() == workspace_name.lower()
            ),
            None,
        )

        if not workspace:
            raise DJW_Search_Error(cls_instance=self, search_name=workspace_name)

        if return_raw:
            res.response = workspace
            return res

        return await DomoJupyterWorkspace.get_by_id(
            workspace_id=workspace["id"],
            auth=self.auth,
            context=context,
            is_use_default_account_class=is_use_default_account_class,
            is_suppress_errors=is_suppress_errors,
        )
