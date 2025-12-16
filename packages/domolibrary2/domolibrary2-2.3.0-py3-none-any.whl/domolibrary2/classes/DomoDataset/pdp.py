"""
PDP (Personalized Data Permissions) system using the unified entities architecture.

This module reimagines PDP policies as entities with proper relationships,
using DomoEnum for operators and the relationship system for user/group associations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from domolibrary2.base.base import DomoEnumMixin
from domolibrary2.base.entities import DomoEntity, DomoSubEntity
from domolibrary2.base.relationships import (
    DomoRelationship,
    DomoRelationshipController,
    ShareAccount,
)


class PDPOperator(DomoEnumMixin, Enum):
    """Operators available for PDP policy parameters."""

    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN_EQUAL = "GREATER_THAN_EQUAL"
    LESS_THAN_EQUAL = "LESS_THAN_EQUAL"
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT_BETWEEN"
    IN = "IN"
    NOT_IN = "NOT_IN"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    IS_NULL = "IS_NULL"
    IS_NOT_NULL = "IS_NOT_NULL"

    default = "EQUALS"


class PDPParameterType(DomoEnumMixin, Enum):
    """Types of PDP policy parameters."""

    COLUMN = "COLUMN"  # Filter based on dataset column values
    DYNAMIC = "DYNAMIC"  # Filter based on Domo Trusted Attributes
    COMPUTED = "COMPUTED"  # Filter based on computed/derived values

    default = "COLUMN"


class PDPPolicyStatus(DomoEnumMixin, Enum):
    """Status of PDP policies."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"

    default = "ACTIVE"


@dataclass
class PdpParameter(DomoSubEntity):
    """Represents a single parameter (filter) within a PDP policy.

    Each parameter defines a specific filter condition that will be applied
    to the dataset when users access it through the policy.

    Attributes:
        column_name: The dataset column this parameter filters on
        column_values: list of values to filter by
        operator: The comparison operator to use (equals, greater than, etc.)
        parameter_type: Whether this is a column-based or dynamic filter
        ignore_case: Whether string comparisons should ignore case
        is_required: Whether this parameter must have a value
        description: Human-readable description of what this parameter does
        trusted_attribute_key: For dynamic parameters, the trusted attribute to use
    """

    column_name: str | None = None
    column_values: list[str] = field(default_factory=list)
    operator: PDPOperator | None = PDPOperator.EQUALS
    parameter_type: PDPParameterType | None = PDPParameterType.COLUMN
    ignore_case: bool = True
    is_required: bool = True
    description: str | None = None
    trusted_attribute_key: str | None = None

    def to_api_dict(self) -> dict[str, Any]:
        """Convert parameter to API format for Domo requests."""
        return {
            "columnName": self.column_name,
            "values": self.column_values,
            "operator": (
                self.operator.value if self.operator else PDPOperator.EQUALS.value
            ),
            "type": (
                self.parameter_type.value
                if self.parameter_type
                else PDPParameterType.COLUMN.value
            ),
            "ignoreCase": self.ignore_case,
            "trustedAttributeKey": self.trusted_attribute_key,
        }

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> "PdpParameter":
        """Create parameter from API response data."""
        return cls(
            column_name=data.get("columnName"),
            column_values=data.get("values", []),
            operator=PDPOperator.get(data.get("operator", "EQUALS")),
            parameter_type=PDPParameterType.get(data.get("type", "COLUMN")),
            ignore_case=data.get("ignoreCase", True),
            trusted_attribute_key=data.get("trustedAttributeKey"),
        )

    def find_relationship(self):
        raise NotImplementedError("find relationship not implemented yet")


