from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ...base.relationships import ShareAccount
from ...client.context import RouteContext
from ...routes import group as group_routes
from ...utils import chunk_execution as dmce
from ..subentity.membership import DomoMembership, MembershipRelationship


@dataclass
class DomoMembership_Group(DomoMembership):
    """
    Group membership management using unified relationship system.

    This class contains the full implementation for managing group membership
    relationships. It uses the relationships property to store all members
    and owners, with calculated properties to filter by type.
    """

    # Relationship management lists for pending operations
    _add_member_ls: list[MembershipRelationship] = field(default_factory=list)
    _remove_member_ls: list[MembershipRelationship] = field(default_factory=list)
    _add_owner_ls: list[MembershipRelationship] = field(default_factory=list)
    _remove_owner_ls: list[MembershipRelationship] = field(default_factory=list)

    async def get_owners(
        self,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[MembershipRelationship]:
        """Get all owner relationships for this group."""
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await group_routes.get_group_owners(
            group_id=self.parent_id,
            auth=self.auth,
            context=context,
        )
        if return_raw:
            return res

        owner_relationships = await self._extract_domo_entities_from_list(
            res.response, relation_type="OWNER", context=context
        )

        # Update relationships list - replace existing owners
        self.relationships = [
            rel
            for rel in self.relationships
            if rel.relationship_type != ShareAccount("OWNER")
        ] + owner_relationships

        return self.owners

    async def get_members(
        self,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[MembershipRelationship]:
        """Get all member relationships for this group."""
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await group_routes.get_group_membership(
            group_id=self.parent_id,
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        member_relationships = await self._extract_domo_entities_from_list(
            res.response, relation_type="MEMBER", context=context
        )

        # Update relationships list - replace existing members
        self.relationships = [
            rel
            for rel in self.relationships
            if rel.relationship_type != ShareAccount("MEMBER")
        ] + member_relationships

        # Update parent entity legacy attributes for backward compatibility
        if self.parent:
            self.parent.members_id_ls = [member.entity.id for member in self.members]
            self.parent.members_ls = [member.entity for member in self.members]

        return self.members

    async def get(
        self, *, context: RouteContext | None = None, **context_kwargs
    ) -> list[MembershipRelationship]:
        """Get all membership relationships for this group."""
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)
        await self.get_owners(context=context)
        await self.get_members(context=context)
        return self.relationships

    async def add_relationship(
        self,
        entity: Any,  # DomoUser, DomoGroup
        relationship_type: ShareAccount,
        is_update: bool = True,
    ) -> list[MembershipRelationship]:
        """Create a new membership relationship for this group."""
        relationship = MembershipRelationship(
            parent_entity=self.parent,
            entity=entity,
            relationship_type=relationship_type,
        )

        self.relationships.append(relationship)

        if is_update:
            await self.update()

        return await self.get()

    async def update(
        self,
        update_payload: dict = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Update group membership with pending changes."""
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await group_routes.update_group_membership(
            auth=self.auth,
            update_payload=update_payload,
            group_id=self.parent_id,
            add_member_arr=self._list_to_dict(self._add_member_ls),
            remove_member_arr=self._list_to_dict(self._remove_member_ls),
            add_owner_arr=self._list_to_dict(self._add_owner_ls),
            remove_owner_arr=self._list_to_dict(self._remove_owner_ls),
            context=context,
        )

        self._reset_obj()

        return res

    # Helper methods for managing pending operations

    def _add_to_list(self, member, list_to_update, relation_type):
        """Add member to pending operations list."""
        if not isinstance(member, MembershipRelationship):
            member_entity = MembershipRelationship(
                parent_entity=self.parent,
                entity=member,
                relationship_type=ShareAccount(relation_type),
            )
        else:
            member_entity = member

        if member_entity not in list_to_update:
            list_to_update.append(member_entity)

    def _add_member(self, member):
        """Add member to pending add list."""
        return self._add_to_list(member, self._add_member_ls, relation_type="MEMBER")

    def _remove_member(self, member, is_keep_system_group=True):
        """Remove member - does not remove system groups by default."""
        from ..DomoGroup import core as dmg

        if (
            is_keep_system_group
            and isinstance(member, dmg.DomoGroup)
            and member.type == "system"
        ):
            return

        return self._add_to_list(member, self._remove_member_ls, relation_type="MEMBER")

    def _add_owner(self, member):
        """Add owner to pending add list."""
        return self._add_to_list(member, self._add_owner_ls, relation_type="OWNER")

    def _remove_owner(self, member, is_keep_system_group=True):
        """Remove owner - does not remove system groups by default."""
        from ..DomoGroup import core as dmg

        if (
            is_keep_system_group
            and isinstance(member, dmg.DomoGroup)
            and member.type == "system"
        ):
            return

        return self._add_to_list(member, self._remove_owner_ls, relation_type="OWNER")

    def _reset_obj(self):
        """Clear all pending operations lists."""
        self._add_member_ls = []
        self._remove_member_ls = []
        self._add_owner_ls = []
        self._remove_owner_ls = []

    async def _extract_domo_groups_from_list(
        self, entity_ls, *, context: RouteContext | None = None, **context_kwargs
    ):
        """Extract DomoGroup objects from API response list."""
        from ..DomoGroup import core as dmg

        return await dmce.gather_with_concurrency(
            *[
                dmg.DomoGroup.get_by_id(
                    group_id=obj.get("groupId") or obj.get("id"),
                    auth=self.auth,
                    context=context,
                )
                for obj in entity_ls
                if obj.get("type") == "GROUP" or obj.get("groupId")
            ],
            n=60,
        )

    async def _extract_domo_users_from_list(
        self, entity_ls, *, context: RouteContext | None = None, **context_kwargs
    ):
        """Extract DomoUser objects from API response list."""
        from .. import DomoUser as dmu

        return await dmce.gather_with_concurrency(
            *[
                dmu.DomoUser.get_by_id(
                    user_id=obj.get("userId") or obj.get("id"),
                    auth=self.auth,
                    context=context,
                )
                for obj in entity_ls
                if obj.get("type") == "USER" or obj.get("userId")
            ],
            n=10,
        )

    async def _extract_domo_entities_from_list(
        self,
        entity_ls,
        relation_type,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[MembershipRelationship]:
        """Extract all entities from API response and create MembershipRelationship objects."""
        domo_groups = await self._extract_domo_groups_from_list(
            entity_ls, context=context
        )
        domo_users = await self._extract_domo_users_from_list(
            entity_ls, context=context
        )

        membership_entities = []
        for entity in domo_groups + domo_users:
            membership_entity = MembershipRelationship(
                parent_entity=self.parent,
                entity=entity,
                relationship_type=ShareAccount(relation_type),
            )
            membership_entities.append(membership_entity)

        return membership_entities

    @staticmethod
    def _list_to_dict(entity_ls):
        """Convert list of MembershipRelationship objects to dict for API."""
        return [rel.to_dict() for rel in entity_ls]

    # High-level convenience methods

    async def add_members(
        self,
        add_user_ls: list[Any],
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Add multiple members to the group."""
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)
        self._reset_obj()

        for domo_user in add_user_ls:
            self._add_member(domo_user)

        res = await self.update(context=context)

        if return_raw:
            return res

        return await self.get_members(context=context)

    async def remove_members(
        self,
        remove_user_ls: list[Any],
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Remove multiple members from the group."""
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)
        self._reset_obj()

        for domo_user in remove_user_ls:
            self._remove_member(domo_user)

        res = await self.update(context=context)

        if return_raw:
            return res

        return await self.get_members(context=context)

    async def set_members(
        self,
        user_ls: list[Any],
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Set the exact member list for the group, removing others."""
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)
        self._reset_obj()

        # Convert users to Membership_Entity instances
        user_entities = []
        for user in user_ls:
            member_entity = MembershipRelationship(
                relationship_type=ShareAccount("MEMBER"),
                parent_entity=self.parent,
                entity=user,
            )
            user_entities.append(member_entity)

        user_ls = user_entities

        memberships = await self.get_members(context=context)

        for domo_user in user_ls:
            self._add_member(domo_user)

        for me in memberships:
            if me not in user_ls:
                self._remove_member(me)

        res = await self.update(context=context)
        if return_raw:
            return res

        return await self.get_members(context=context)

    async def add_owners(
        self,
        add_owner_ls: list[Any],
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Add multiple owners to the group."""
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)
        self._reset_obj()

        for domo_user in add_owner_ls:
            self._add_owner(domo_user)

        res = await self.update(context=context)

        if return_raw:
            return res

        return await self.get_owners(context=context)

    async def remove_owners(
        self,
        remove_owner_ls: list[Any],
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Remove multiple owners from the group."""
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)
        self._reset_obj()

        for domo_user in remove_owner_ls:
            self._remove_owner(domo_user)

        res = await self.update(context=context)

        if return_raw:
            return res

        return await self.get_owners(context=context)

    async def set_owners(
        self,
        owner_ls: list[Any],
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Set the exact owner list for the group, removing others."""
        from ..DomoGroup import core as dmdg

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)
        self._reset_obj()

        # Convert owners to Membership_Entity instances
        [
            MembershipRelationship(
                relationship_type=ShareAccount("OWNER"),
                parent_entity=self.parent,
                entity=owner,
            )
            for owner in owner_ls
        ]

        membership: list[MembershipRelationship] = await self.get_owners(
            context=context
        )

        for domo_entity in owner_ls:
            self._add_owner(domo_entity)

        for oe in membership:
            # open accounts must have themselves as an owner
            if (
                self.parent
                and self.parent == "open"
                and self.parent.id == oe.entity.id
                and isinstance(oe.entity, dmdg.DomoGroup)
            ):
                self._add_owner(oe)
                continue

            if isinstance(oe.entity, dmdg.DomoGroup) and oe.entity.is_system:
                self._add_owner(oe)
                continue

            if oe.entity not in owner_ls:
                self._remove_owner(oe)

        res = await self.update(context=context)

        if return_raw:
            return res

        return await self.get_owners(context=context)

    async def add_owner_manage_all_groups_role(
        self,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Add the Grant: Manage all groups role as an owner."""
        from ..DomoGroup import core as dmg

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)
        domo_groups = dmg.DomoGroups(auth=self.auth)

        grant_group = await domo_groups.search_by_name(
            group_name="Grant: Manage all groups",
            is_hide_system_groups=False,
            context=context,
        )

        await self.add_owners(add_owner_ls=[grant_group], context=context)

        return await self.get_owners(context=context)
