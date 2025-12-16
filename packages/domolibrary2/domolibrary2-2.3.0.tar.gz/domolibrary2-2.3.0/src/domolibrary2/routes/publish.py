from ..auth import DomoAuth
from ..base import exceptions as de
from ..client import (
    get_data as gd,
    response as rgd,
)
from ..client.context import RouteContext
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

__all__ = [
    "GET_Publish_Error",
    "CRUD_Publish_Error",
    "search_publications",
    "get_publication_by_id",
    "get_subscription_by_id",
    "generate_publish_body",
    "create_publish_job",
    "update_publish_job",
    "get_publish_subscriptions",
    "get_subscription_summaries",
    "get_subscriber_content_details",
    "get_subscription_invitations",
    "get_subscriber_domains",
    "add_subscriber_domain",
    "accept_invite_by_id",
    "accept_invite_by_id_v2",
    "refresh_publish_jobs",
]


class GET_Publish_Error(de.RouteError):
    def __init__(self, res: rgd.ResponseGetData, message: str | None = None):
        super().__init__(res=res, message=message)


class CRUD_Publish_Error(de.RouteError):
    def __init__(self, res: rgd.ResponseGetData, message: str | None = None):
        super().__init__(res=res, message=message)


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_publications(
    auth: DomoAuth,
    search_term: str | None = None,
    limit: int = 100,
    offset: int = 0,
    debug_loop: bool = False,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication/summaries"

    offset_params = {"limit": "limit", "offset": "offset"}

    params = {}
    if search_term:
        params.update({"searchTerm": search_term})

    def arr_fn(res: rgd.ResponseGetData):
        return res.response

    res = await gd.looper(
        auth=auth,
        method="GET",
        limit=limit,
        skip=offset,
        arr_fn=arr_fn,
        fixed_params=params,
        offset_params=offset_params,
        loop_until_end=True,
        debug_loop=debug_loop,
        url=url,
        context=context,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GET_Publish_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_publication_by_id(
    auth: DomoAuth,
    publication_id: str,
    timeout=10,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication/{publication_id}"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        timeout=timeout,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GET_Publish_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_subscription_by_id(
    auth: DomoAuth,
    subscription_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieves a subscription by its ID"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/subscription/{subscription_id}"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GET_Publish_Error(res)

    return res


# generate publish body


def generate_publish_body(
    url: str,
    sub_domain_ls: list[str],
    content_ls: list[str],
    name: str,
    description: str,
    unique_id: str,
    is_new: bool,
) -> dict:
    if not sub_domain_ls:
        sub_domain_ls = []

    if not content_ls:
        content_ls = []

    body = {
        "id": unique_id,
        "name": name,
        "description": description,
        "domain": url,
        "content": content_ls,
        "subscriberDomain": sub_domain_ls,
        "new": str(is_new).lower(),
    }

    return body


# Creating publish job for a specific subscriber
@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_publish_job(
    auth: DomoAuth,
    body: dict,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication"

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CRUD_Publish_Error(res)

    return res


# Updating existing publish job with content
@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_publish_job(
    auth: DomoAuth,
    publication_id: str,
    body: dict,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication/{publication_id}"

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CRUD_Publish_Error(res)
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_publish_subscriptions(
    auth: DomoAuth,
    publish_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """retrieves a summary of existing subscriptions"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publications/summaries/{publish_id}/subscriptions"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GET_Publish_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_subscription_summaries(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """retrieves a summary of existing subscriptions"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/subscription/summaries"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GET_Publish_Error(res)
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_subscriber_content_details(
    auth: DomoAuth,
    publication_id,
    subscriber_instance: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    if not subscriber_instance.endswith(".domo.com"):
        subscriber_instance = f"{subscriber_instance}.domo.com"

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/associations/{publication_id}/subscribers/{subscriber_instance}"

    res = await gd.get_data(
        method="get",
        url=url,
        auth=auth,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GET_Publish_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_subscription_invitations(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """retrieves a list of subscription invitations"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/subscription/invites"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GET_Publish_Error(res)
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_subscriber_domains(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """retrieves a list of subsriber domains"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/proxy_user?parts=SUBSCRIPTION_COUNT"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GET_Publish_Error(res)
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def add_subscriber_domain(
    auth: DomoAuth,
    domain: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """adds subscriber domain to the list"""

    if ".domo.com" not in domain:
        domain = domain + ".domo.com"
    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/proxy_user/domain/{domain}/"
    body = {"tenantId": domain}
    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body=body,
        context=context,
    )

    if not res.is_success:
        raise GET_Publish_Error(res)
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def accept_invite_by_id(
    auth: DomoAuth,
    subscription_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """this takes get_subscription_invites_list into account and accepts - not instant"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/subscription/{subscription_id}"

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        context=context,
    )

    if not res.is_success:
        raise CRUD_Publish_Error(res)
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def accept_invite_by_id_v2(
    auth: DomoAuth,
    publication_id: str,
    owner_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """this takes get_subscription_invites_list into account and accepts - not instant"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/subscriptions/v2"

    body = {
        "publicationId": publication_id,
        "customerId": "",
        "domain": "",
        "groupIds": [],
        "userId": owner_id,
        "userIds": [],
    }

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        context=context,
    )

    if not res.is_success:
        raise CRUD_Publish_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def refresh_publish_jobs(
    auth: DomoAuth,
    publish_ids: list,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Refreshing list of publish jobs. Typically "instance" = publisher instance"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication/refresh"

    body = {"publicationIds": publish_ids}

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body=body,
        context=context,
    )

    if not res.is_success:
        raise CRUD_Publish_Error(res)

    return res