@dataclass(eq=False)
class PDPPolicy(DomoEntity):
    """Represents a PDP (Personalized Data Permissions) policy.

    A PDP policy is a rule that applies to a dataset, defining how data should
    be filtered based on parameters and which users/groups have access.

    The policy uses the relationship system to manage user and group associations
    rather than storing direct lists, providing better tracking and management.

    Attributes:
        dataset_id: ID of the dataset this policy applies to
        filter_group_id: Domo's internal ID for this policy
        parameters: list of filter parameters that define the data restrictions
        policy_status: Current status of the policy (active, inactive, etc.)
        is_enabled: Whether the policy is currently enforced
        priority: Priority order when multiple policies apply
        effective_date: When the policy becomes effective
        expiration_date: When the policy expires (if applicable)
        created_by_user_id: ID of the user who created this policy
        last_modified_by_user_id: ID of the user who last modified this policy
        relationship_controller: Manages user/group relationships for this policy
    """

    dataset_id: str | None = None
    filter_group_id: str | None = None
    parameters: list[PdpParameter] = field(default_factory=list)
    policy_status: PDPPolicyStatus | None = PDPPolicyStatus.ACTIVE
    is_enabled: bool = True
    priority: int = 1
    effective_date: datetime | None = None
    expiration_date: datetime | None = None
    created_by_user_id: str | None = None
    last_modified_by_user_id: str | None = None
    relationship_controller: DomoRelationshipController = field(
        default_factory=DomoRelationshipController
    )

    def add_user(self, user_id: str, created_by: str | None = None) -> DomoRelationship:
        """Add a user to this PDP policy.

        Args:
            user_id: ID of the user to add
            created_by: ID of the user creating this relationship

        Returns:
            The created relationship object
        """
        return self.relationship_controller.create_relationship(
            source_entity_id=user_id,
            source_entity_type="user",
            target_entity_id=self.id or self.filter_group_id,
            target_entity_type="pdp_policy",
            relationship_type=ShareAccount.MEMBER,
            permissions=["data_access"],
            metadata={"policy_type": "pdp", "dataset_id": self.dataset_id},
            created_by=created_by,
        )

    def get_users(self) -> list[DomoRelationship]:
        """Get all users associated with this policy."""
        return self.relationship_controller.find_relationships(
            target_entity_id=self.id or self.filter_group_id,
            relationship_type=ShareAccount.MEMBER,
            active_only=True,
        )

    def get_groups(self) -> list[DomoRelationship]:
        """Get all groups associated with this policy."""
        return self.relationship_controller.find_relationships(
            target_entity_id=self.id or self.filter_group_id,
            relationship_type=ShareAccount.GROUP_MEMBER,
            active_only=True,
        )

    def remove_user(self, user_id: str) -> list[DomoRelationship]:
        """Remove a user from this policy."""
        return self.relationship_controller.revoke_relationship(
            source_entity_id=user_id,
            target_entity_id=self.id or self.filter_group_id,
            relationship_type=ShareAccount.MEMBER,
        )

    def remove_group(self, group_id: str) -> list[DomoRelationship]:
        """Remove a group from this policy."""
        return self.relationship_controller.revoke_relationship(
            source_entity_id=group_id,
            target_entity_id=self.id or self.filter_group_id,
            relationship_type=ShareAccount.GROUP_MEMBER,
        )

    def add_parameter(self, parameter: PdpParameter) -> None:
        """Add a filter parameter to this policy."""
        parameter.parent_id = self.id or self.filter_group_id
        self.parameters.append(parameter)

    def remove_parameter(self, parameter_id: str) -> None:
        """Remove a parameter from this policy."""
        self.parameters = [p for p in self.parameters if p.id != parameter_id]

    def is_active(self) -> bool:
        """Check if the policy is currently active and effective."""
        if not self.is_enabled or self.policy_status != PDPPolicyStatus.ACTIVE:
            return False

        now = datetime.now()

        if self.effective_date and self.effective_date > now:
            return False

        if self.expiration_date and self.expiration_date < now:
            return False

        return True

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> "PDPPolicy":
        """Create policy from API response data."""
        policy = cls(
            id=data.get("filterGroupId"),
            filter_group_id=data.get("filterGroupId"),
            name=data.get("name"),
            dataset_id=data.get("dataSourceId"),
            is_enabled=data.get("enabled", True),
            priority=data.get("priority", 1),
        )

        # Add parameters
        for param_data in data.get("parameters", []):
            parameter = PdpParameter.from_api_dict(param_data)
            policy.add_parameter(parameter)

        # Add user relationships
        for user_id in data.get("userIds", []):
            policy.add_user(user_id)

        # Add group relationships
        for group_id in data.get("groupIds", []):
            policy.add_group(group_id)

        return policy

    def add_group(
        self, group_id: str, created_by: str | None = None
    ) -> DomoRelationship:
        """Add a group to this PDP policy.

        Args:
            group_id: ID of the group to add
            created_by: ID of the user creating this relationship

        Returns:
            The created relationship object
        """
        return self.relationship_controller.create_relationship(
            source_entity_id=group_id,
            source_entity_type="group",
            target_entity_id=self.id or self.filter_group_id,
            target_entity_type="pdp_policy",
            relationship_type=ShareAccount.GROUP_MEMBER,
            permissions=["data_access"],
            metadata={"policy_type": "pdp", "dataset_id": self.dataset_id},
            created_by=created_by,
        )

    def to_api_dict(self) -> dict[str, Any]:
        """Convert policy to API format for Domo requests."""
        user_relationships = self.get_users()
        group_relationships = self.get_groups()

        return {
            "filterGroupId": self.filter_group_id,
            "name": self.name,
            "dataSourceId": self.dataset_id,
            "parameters": [param.to_api_dict() for param in self.parameters],
            "userIds": [rel.source_entity_id for rel in user_relationships],
            "groupIds": [rel.source_entity_id for rel in group_relationships],
            "virtualUserIds": [],  # Legacy field, typically empty
            "enabled": self.is_enabled,
            "priority": self.priority,
        }


