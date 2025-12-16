__all__ = [
    "AccessConfigError",
    "AccessRelationship",
    "DomoAccess",
]

from dataclasses import dataclass, field

from domolibrary2.base.relationships import DomoRelationshipController
from domolibrary2.routes.account.sharing import ShareAccount

from ...base.entities import DomoEntity, DomoSubEntity
from ...base.exceptions import ClassError
from ...base.relationships import DomoRelationship

# from .. import DomoUser as dmdu


class AccessConfigError(ClassError):
    def __init__(self, cls_instance=None, account_id=None, message=None):
        super().__init__(
            cls_instance=cls_instance,
            entity_id=account_id,
            message=message,
        )


@dataclass
class AccessRelationship(DomoRelationship):
    """Describes an entity with access to an object.
    Will describe sharing accounts, datasets and dataflows
    """


@dataclass
class DomoAccess(DomoRelationshipController, DomoSubEntity):
    """
    Describes concept of content access
    ex. DomoAccount.Access can be SHARED, VIEWED, EDIT access with DomoUsers and DomoGroups
    """

    share_enum: ShareAccount = field(
        repr=False, default=None
    )  # describes the types of access (view, read, owner) a related entity can have

    def __post_init__(self):
        # super().__post_init__()

        if self.share_enum and not issubclass(self.share_enum, ShareAccount):
            print(self.share_enum)
            raise AccessConfigError(
                cls_instance=self,
                account_id=self.parent_id,
                message="Share enum must be a subclass of ShareAccount.",
            )

    async def get(self) -> list[DomoRelationship]:
        """Get all access relationships for this object."""
        raise NotImplementedError("DomoAccess.get not implemented")

    async def grant_access(
        self,
        entity: DomoEntity,
        relationship_type: ShareAccount,
        **kwargs,
    ) -> bool:
        """Grant access to an entity."""
        raise NotImplementedError("DomoAccess.grant_access not implemented")

    async def revoke_access(
        self,
        entity: DomoEntity,
        relationship_type: ShareAccount,
        **kwargs,
    ) -> bool:
        """Revoke access from an entity."""
        raise NotImplementedError("DomoAccess.revoke_access not implemented")
