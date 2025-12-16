__all__ = [
    "parse_dt",
    "DomoScheduler_Policy_Restrictions",
    "DomoScheduler_Policy_Frequencies",
    "DomoScheduler_Policy_Member",
    "DomoScheduler_Policy",
    "DomoScheduler_Policies",
]

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal

import httpx

from ...auth import DomoAuth
from ...base import DomoBase, DomoEnumMixin, DomoSubEntity
from ...client.context import RouteContext
from ...routes.instance_config import scheduler_policies as instance_config_routes


def parse_dt(dt: str) -> datetime:
    return datetime.fromisoformat(dt.replace("Z", "+00:00"))


class DomoScheduler_Policy_Restrictions(DomoEnumMixin, Enum):
    NO_RESTRICTIONS = 0
    FIFTEEN_MINUTES = 15
    THIRTY_MINUTES = 30
    HOURLY = 60
    DAILY = 1440


@dataclass
class DomoScheduler_Policy_Frequencies:
    connector_frequency: DomoScheduler_Policy_Restrictions
    dataflow_frequency: DomoScheduler_Policy_Restrictions

    @classmethod
    def from_dict(cls, d: dict[str, Any]):
        def to_enum(v: int) -> DomoScheduler_Policy_Restrictions:
            try:
                return DomoScheduler_Policy_Restrictions(v)
            except ValueError:
                raise ValueError(f"Unsupported frequency (minutes): {v}")

        return cls(
            connector_frequency=to_enum(d["connectorFrequency"]),
            dataflow_frequency=to_enum(d["dataflowFrequency"]),
        )

    def to_dict(self) -> dict:
        return {
            "connectorFrequency": self.connector_frequency.value,
            "dataflowFrequency": self.dataflow_frequency.value,
        }


@dataclass
class DomoScheduler_Policy_Member:
    type: Literal["USER", "GROUP"]
    # TODO: Investigate if its worth it to connect to group or user domo classes
    id: str

    @classmethod
    def from_dict(cls, d: dict):
        return cls(type=d["type"], id=str(d["id"]))

    def to_dict(self) -> dict:
        return {"type": self.type, "id": self.id}


@dataclass
class DomoScheduler_Policy(DomoBase):
    created_on: datetime
    name: str
    frequencies: DomoScheduler_Policy_Frequencies
    members: list[DomoScheduler_Policy_Member] = field(default_factory=list)
    id: str | None = field(
        default=None
    )  # Will be None if the policy is not yet created (used on upsert)
    policy_id: str | None = field(default=None)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            created_on=parse_dt(d["createdOn"]),
            id=d["id"],
            name=d["name"],
            frequencies=DomoScheduler_Policy_Frequencies.from_dict(d["frequencies"]),
            members=[DomoScheduler_Policy_Member.from_dict(m) for m in d["members"]],
        )

    def to_dict(self, override_fn: Callable[[str, Any], Any] | None = None) -> dict:
        return {
            "createdOn": self.created_on.isoformat().replace("+00:00", "Z"),
            "id": self.id,
            "name": self.name,
            "frequencies": self.frequencies.to_dict(),
            "members": [m.to_dict() for m in self.members],
            "policyId": self.policy_id,
        }


@dataclass
class DomoScheduler_Policies(DomoSubEntity):
    auth: DomoAuth
    policies: list[DomoScheduler_Policy] = field(default_factory=list)

    async def get(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
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

        res = await instance_config_routes.get_scheduler_policies(
            auth=self.auth,
            return_raw=return_raw,
            context=context,
        )
        self.policies = [DomoScheduler_Policy.from_dict(p) for p in res.response]
        print(self.policies)
        return self.policies

    async def upsert(
        self,
        policy: DomoScheduler_Policy,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
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

        create_policy = (not policy.id or not str(policy.id).strip()) or (
            policy.id not in {p.id for p in self.policies}
        )
        # If the policy is not yet created, create it
        if create_policy:
            res = await instance_config_routes.create_scheduler_policy(
                auth=self.auth,
                create_body=policy.to_dict(),
                return_raw=return_raw,
                context=context,
            )
            policy = DomoScheduler_Policy.from_dict(res.response)
            self.policies.append(policy)
            return policy
        else:
            idx = self.policies.index(policy)
            res = await instance_config_routes.update_scheduler_policy(
                auth=self.auth,
                policy_id=policy.id,
                update_body=policy.to_dict(),
                return_raw=return_raw,
                context=context,
            )
            policy = DomoScheduler_Policy.from_dict(res.response)
            self.policies[idx] = policy
            return policy

    async def delete(
        self,
        policy_id: str,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
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

        res = await instance_config_routes.delete_scheduler_policy(
            auth=self.auth,
            policy_id=policy_id,
            context=context,
        )
        return res.is_success
