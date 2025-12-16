from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
)
from ..client.context import RouteContext
from ..client.response import ResponseGetData
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

__all__ = [
    "RoleNotRetrievedError",
    "Role_CRUD_Error",
    "get_roles",
    "get_role_by_id",
    "get_role_grants",
    "get_role_membership",
    "create_role",
    "delete_role",
    "get_default_role",
    "set_default_role",
    "update_role_metadata",
    "set_role_grants",
    "role_membership_add_users",
]


class RoleNotRetrievedError(RouteError):
    def __init__(
        self,
        res: ResponseGetData,
        message=None,
    ):
        super().__init__(res=res, message=message)


# | export
class Role_CRUD_Error(RouteError):
    def __init__(
        self,
        res: ResponseGetData,
        message=None,
    ):
        super().__init__(res=res, message=message)


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_roles(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if not res.is_success:
        raise RoleNotRetrievedError(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_role_by_id(
    auth: DomoAuth,
    role_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if not res.is_success:
        raise RoleNotRetrievedError(
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_role_grants(
    auth: DomoAuth,
    role_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/authorities"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if len(res.response) == 0:
        role_res = await get_roles(auth=auth, context=context)

        domo_role = [role for role in role_res.response if role.get("id") == role_id]

        if not domo_role:
            raise RoleNotRetrievedError(
                res=res,
                message=f"role {role_id} does not exist",
            )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_role_membership(
    auth: DomoAuth,
    role_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/users"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if len(res.response.get("users")) == 0:
        role_res = await get_roles(auth=auth, context=context)

        domo_role = next(
            (role for role in role_res.response if role.get("id") == role_id), None
        )

        if not domo_role:
            raise RoleNotRetrievedError(
                res=res,
                message=f"role {role_id} does not exist or cannot be retrieved",
            )

    if return_raw:
        return res

    res.response = res.response.get("users")

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_role(
    auth: DomoAuth,
    name: str,
    description: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles"

    body = {"name": name, "description": description}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        context=context,
    )

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def delete_role(
    auth: DomoAuth,
    role_id: int,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        context=context,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        print(
            " 😕 weird API issue, but role should have been deleted.  setting is_success = True \n"
        )
        res.is_success = True

    if not res.is_success:
        raise Role_CRUD_Error(
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_default_role(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/user.roleid.default"

    params = {"defaultValue": 2, "ignoreCache": True}

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        params=params,
        context=context,
    )

    if not res.is_success:
        raise RoleNotRetrievedError(res=res)

    res.response = res.response.get("value")

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def set_default_role(
    auth: DomoAuth,
    role_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    # url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/user.roleid.default"
    # body = {"name": "user.roleid.default", "value": role_id}

    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/settings"
    body = {"defaultRoleId": int(role_id), "allowlistRoleIds": None}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_role_metadata(
    auth: DomoAuth,
    role_id: str,
    role_name: str,
    role_description: str | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}"

    body = {"name": role_name, "description": role_description, "id": role_id}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        print(
            " 😕 weird API issue, but role should have been modified.  setting is_success = True \n"
        )
        res.is_success = True

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def set_role_grants(
    auth: DomoAuth,
    role_id: str,
    grants: list[str],
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/authorities"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=grants,
        context=context,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        print(
            " 😕 weird API issue, but role should have been modified.  setting is_success = True \n"
        )
        res.is_success = True

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def role_membership_add_users(
    auth: DomoAuth,
    role_id: str,
    user_ids: list[str],  # list of user ids
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/users"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=user_ids,
        context=context,
    )

    if not res.is_success:
        raise Role_CRUD_Error(res=res)

    return res