@dataclass
class DatasetPdpPolicies(DomoSubEntity):
    """Manager for all PDP policies associated with a dataset.

    This class provides high-level operations for managing the collection
    of PDP policies that apply to a specific dataset.

    Attributes:
        dataset_id: ID of the dataset these policies apply to
        policies: list of PDP policies for this dataset
        is_pdp_enabled: Whether PDP is enabled for this dataset
    """

    policies: list[PDPPolicy] = field(default_factory=list)
    is_pdp_enabled: bool = False

    def add_policy(self, policy: PDPPolicy) -> None:
        """Add a policy to this dataset."""
        policy.dataset_id = self.dataset_id
        self.policies.append(policy)

    def remove_policy(self, policy_id: str) -> None:
        """Remove a policy from this dataset."""
        self.policies = [
            p
            for p in self.policies
            if p.id != policy_id and p.filter_group_id != policy_id
        ]

    def get_policy_by_id(self, policy_id: str) -> PDPPolicy | None:
        """Get a policy by its ID."""
        return next(
            (
                p
                for p in self.policies
                if p.id == policy_id or p.filter_group_id == policy_id
            ),
            None,
        )

    def get_policy_by_name(
        self, name: str, exact_match: bool = True
    ) -> PDPPolicy | None:
        """Get a policy by its name."""
        if exact_match:
            return next((p for p in self.policies if p.name == name), None)
        else:
            return next(
                (p for p in self.policies if name.lower() in p.name.lower()), None
            )

    def get_active_policies(self) -> list[PDPPolicy]:
        """Get all currently active policies."""
        return [p for p in self.policies if p.is_active()]

    def get_policies_for_user(self, user_id: str) -> list[PDPPolicy]:
        """Get all policies that apply to a specific user."""
        applicable_policies = []

        for policy in self.get_active_policies():
            user_relationships = policy.get_users()
            if any(rel.source_entity_id == user_id for rel in user_relationships):
                applicable_policies.append(policy)

        return applicable_policies

    def get_policies_for_group(self, group_id: str) -> list[PDPPolicy]:
        """Get all policies that apply to a specific group."""
        applicable_policies = []

        for policy in self.get_active_policies():
            group_relationships = policy.get_groups()
            if any(rel.source_entity_id == group_id for rel in group_relationships):
                applicable_policies.append(policy)
        return applicable_policies


__all__ = [
    "PDPOperator",
    "PDPParameterType",
    "PDPPolicyStatus",
    "PdpParameter",
    "PDPPolicy",
    "DatasetPdpPolicies",
]
