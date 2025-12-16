"""Dataset sharing operations."""

from __future__ import annotations

from enum import Enum

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)
from .exceptions import Dataset_GET_Error, ShareDataset_Error


class ShareDataset_AccessLevelEnum(DomoEnumMixin, Enum):
    CO_OWNER = "CO_OWNER"
    CAN_EDIT = "CAN_EDIT"
    CAN_SHARE = "CAN_SHARE"


def generate_share_dataset_payload(
    entity_type: str,  # USER or GROUP
    entity_id: str,
    access_level: ShareDataset_AccessLevelEnum = ShareDataset_AccessLevelEnum.CAN_SHARE,
    is_send_email: bool = False,
) -> dict:
    """Generate payload for sharing a dataset.

    Args:
        entity_type: Type of entity (USER or GROUP)
        entity_id: ID of the user or group
        access_level: Access level (ShareDataset_AccessLevelEnum enum). Defaults to CAN_SHARE.
        is_send_email: Whether to send email notification

    Returns:
        Dictionary payload for dataset sharing API
    """
    return {
        "permissions": [
            {"type": entity_type, "id": entity_id, "accessLevel": access_level.value}
        ],
        "sendEmail": is_send_email,
    }


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def share_dataset(
    auth: DomoAuth,
    dataset_id: str,
    body: dict,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/share"

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        context=context,
    )

    if not res.is_success:
        raise ShareDataset_Error(dataset_id=dataset_id, res=res)

    update_user_ls = [f"{user['type']} - {user['id']}" for user in body["permissions"]]

    res.response = (
        f"updated access list {', '.join(update_user_ls)} added to {dataset_id}"
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
async def get_permissions(
    auth: DomoAuth,
    dataset_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """retrieve the schema for a dataset"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/permissions"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if not res.is_success:
        raise Dataset_GET_Error(dataset_id=dataset_id, res=res)

    return res
