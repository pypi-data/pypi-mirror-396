__all__ = ["DomoJupyter_Content"]


import datetime as dt
import json
import os
from dataclasses import dataclass, field
from typing import Any

import httpx
from dateutil.parser import parse

from ... import auth as dmda
from ...client.context import RouteContext
from ...routes import jupyter as jupyter_routes
from ...utils import DictDot as util_dd


@dataclass
class DomoJupyter_Content:
    name: str
    folder: str
    last_modified: dt.datetime
    file_type: str
    content: str

    auth: dmda.DomoJupyterAuth = field(repr=False)

    default_export_folder: str = "export"

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False

        return self.folder == other.folder and self.name == other.name

    def __post_init__(self):
        dmda.test_is_jupyter_auth(self.auth)

        if self.folder.endswith(self.name):
            self.folder = self.folder.replace(self.name, "")

    @classmethod
    def from_dict(cls, obj: dict[str, Any], auth: dmda.DomoJupyterAuth):
        dd = util_dd.DictDot(obj) if not isinstance(obj, util_dd.DictDot) else obj

        dc = cls(
            name=dd.name,
            folder=dd.path,
            last_modified=parse(dd.last_modified),
            file_type=dd.type,
            auth=auth,
            content=obj.get("content"),
        )

        return dc

    def export(
        self,
        output_folder: str = None,
        file_name: str = None,
        default_export_folder: str = None,
    ):
        if default_export_folder:
            self.default_export_folder = default_export_folder

        output_folder = output_folder or os.path.join(
            self.default_export_folder, self.folder
        )

        file_name = file_name or self.name

        if not os.path.exists(output_folder):
            print(output_folder)
            os.makedirs(output_folder)

        content_str = self.content
        if isinstance(self.content, dict):
            content_str = json.dumps(self.content)

        output_path = os.path.join(output_folder, file_name)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content_str)
            f.close()

        return output_path

    @classmethod
    async def create_content(
        cls,
        auth: dmda.DomoJupyterAuth,
        new_content=None,
        folder_path="",
        debug_api: bool = False,
        return_raw: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
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

        res = await jupyter_routes.create_jupyter_obj(
            auth=auth,
            new_content=new_content,
            content_path=folder_path,
            context=context,
        )

        if return_raw:
            return res

        dj_content = cls.from_dict(auth=auth, obj=res.response)

        if new_content:
            dj_content.content = new_content
            await dj_content.update(context=context)

        return dj_content

    async def update(
        self,
        jupyter_folder: str = None,
        jupyter_file_name: str = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
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

        if jupyter_folder and jupyter_file_name:
            content_path = f"{jupyter_folder}/{jupyter_file_name}"

        if len(self.folder) > 0:
            content_path = f"{self.folder}/{self.name}"

        else:
            content_path = self.name

            if content_path.lower().startswith(self.default_export_folder.lower()):
                content_path = content_path.replace(self.default_export_folder, "")

        content_path = "/".join(os.path.normpath(content_path).split(os.sep))

        return await jupyter_routes.update_jupyter_file(
            auth=self.auth,
            content_path=content_path,
            new_content=self.content,
            context=context,
        )

    async def delete(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
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

        content_path = self.folder + "/" if self.folder else ""
        content_path += self.name

        return await jupyter_routes.delete_jupyter_content(
            auth=self.auth,
            content_path=f"{self.folder}/{self.name}",
            context=context,
        )
