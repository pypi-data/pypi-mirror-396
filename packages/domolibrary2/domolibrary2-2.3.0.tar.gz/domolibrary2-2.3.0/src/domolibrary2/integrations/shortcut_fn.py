"""Fill in a module description here"""

__all__ = ["share_domo_account_with_domo_group"]


from ..auth import DomoAuth
from ..classes import (
    DomoAccount as dmacc,
)
from ..classes.DomoGroup import core as dmdg


async def share_domo_account_with_domo_group(
    auth: DomoAuth,
    account_name: str,
    group_name: str,
    is_upsert_group: bool = False,  # will not attempt to upsert group
    group_description: str = None,
    group_owner_names: list[str] = None,  # will default to ["Role: Admin"]
    group_type: dmdg.GroupType_Enum = dmdg.GroupType_Enum["CLOSED"].value,
    is_search_system_accounts: bool = True,  # will default to True if no group_owner_name
):
    try:
        domo_groups = await dmdg.DomoGroups.by_name(
            auth=auth,
            group_names=[group_name],
            is_search_system_accounts=is_search_system_accounts,
        )

        domo_group = next(
            domo_group for domo_group in domo_groups if domo_group.name == group_name
        )

    except dmdg.SearchGroups_Error:
        is_upsert_group = True

    if is_upsert_group:
        if not group_owner_names:
            is_search_system_accounts = True

        domo_group = await dmdg.DomoGroups.upsert(
            auth=auth,
            group_name=group_name,
            description=group_description,
            group_owner_names=group_owner_names,
            group_type=group_type,
            is_search_system_accounts=is_search_system_accounts,
        )

    domo_accounts = await dmacc.DomoAccounts.get_accounts(
        auth=auth, account_name=account_name
    )

    domo_account = next(acc for acc in domo_accounts if acc.name == account_name)

    return await domo_account.share(group_id=domo_group.id, auth=auth)
