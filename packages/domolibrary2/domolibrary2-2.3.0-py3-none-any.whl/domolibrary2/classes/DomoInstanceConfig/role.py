__all__ = [
    "DomoRole",
    "SetRoleGrants_MissingGrants",
    "AddUser_Error",
    "DeleteRole_Error",
    "SearchRole_NotFound",
    "DomoRoles",
]


from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoEntity, DomoManager
from ...base.exceptions import ClassError
from ...base.relationships import (
    DomoRelationshipController,
)
from ...client.context import RouteContext
from ...routes import role as role_routes
from ..DomoUser import DomoUser
from .role_grant import DomoGrant


class SetRoleGrants_MissingGrants(ClassError):  # noqa: N801, N818
    def __init__(
        self,
        cls_instance,
        message: str | None = None,
        missing_grants: list[str] | None = None,
    ):
        if missing_grants:
            message = f"role {cls_instance.name} is missing the following grants: {missing_grants}"
        super().__init__(cls_instance=cls_instance, message=message)


class AddUser_Error(ClassError):  # noqa: N801
    def __init__(self, cls_instance, user):
        message = f"user must either be a DomoUser object or provide user_id. received user: {user}, {type(user)}"
        super().__init__(cls_instance=cls_instance, message=message)


class DeleteRole_Error(ClassError):  # noqa: N801
    def __init__(self, cls_instance=None, message: str = "failure to delete role"):
        super().__init__(cls_instance=cls_instance, message=message)


class SearchRole_NotFound(ClassError):  # noqa: N801, N818
    def __init__(self, cls_instance, role_name: str = ""):
        message = f"role {role_name} not found"
        super().__init__(cls_instance=cls_instance, message=message)


