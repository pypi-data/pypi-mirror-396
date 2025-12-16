from __future__ import annotations

from enum import Enum

from ..auth import DomoAuth
from ..base import exceptions as dmde
from ..base.base import DomoEnumMixin
from ..client import (
    get_data as gd,
    response as rgd,
)
from ..client.context import RouteContext
from ..utils import (
    convert as dmcv,
    enums as dmue,
)
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

__all__ = [
    "Group_GET_Error",
    "SearchGroups_Error",
    "search_groups_by_name",
    "get_all_groups",
    "get_group_by_id",
    "Group_CRUD_Error",
    "is_system_groups_visible",
    "toggle_system_group_visibility",
    "GroupType_Enum",
    "generate_body_create_group",
    "create_group",
    "update_group",
    "delete_groups",
    "get_group_owners",
    "get_group_membership",
    "generate_body_update_group_membership",
    "update_group_membership",
    "update_group_members",
    "update_group_owners",
]


class Group_GET_Error(dmde.RouteError):
    def __init__(
        self,
        res: rgd.ResponseGetData,
        message=None,
    ):
        super().__init__(res=res, message=message or res.response)


class SearchGroups_Error(dmde.RouteError):
    def __init__(
        self,
        res: rgd.ResponseGetData,
        message=None,
    ):
        super().__init__(res=res, message=message or res.response)


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_groups_by_name(
    auth: DomoAuth,
    search_name: str,
    is_exact_match: bool = True,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """uses /content/v2/groups/grouplist api -- includes user details"""

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/grouplist?ascending=true&search={search_name}&sort=name "

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )
    if not res.is_success:
        raise Group_GET_Error(res=res)

    if not is_exact_match:
        return res

    match_group = next(
        (group for group in res.response if group.get("name") == search_name), None
    )

    if not match_group:
        raise SearchGroups_Error(
            res=res,
            message=f"There is no exact match for {search_name}",
        )

    res.response = match_group

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_all_groups(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    debug_loop: bool = False,
    return_raw: bool = False,
    maximum=None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """uses /content/v2/groups/grouplist api -- includes user details"""

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/grouplist"

    def arr_fn(res):
        return res.response

    res = await gd.looper(
        offset_params={"offset": "offset", "limit": "limit"},
        arr_fn=arr_fn,
        loop_until_end=True if maximum is None else False,
        limit=30,
        url=url,
        method="GET",
        auth=auth,
        context=context,
        debug_loop=debug_loop,
        return_raw=return_raw,
        maximum=maximum,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Group_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_group_by_id(
    auth: DomoAuth,
    group_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """uses /content/v2/groups/ api -- does not return details"""

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/{group_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if res.status == 404 and res.response == "Not Found":
        raise SearchGroups_Error(
            res=res,
            message=f"group {group_id} not found",
        )

    if not res.is_success:
        raise Group_GET_Error(res=res)

    return res


class Group_CRUD_Error(dmde.RouteError):
    def __init__(self, res: rgd.ResponseGetData, message: str | None = None):
        super().__init__(res=res, message=message or res.response)


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def is_system_groups_visible(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/groups.system.enabled"

    res = await gd.get_data(
        url=url,
        auth=auth,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Group_GET_Error(res=res)

    if res.response.get("value"):
        res.response["value"] = dmcv.convert_string_to_bool(res.response["value"])

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def toggle_system_group_visibility(
    auth: DomoAuth,
    is_hide_system_groups: bool,
    *,
    context: RouteContext | None = None,
    debug_prn: bool = False,
    **context_kwargs,
):
    if debug_prn:
        print(
            f"toggling group visiblity in {auth.domo_instance} {'hiding system groups' if is_hide_system_groups else 'show system groups'}"
        )

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/setVisibility"

    res = await gd.get_data(
        url=url,
        method="POST",
        auth=auth,
        body={"type": "system", "hidden": is_hide_system_groups},
        context=context,
    )

    if not res.is_success:
        raise Group_CRUD_Error(res=res)

    # Build nested context with incremented debug_num_stacks_to_drop
    base_drop = context.debug_num_stacks_to_drop if context else 1
    new_context = RouteContext.build_context(
        context=context,
        debug_num_stacks_to_drop=base_drop + 1,
        **context_kwargs,
    )

    return await is_system_groups_visible(
        auth=auth,
        context=new_context,
    )


class GroupType_Enum(DomoEnumMixin, Enum):
    OPEN = "open"
    ADHOC = "adHoc"
    CLOSED = "closed"
    DIRECTORY = "directory"
    DYNAMIC = "dynamic"
    SYSYTEM = "system"


def generate_body_create_group(
    group_name: str, group_type: str = "open", description: str = ""
) -> dict:
    """Generates the body to create group for content_v2_group API"""
    body = {"name": group_name, "type": group_type, "description": description}

    return body


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_group(
    auth: DomoAuth,
    group_name: str,
    group_type: GroupType_Enum | str = "open",
    description: str = "",
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    # body : {"name": "GROUP_NAME", "type": "open", "description": ""}

    group_type = dmue.normalize_enum(group_type)

    body = generate_body_create_group(
        group_name=group_name, group_type=group_type, description=description
    )
    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        try:
            group_exists = await search_groups_by_name(
                auth=auth, search_name=group_name, is_exact_match=True
            )

            if group_exists.is_success:
                raise Group_CRUD_Error(
                    res=res,
                    message=f"{group_name} already exists. Choose a different group_name",
                )

        except SearchGroups_Error:
            raise Group_CRUD_Error(
                res=res,
                message=res.response,
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
async def update_group(
    auth: DomoAuth,
    group_id: int,
    group_name: str | None = None,
    group_type: str | None = None,
    description: str | None = None,
    additional_params: dict | None = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    group_type = dmue.normalize_enum(group_type)

    s = {"groupId": int(group_id)}

    if group_name:
        s.update({"name": group_name})

    if group_type:
        s.update({"type": group_type})

    if description:
        s.update({"description": description})

    if additional_params and isinstance(additional_params, dict):
        s.update({**additional_params})
        pass

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=[s],
        context=context,
    )

    if group_name and res.status == 400:
        raise Group_CRUD_Error(
            res=res,
            message="are you trying to create an account with a duplicate name?",
        )

    if not res.is_success:
        raise Group_CRUD_Error(
            res=res,
            message=res.response,
        )

    res.response = f"updated {group_id} from {auth.domo_instance}"
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def delete_groups(
    auth: DomoAuth,
    group_ids: list[str],  # list of group_ids
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    group_ids = group_ids if isinstance(group_ids, list) else [str(group_ids)]

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        body=group_ids,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Group_CRUD_Error(
            res=res,
            message=f"failed to delete {', '.join(group_ids)}",
        )

    res.response = f"deleted {', '.join(group_ids)} from {auth.domo_instance}"
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_group_owners(
    auth: DomoAuth,
    group_id: str,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    # maximum: int = None,
    # skip: int = 0,
    # debug_loop: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    # url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/access"
    # url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/users?group={group_id}"
    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/permissions?checkOwnership=true&includeUsers=false"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=[str(group_id)],
        method="POST",
        context=context,
    )

    ## probably not paginated, headers would not make sence when checking owners

    # def arr_fn(res):
    #     return res.response[0].get("permissions").get("owners")

    # res = await gd.looper(
    #     auth=auth,
    #     session=session,
    #     url=url,
    #     offset_params={"offset": "offset", "limit": "limit"},
    #     arr_fn=arr_fn,
    #     loop_until_end=(
    #         True if maximum is None else False
    #     ),  # usually you'll set this to true.  it will override maximum
    #     method="POST",
    #     body=[str(group_id)],
    #     offset_params_in_body=False,
    #     limit=50,
    #     skip=skip,
    #     maximum=maximum,
    #     debug_api=debug_api,
    #     debug_loop=debug_loop,
    #     debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
    #     parent_class=parent_class,
    #     return_raw=return_raw,
    # )

    if return_raw:
        return res

    if not res.is_success:
        raise Group_GET_Error(res=res)

    res.response = res.response[0]["permissions"]["owners"]

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_group_membership(
    auth: DomoAuth,
    group_id: str,
    return_raw: bool = False,
    maximum=None,
    *,
    context: RouteContext | None = None,
    debug_loop: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    # url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/access"
    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/users"

    # res = await gd.get_data(
    #     auth=auth,
    #     url=url,
    #     method="GET",
    #     debug_api=debug_api,
    #     session=session,
    #     parent_class=parent_class,
    #     debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    #     params = {
    #         "offset" : 1,
    #         "limit" : 1
    #     }
    # )
    def arr_fn(res):
        return res.response.get("groupUserList")

    fixed_params = {"group": group_id}

    res = await gd.looper(
        auth=auth,
        url=url,
        fixed_params=fixed_params,
        offset_params={"offset": "offset", "limit": "limit"},
        arr_fn=arr_fn,
        loop_until_end=(
            True if maximum is None else False
        ),  # usually you'll set this to true.  it will override maximum
        maximum=maximum,
        method="GET",
        offset_params_in_body=False,
        limit=500,
        skip=0,
        context=context,
        debug_loop=debug_loop,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Group_GET_Error(res=res)

    return res


def generate_body_update_group_membership(
    group_id: str,
    add_owner_arr: list[str] | None = None,
    remove_owner_arr: list[str] | None = None,
    remove_member_arr: list[str] | None = None,
    add_member_arr: list[str] = None,
) -> list[dict]:
    """
    each member or owner obj should be an object of shape {"type", "id"}
    """
    body = {"groupId": int(group_id)}

    if add_owner_arr and len(add_owner_arr) > 0:
        body.update({"addOwners": add_owner_arr})

    if remove_owner_arr and len(remove_owner_arr) > 0:
        body.update({"removeOwners": remove_owner_arr})

    if remove_member_arr and len(remove_member_arr) > 0:
        body.update({"removeMembers": remove_member_arr})
    if add_member_arr and len(add_member_arr) > 0:
        body.update({"addMembers": add_member_arr})

    return [body]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_group_membership(
    auth: DomoAuth,
    group_id: str,
    update_payload: dict | None = None,
    add_member_arr: list[dict] | None = None,
    remove_member_arr: list[dict] | None = None,
    add_owner_arr: list[dict] = None,
    remove_owner_arr: list[dict] = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    each member or owner obj should be an object of shape {"type", "id"}
    """

    update_payload = update_payload or generate_body_update_group_membership(
        group_id=group_id,
        add_member_arr=add_member_arr,
        remove_member_arr=remove_member_arr,
        add_owner_arr=add_owner_arr,
        remove_owner_arr=remove_owner_arr,
    )

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/access"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=update_payload,
        context=context,
    )

    if not res.is_success:
        raise Group_CRUD_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_group_members(
    auth: DomoAuth,
    group_id: str,
    add_member_arr: list[dict] = None,
    remove_member_arr: list[dict] = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    each member or owner obj should be an object of shape {"type", "id"}
    """

    body = generate_body_update_group_membership(
        group_id=group_id,
        add_member_arr=add_member_arr,
        remove_member_arr=remove_member_arr,
    )

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/access"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if not res.is_success:
        raise Group_CRUD_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_group_owners(
    auth: DomoAuth,
    group_id: str,
    add_owner_arr: list[dict] = None,
    remove_owner_arr: list[dict] = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    each member or owner obj should be an object of shape {"type", "id"}
    """

    body = generate_body_update_group_membership(
        group_id=group_id,
        add_owner_arr=add_owner_arr,
        remove_owner_arr=remove_owner_arr,
    )

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/access"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if not res.is_success:
        raise Group_CRUD_Error(res=res)

    return res
