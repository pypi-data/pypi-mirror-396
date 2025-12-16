"""DomoAccess re-export for DomoAccount package.

This module re-exports DomoAccess classes from the subentity package
to resolve import dependencies within the DomoAccount package.
"""

from dataclasses import dataclass, field

from ...client.context import RouteContext
from ...client.response import ResponseGetData
from ...routes import account as account_routes
from ...routes.account import (
    ShareAccount,
    ShareAccount_AccessLevel,
    ShareAccount_V1_AccessLevel,
)
from ...utils import chunk_execution as dmce
from ..subentity.access import AccessRelationship, DomoAccess


@dataclass
class Account_AccessRelationship(AccessRelationship):
    def __repr__(self) -> str:
        return f"{super().__repr__()}, relationship_type={self.relationship_type!r}, entity_id={self.entity_id!r}, entity_type={self.entity_type!r}, entity_name={self.entity_name!r}"

    @property
    def entity_id(self) -> str:
        return self.entity.id

    @property
    def entity_type(self) -> str:
        return self.entity.entity_type

    @property
    def entity_name(self) -> str | None:
        return (
            getattr(self.entity, "email_address", None)
            or getattr(self.entity, "name", None)
            or getattr(self.entity, "display_name", None)
        )

    def to_dict(self) -> dict[str, str]:
        return {"id": self.entity.id, "type": self.entity.entity_type}

    async def update(self) -> None:
        raise NotImplementedError("DomoAccount_Access.update not implemented")

    @classmethod
    async def from_user_id(
        cls,
        parent_entity,
        user_id,
        auth,
        access_level,
        suppress_no_results_error: bool = True,
        *,
        context: RouteContext | None = None,
    ):
        from ...routes.user.exceptions import SearchUserNotFoundError
        from ..DomoUser import DomoUser

        try:
            user = await DomoUser.get_by_id(auth=auth, user_id=user_id, context=context)
            return cls(
                entity=user,
                relationship_type=access_level,
                parent_entity=parent_entity,
            )
        except SearchUserNotFoundError:
            if suppress_no_results_error:
                # User no longer exists, return None
                return None
            raise

    @classmethod
    async def from_group_id(
        cls,
        parent_entity,
        group_id,
        auth,
        access_level,
        suppress_no_results_error: bool = True,
        *,
        context: RouteContext | None = None,
    ):
        from ...routes.group import SearchGroups_Error
        from ..DomoGroup.core import DomoGroup

        try:
            group = await DomoGroup.get_by_id(
                auth=auth, group_id=group_id, context=context
            )
            return cls(
                entity=group,
                relationship_type=access_level,
                parent_entity=parent_entity,
            )
        except SearchGroups_Error:
            if suppress_no_results_error:
                # Group no longer exists, return None
                return None
            raise

    @classmethod
    async def from_entity_id(
        cls,
        parent_entity,
        entity_id,
        auth,
        access_level,
        entity_type,
        suppress_no_results_error: bool = True,
        *,
        context: RouteContext | None = None,
    ):
        if entity_type == "USER":
            return await cls.from_user_id(
                parent_entity,
                entity_id,
                auth,
                access_level,
                suppress_no_results_error,
                context=context,
            )
        elif entity_type == "GROUP":
            return await cls.from_group_id(
                parent_entity,
                entity_id,
                auth,
                access_level,
                suppress_no_results_error,
                context=context,
            )
        else:
            raise ValueError(f"Unknown entity_type: {entity_type}")


