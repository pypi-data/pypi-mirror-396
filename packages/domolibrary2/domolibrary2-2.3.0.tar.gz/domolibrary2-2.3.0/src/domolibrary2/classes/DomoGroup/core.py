from dataclasses import dataclass, field
from typing import Any

from ...auth import DomoAuth
from ...base import exceptions as dmde
from ...base.entities import DomoEntity, DomoManager
from ...base.exceptions import RouteError
from ...client.context import RouteContext
from ...routes import group as group_routes
from ...routes.group import Group_CRUD_Error, GroupType_Enum
from .membership import DomoMembership_Group

__all__ = ["Group_Class_Error", "DomoGroup", "DomoGroups"]


class Group_Class_Error(dmde.ClassError):
    def __init__(
        self, cls_instance, message: str = None, entity_name=None, entity_id: str = None
    ):
        super().__init__(
            cls_instance=cls_instance,
            message=message,
            entity_id=entity_id,
            entity_name=entity_name,
        )


@dataclass(eq=False)
class DomoGroup(DomoEntity):
    id: str

    name: str = None
    type: str = None

    is_system: bool = None

    description: str = None
    members_id_ls: list[str] = field(repr=False, default_factory=list)
    owner_id_ls: list[str] = field(repr=False, default_factory=list)

    members_ls: list[dict] = field(repr=False, default_factory=list)
    owner_ls: list[dict] = field(repr=False, default_factory=list)

    custom_attributes: dict = field(default_factory=dict)

    Membership: DomoMembership_Group = field(repr=False, default=None)

    @property
    def entity_type(self) -> str:
        return "group"

    def __post_init__(self):
        self.Membership = DomoMembership_Group.from_parent(parent=self)

        self.is_system = True if self.type == "system" else False

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]):
        return cls(
            auth=auth,
            id=obj.get("id") or obj.get("groupId"),
            name=obj.get("name"),
            description=obj.get("description"),
            type=obj.get("type") or obj.get("groupType"),
            members_id_ls=obj.get("userIds"),
            owner_ls=obj.get("owners"),
            raw=obj,
        )

    @classmethod
    def _from_grouplist_json(cls, auth: DomoAuth, obj: dict[str, Any]):
        return cls(
            auth=auth,
            id=obj.get("groupId"),
            name=obj.get("name"),
            description=obj.get("description"),
            type=obj.get("groupType"),
            owner_ls=obj.get("owners"),
            owner_id_ls=[owner.id for owner in obj.get("owners", [])],
            members_ls=obj.get("groupMembers", []),
            members_id_ls=[member.id for member in obj.get("groupMembers", [])],
            raw=obj,
        )

    @staticmethod
    def _groups_to_domo_group(json_list, auth: DomoAuth) -> list[dict]:
        domo_groups = [DomoGroup.from_dict(auth=auth, obj=obj) for obj in json_list]

        return domo_groups

    @property
    def display_url(self) -> str:
        """Generate the URL to display this group in the Domo admin interface."""
        return f"https://{self.auth.domo_instance}.domo.com/admin/groups/{self.id}"

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        group_id: str,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await group_routes.get_group_by_id(
            auth=auth,
            group_id=group_id,
            context=context,
        )
        if return_raw:
            return res

        dg = cls.from_dict(auth=auth, obj=res.response)

        # await dg.Membership.get_owners()
        # await dg.Membership.get_members() # disabled because causes recursion

        return dg

    @classmethod
    async def get_entity_by_id(cls, entity_id, **kwargs):
        """
        Internal method to get an entity by ID.
        """
        return await cls.get_by_id(auth=cls.auth, group_id=entity_id, **kwargs)

    @classmethod
    async def create_from_name(
        cls,
        auth: DomoAuth,
        group_name: str = None,
        group_type: GroupType_Enum | str = "open",  # use GroupType_Enum
        description: str = None,
        is_include_manage_groups_role: bool = True,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await group_routes.create_group(
            auth=auth,
            group_name=group_name,
            group_type=group_type,
            description=description,
            context=context,
        )

        domo_group = cls.from_dict(auth=auth, obj=res.response)

        if is_include_manage_groups_role:
            await domo_group.Membership.add_owner_manage_all_groups_role(
                **context_kwargs
            )

        return domo_group

    async def update_metadata(
        self,
        auth: DomoAuth = None,
        group_name: str = None,
        group_type: str = None,  # use GroupType_Enum
        description: str = None,
        additional_params: dict = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = auth or self.auth
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = None
        try:
            res = await group_routes.update_group(
                auth=auth,
                group_id=self.id,
                group_name=group_name,
                group_type=group_type,
                description=description,
                additional_params=additional_params,
                context=context,
            )

            if return_raw:
                return res

            updated_group = await DomoGroup.get_by_id(
                auth=auth, group_id=self.id, context=context
            )

            self.name = updated_group.name or self.name
            self.description = updated_group.description or self.description
            self.type = updated_group.type or self.type

        except Group_CRUD_Error as e:
            if group_type != self.type:
                raise Group_Class_Error(
                    cls_instance=self,
                    entity_name=self.name,
                    entity_id=self.id,
                    message=f"probably cannot change group_type to '{group_type}' from current type '{self.type}' consider passing `addtional_parameters`",
                ) from e

            else:
                raise e from e

        return self

    async def delete(
        self,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await group_routes.delete_groups(
            auth=self.auth,
            group_ids=[str(self.id)],
            context=context,
        )

        res.parent_class = self.__class__.__name__

        return res


@dataclass
class DomoGroups(DomoManager):
    is_hide_system_groups: bool = None

    groups: list[DomoGroup] = None

    @staticmethod
    def _groups_to_domo_group(json_list, auth: DomoAuth):
        return [DomoGroup.from_dict(auth=auth, obj=obj) for obj in json_list]

    async def get_is_system_groups_visible(
        self,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await group_routes.is_system_groups_visible(
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        self.is_hide_system_groups = res.response["value"]

        return self.is_hide_system_groups

    async def toggle_show_system_groups(
        self,
        is_hide_system_groups: bool,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        if self.is_hide_system_groups == is_hide_system_groups:
            return self.is_hide_system_groups

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await group_routes.toggle_system_group_visibility(
            auth=self.auth,
            is_hide_system_groups=is_hide_system_groups,
            context=context,
        )

        if return_raw:
            return res

        self.is_hide_system_groups = not res.response["value"]

        return self.is_hide_system_groups

    async def get(
        self,
        is_hide_system_groups: bool = True,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        await self.toggle_show_system_groups(
            is_hide_system_groups=is_hide_system_groups,
            context=context,
        )

        res = await group_routes.get_all_groups(
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        if len(res.response):
            self.groups = self._groups_to_domo_group(
                json_list=res.response, auth=self.auth
            )

        else:
            self.groups = []

        return self.groups

    async def search_by_name(
        self,
        group_name: list[str],
        is_hide_system_groups: bool = None,
        only_allow_one: bool = True,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> (
        DomoGroup | list[DomoGroup]
    ):  # by default returns one DomoGroup, but can return a list of DomoGroups
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        domo_groups = await self.get(
            is_hide_system_groups=is_hide_system_groups,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return domo_groups

        filter_groups = None
        if isinstance(group_name, str):
            filter_groups = [
                dg for dg in domo_groups if dg.name.lower() == group_name.lower()
            ]

        if isinstance(group_name, list):
            filter_groups = [
                dg
                for dg in domo_groups
                if dg.name.lower() in [gname.lower() for gname in group_name]
            ]

        if not filter_groups:
            raise Group_Class_Error(
                cls_instance=self,
                entity_id=self.auth.domo_instance,
                message=f"{len(domo_groups)} retrieved.  unable to find a group matching {group_name}",
            )

        if only_allow_one:
            return filter_groups[0]

        return filter_groups

    async def upsert(
        self,
        group_name: str,
        group_type: str = None,  # if create_group, use routes.class.GroupType_Enum
        description: str = None,
        additional_params: dict = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        domo_group = None
        try:
            domo_group = await self.search_by_name(
                group_name=group_name, only_allow_one=True, context=context
            )

        except Group_Class_Error:
            return await DomoGroup.create_from_name(
                auth=self.auth,
                group_name=group_name,
                group_type=group_type,
                description=description,
                context=context,
            )

        try:
            await domo_group.update_metadata(
                group_type=group_type,
                description=description,
                context=context,
            )

        except RouteError:
            await group_routes.update_group(
                auth=self.auth,
                group_id=domo_group.id,
                group_name=group_name,
                # group_type=group_type,
                description=description,
                additional_params=additional_params,
                context=context,
            )

        return domo_group