@dataclass
class DomoRole(
    DomoRelationshipController,
    DomoEntity,
):
    id: str
    name: str | None = field(default=None)
    description: str | None = field(default=None)
    is_system_role: bool | None = field(default=None)
    is_default_role: bool | None = field(default=None)

    grants: list[Any] = field(default_factory=list)  # Will be DomoGrant objects
    membership: list = field(default_factory=list)

    # def __post_init__(self):
    #     super().__post_init__()

    @property
    def entity_type(self):
        return "ROLE"

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/admin/roles/{self.id}?tab=grants"

    def __post_init__(self):
        self.is_system_role = True if int(self.id or 0) <= 5 else False

        if self.grants:
            self.grants = self._valid_grants(self.grants)

    def _valid_grants(self, grants) -> list[Any]:
        """Convert grant strings or objects to DomoGrant objects."""

        if not grants:
            return []

        if isinstance(grants[0], str):
            return [DomoGrant(grant_str) for grant_str in grants]
        elif (
            hasattr(grants[0], "__class__")
            and grants[0].__class__.__name__ == "DomoGrant"
        ):
            return grants
        else:
            return []

    @classmethod
    def from_dict(
        cls, auth: DomoAuth, obj: dict[str, Any], is_default_role: bool | None = None
    ):
        return cls(
            auth=auth,
            id=obj.get("id", ""),
            name=obj.get("name"),
            description=obj.get("description"),
            is_system_role=obj.get("is_system_role", False),
            is_default_role=is_default_role,
            grants=obj.get("grants", []),
            raw=obj,
        )

    @classmethod
    async def get_entity_by_id(cls, entity_id, auth, **kwargs):
        return await cls.get_by_id(
            auth=auth,
            role_id=entity_id,
            **kwargs,
        )

    async def get():
        raise NotImplementedError("Subclasses must implement get method.")

    async def add_relationship(self):
        raise NotImplementedError("Subclasses must implement add_relationship method.")

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        role_id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
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

        res = await role_routes.get_role_by_id(
            auth=auth,
            role_id=role_id,
            context=context,
        )

        return cls.from_dict(obj=res.response, auth=auth)

    async def update(
        self,
        name=None,
        description: str | None = None,
        grants: list["DomoGrant"] | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
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

        name = name or self.name
        description = description or self.description

        res = await role_routes.update_role_metadata(
            role_id=self.id,
            role_name=name,
            role_description=description,
            auth=self.auth,
            context=context,
        )

        self.name = name
        self.description = description

        if grants:
            await self.set_grants(grants=grants, context=context)

        if return_raw:
            return res

        return self

    async def get_grants(
        self,
        auth: DomoAuth,
        role_id: str | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[DomoGrant]:
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await role_routes.get_role_grants(
            auth=auth,
            role_id=role_id or self.id,
            context=context,
        )

        self.grants = [DomoGrant(obj) for obj in res.response]

        return self.grants

    async def set_grants(
        self,
        grants: list[DomoGrant],
        role_id: str | None = None,
        is_replace: bool = True,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=False,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        all_grants = await self.get_grants(
            role_id=role_id or self.id,
            auth=self.auth,
            context=context,
        )

        all_grants_str = [g.id for g in all_grants]

        missing_grants = [g for g in grants if g.id not in all_grants_str]

        if missing_grants:
            raise SetRoleGrants_MissingGrants(
                cls_instance=self, missing_grants=[g.id for g in missing_grants]
            )

        res = await role_routes.set_role_grants(
            auth=self.auth,
            role_id=role_id or self.id,
            grants=[g.id for g in grants],
            is_replace=is_replace,
            context=context,
        )

        return res

    async def add_user(
        self,
        auth: DomoAuth,
        user_id: str | None = None,
        user: DomoUser | None = None,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=False,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if user_id is None:
            if isinstance(user, DomoUser):
                user_id = user.id
            else:
                raise ValueError("must either provide a user_id or user : DomoUser")

        res = await role_routes.role_membership_add_users(
            auth=auth,
            role_id=self.id,
            user_ids=[user_id],
            context=context,
        )

        self.membership.append(user_id)

        return res

    async def set_as_default_role(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
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

        return await role_routes.set_default_role(
            auth=self.auth,
            role_id=self.id,
            context=context,
        )

    @classmethod
    async def create(
        cls,
        auth: DomoAuth,
        name: str,
        description,
        grants: list[DomoGrant],
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
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

        res = await role_routes.create_role(
            auth=auth,
            name=name,
            description=description,
            context=context,
        )

        if return_raw:
            return res

        domo_role = cls.from_dict(obj=res.response, auth=auth)

        if grants:
            await domo_role.set_grants(grants=grants, context=context)

        return domo_role

    async def get_membership(
        self,
        role_id=None,
        auth: DomoAuth | None = None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop=2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        from .. import DomoUser

        auth = auth or self.auth
        role_id = role_id or self.id

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await role_routes.get_role_membership(
            auth=auth,
            role_id=role_id,
            context=context,
        )

        if return_raw:
            return res.response

        self.membership = [
            DomoUser.from_dict(obj=obj, auth=auth) for obj in res.response
        ]
        return self.membership

    async def delete(
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

        return await role_routes.delete_role(
            role_id=self.id,
            auth=self.auth,
            context=context,
        )


@dataclass
class DomoRoles(DomoManager):
    default_role: DomoRole | None = None
    roles: list[DomoRole] | None = field(default=None)

    async def get(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[DomoRole]:
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await role_routes.get_roles(
            auth=self.auth,
            context=context,
        )

        self.roles = [
            DomoRole.from_dict(obj=obj, auth=self.auth) for obj in res.response
        ]
        return self.roles

    async def by_name(
        self,
        search_name: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        is_suppress_error: bool = False,
        debug_num_stacks_to_drop: int = 3,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> DomoRole:
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        await self.get(
            context=context,
        )

        match_role = (
            next(
                (
                    r
                    for r in self.roles
                    if r.name and search_name.lower() in r.name.lower()
                ),
                None,
            )
            if self.roles
            else None
        )

        if not match_role or not match_role.name and not is_suppress_error:
            raise SearchRole_NotFound(cls_instance=self, role_name=search_name)

        return match_role

    async def upsert(
        self,
        name: str,
        description: str | None = None,
        grants: list["DomoGrant"] | None = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_prn: bool = False,
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

        domo_role = None
        try:
            domo_role = await self.by_name(
                search_name=name,
                context=context,
            )

            if debug_prn:
                print(f"updating role {name}")

            await domo_role.update(
                description=description,
                context=context,
            )

            if grants:
                await domo_role.set_grants(
                    grants=grants,
                    context=context,
                )

        except SearchRole_NotFound:
            if debug_prn:
                print(f"Creating - {name}")

            domo_role = await DomoRole.create(
                name=name,
                description=description,
                auth=self.auth,
                grants=grants or [],
                context=context,
            )

        await self.get(context=context)

        return domo_role

    async def get_default_role(
        self,
        debug_api=False,
        session=None,
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

        # First get the default role ID
        res = await role_routes.get_default_role(
            auth=self.auth,
            context=context,
        )

        # res.response is the role ID, now get the full role details
        default_role_id = res.response

        # Get the full role object by ID
        self.default_role = await DomoRole.get_by_id(
            auth=self.auth,
            role_id=default_role_id,
            context=context,
        )

        return self.default_role