@dataclass
class DomoAccess_Account(DomoAccess):
    """
    Account access management with unified access control integration.

    This class provides backward compatibility while integrating with
    the new unified access control system. Use get_unified_access_summary()
    for access to the standardized access control interface.
    """

    version: int = None  # api version - aligns to feature switch

    share_enum: ShareAccount = field(default=ShareAccount_AccessLevel)

    def __post_init__(self):
        super().__post_init__()

        if isinstance(self.share_enum, ShareAccount_AccessLevel):
            self.version = 2
        elif isinstance(self.share_enum, ShareAccount_V1_AccessLevel):
            self.version = 1

        return True

    async def get(
        self,
        return_raw: bool = False,
        suppress_no_results_error: bool = True,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Get account access list.

        Args:
            return_raw: Return raw API response without processing
            suppress_no_results_error: If True, skip users/groups that don't exist; if False, raise error
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, debug_num_stacks_to_drop, etc.)

        Returns:
            List of Account_AccessRelationship objects
        """
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await account_routes.get_account_accesslist(
            auth=self.auth,
            account_id=self.parent_id,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        self.relationships = [
            rel
            for rel in await dmce.gather_with_concurrency(
                *[
                    Account_AccessRelationship.from_entity_id(
                        parent_entity=self.parent,
                        entity_id=obj["id"],
                        auth=self.auth,
                        access_level=obj["accessLevel"],
                        entity_type=obj["type"],
                        suppress_no_results_error=suppress_no_results_error,
                        context=context,
                    )
                    for obj in res.response
                ],
                n=10,
            )
            if rel is not None  # Filter out users/groups that no longer exist
        ]

        return self.relationships

    async def add_share(
        self,
        entity,
        access_level=None,
        user_id: int = None,
        group_id: int = None,
        use_v1_api: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> Account_AccessRelationship:
        """Share this account with a user or group.

        Can be called in two ways:
        1. Pass an entity object (DomoUser or DomoGroup) with access_level
        2. Pass user_id or group_id with access_level

        Args:
            entity: DomoUser or DomoGroup object (optional if user_id/group_id provided)
            access_level: Access level enum or string (defaults to self.share_enum.CAN_VIEW)
            user_id: User ID to share with (optional)
            group_id: Group ID to share with (optional)
            use_v1_api: Force v1 API usage (ignored if group_id provided)
            return_raw: Return raw response without processing
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, etc.)

        Returns:
            Account_AccessRelationship instance representing the new share relationship
            (or ResponseGetData if return_raw=True)

        Raises:
            ValueError: If neither entity nor user_id/group_id provided
            Account_Share_Error: If sharing operation fails

        Examples:
            >>> # Share with DomoUser entity
            >>> user = await DomoUser.get_by_id(auth=auth, user_id=456)
            >>> relationship = await account.Access.add_share(
            ...     entity=user,
            ...     access_level=ShareAccount_AccessLevel.CAN_VIEW
            ... )
            >>> print(relationship.entity_id)  # 456

            >>> # Share with group by ID
            >>> relationship = await account.Access.add_share(
            ...     group_id=789,
            ...     access_level=ShareAccount_AccessLevel.CAN_EDIT
            ... )
            >>> print(relationship.entity_type)  # GROUP
        """
        # Extract IDs from entity if provided
        if entity:
            if hasattr(entity, "entity_type"):
                if entity.entity_type.upper() == "USER":
                    user_id = entity.id
                elif entity.entity_type.upper() == "GROUP":
                    group_id = entity.id
            else:
                # Try to infer from class name
                class_name = entity.__class__.__name__
                if "USER" in class_name.upper():
                    user_id = entity.id
                elif "GROUP" in class_name.upper():
                    group_id = entity.id

        # Determine entity type and ID
        if user_id:
            entity_type = "USER"
            entity_id = user_id
        elif group_id:
            entity_type = "GROUP"
            entity_id = group_id
        else:
            raise ValueError("Must provide either entity, user_id, or group_id")

        # Set default access level
        if not access_level:
            access_level = self.share_enum.CAN_VIEW

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        # Call the route function
        res = await account_routes.share_account(
            auth=self.auth,
            account_id=self.parent.id,
            access_level=access_level,
            user_id=user_id,
            group_id=group_id,
            use_v1_api=use_v1_api,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        # Create and return the relationship instance for the shared entity
        relationship = await Account_AccessRelationship.from_entity_id(
            parent_entity=self.parent,
            entity_id=entity_id,
            auth=self.auth,
            access_level=access_level,
            entity_type=entity_type,
            context=context,
        )

        # Optionally refresh the full access list to keep it in sync
        await self.get(context=context)

        return relationship

    async def remove_share(
        self,
        entity=None,
        user_id: int = None,
        group_id: int = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> ResponseGetData:
        """Remove account sharing for a user or group.

        Can be called in two ways:
        1. Pass an entity object (DomoUser or DomoGroup)
        2. Pass user_id or group_id

        Args:
            entity: DomoUser or DomoGroup object (optional if user_id/group_id provided)
            user_id: User ID to remove (optional)
            group_id: Group ID to remove (optional)
            return_raw: Return raw response without processing
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, etc.)

        Returns:
            ResponseGetData if return_raw=True, else refreshed relationships

        Raises:
            ValueError: If neither entity nor user_id/group_id provided
            Account_Share_Error: If remove operation fails

        Examples:
            >>> # Remove share for DomoUser entity
            >>> user = await DomoUser.get_by_id(auth=auth, user_id=456)
            >>> await account.Access.remove_share(entity=user)

            >>> # Remove share by group ID
            >>> await account.Access.remove_share(group_id=789)
        """
        # Extract IDs from entity if provided
        if entity:
            if hasattr(entity, "entity_type"):
                if entity.entity_type.upper() == "USER":
                    user_id = entity.id
                elif entity.entity_type.upper() == "GROUP":
                    group_id = entity.id
            else:
                # Try to infer from class name
                class_name = entity.__class__.__name__
                if "USER" in class_name.upper():
                    user_id = entity.id
                elif "GROUP" in class_name.upper():
                    group_id = entity.id

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        # Share with NO_ACCESS to remove
        res = await account_routes.share_account(
            auth=self.auth,
            account_id=self.parent_id,
            access_level=ShareAccount_AccessLevel.NO_ACCESS,
            user_id=user_id,
            group_id=group_id,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        # Refresh access list after removing
        return await self.get(context=context)


@dataclass
class DomoAccess_OAuth(DomoAccess_Account):
    share_enum: ShareAccount = field(repr=False, default=ShareAccount_AccessLevel)

    async def get(
        self,
        return_raw: bool = False,
        suppress_no_results_error: bool = True,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Get OAuth account access list.

        Args:
            return_raw: Return raw API response without processing
            suppress_no_results_error: If True, skip users/groups that don't exist; if False, raise error
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, debug_num_stacks_to_drop, etc.)

        Returns:
            List of Account_AccessRelationship objects
        """
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await account_routes.get_oauth_account_accesslist(
            auth=self.auth,
            account_id=self.parent_id,
            context=context,
        )

        if return_raw:
            return res

        # Process response and filter out deleted users/groups
        self.relationships = [
            rel
            for rel in await dmce.gather_with_concurrency(
                *[
                    Account_AccessRelationship.from_entity_id(
                        parent_entity=self.parent,
                        entity_id=obj["id"],
                        auth=self.auth,
                        access_level=obj["accessLevel"],
                        entity_type=obj["type"],
                        suppress_no_results_error=suppress_no_results_error,
                        context=context,
                    )
                    for obj in res.response
                ],
                n=10,
            )
            if rel is not None  # Filter out users/groups that no longer exist
        ]

        return self.relationships

    async def add_share(
        self,
        entity,
        access_level=None,
        user_id: int = None,
        group_id: int = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> Account_AccessRelationship:
        """Share this OAuth account with a user or group.

        Args:
            entity: DomoUser or DomoGroup object (optional if user_id/group_id provided)
            access_level: Access level enum or string (defaults to self.share_enum.CAN_VIEW)
            user_id: User ID to share with (optional)
            group_id: Group ID to share with (optional)
            return_raw: Return raw response without processing
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, etc.)

        Returns:
            Account_AccessRelationship instance representing the new share relationship
            (or ResponseGetData if return_raw=True)

        Examples:
            >>> # Share OAuth account with user
            >>> relationship = await oauth_account.Access.add_share(
            ...     user_id=456,
            ...     access_level=ShareAccount_AccessLevel.CAN_VIEW
            ... )
            >>> print(relationship.entity_id)  # 456
        """
        # Extract IDs from entity if provided
        if entity:
            if hasattr(entity, "entity_type"):
                if entity.entity_type == "USER":
                    user_id = entity.id
                elif entity.entity_type == "GROUP":
                    group_id = entity.id
            else:
                class_name = entity.__class__.__name__
                if "User" in class_name:
                    user_id = entity.id
                elif "Group" in class_name:
                    group_id = entity.id

        # Determine entity type and ID
        if user_id:
            entity_type = "USER"
            entity_id = user_id
        elif group_id:
            entity_type = "GROUP"
            entity_id = group_id
        else:
            raise ValueError("Must provide either entity, user_id, or group_id")

        # Set default access level
        if not access_level:
            access_level = self.share_enum.CAN_VIEW

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        # Call the OAuth-specific route function
        res = await account_routes.share_oauth_account(
            auth=self.auth,
            account_id=self.parent_id,
            access_level=access_level,
            user_id=user_id,
            group_id=group_id,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        # Create and return the relationship instance for the shared entity
        relationship = await Account_AccessRelationship.from_entity_id(
            parent_entity=self.parent,
            entity_id=entity_id,
            auth=self.auth,
            access_level=access_level,
            entity_type=entity_type,
            context=context,
        )

        # Optionally refresh the full access list to keep it in sync
        await self.get(context=context)

        return relationship

    async def remove_share(
        self,
        entity=None,
        user_id: int = None,
        group_id: int = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> ResponseGetData:
        """Remove OAuth account sharing for a user or group.

        Args:
            entity: DomoUser or DomoGroup object (optional if user_id/group_id provided)
            user_id: User ID to remove (optional)
            group_id: Group ID to remove (optional)
            return_raw: Return raw response without processing
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, etc.)

        Returns:
            ResponseGetData if return_raw=True, else refreshed relationships

        Examples:
            >>> # Remove OAuth account share
            >>> await oauth_account.Access.remove_share(user_id=456)
        """
        # Extract IDs from entity if provided
        if entity:
            if hasattr(entity, "entity_type"):
                if entity.entity_type == "USER":
                    user_id = entity.id
                elif entity.entity_type == "GROUP":
                    group_id = entity.id
            else:
                class_name = entity.__class__.__name__
                if "User" in class_name:
                    user_id = entity.id
                elif "Group" in class_name:
                    group_id = entity.id

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        # Share with NO_ACCESS to remove
        res = await account_routes.share_oauth_account(
            auth=self.auth,
            account_id=self.parent_id,
            access_level=ShareAccount_AccessLevel.NO_ACCESS,
            user_id=user_id,
            group_id=group_id,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        # Refresh access list after removing
        return await self.get(context=context)


__all__ = ["DomoAccess_Account", "DomoAccess_OAuth", "Account_AccessRelationship"]
