__all__ = ["DomoCertificationState", "DomoCertification"]

import datetime as dt
from dataclasses import dataclass
from enum import Enum

from ...base import DomoEnumMixin, DomoSubEntity
from ...utils import convert as cd


class DomoCertificationState(DomoEnumMixin, Enum):
    CERTIFIED = "certified"
    PENDING = "PENDING"
    EXPIRED = "EXPIRED"


@dataclass
class DomoCertification(DomoSubEntity):
    certification_state: DomoCertificationState = None
    last_updated: dt.datetime = None
    certification_type: str = None
    certification_name: str = None

    @classmethod
    def from_parent(cls, parent):
        return cls(
            parent=parent,
        )

    async def get(self):
        certification = self.parent.raw.get("certification")

        if not certification:
            return None

        self.last_updated = cd.convert_epoch_millisecond_to_datetime(
            certification.get("lastUpdated")
        )

        self.certification_type = certification.get("processType")
        self.certification_name = certification.get("processName")

        if isinstance(certification.get("state"), dict):
            self.certification_state = DomoCertificationState[
                certification.get("state").get("value")
            ]

        return self.to_dict()

    @classmethod
    def from_dict(
        cls,
        data,
        parent=None,
        parent_id=None,
        auth=None,
    ):
        """
        Create a DomoCertification from a dictionary.
        """
        return cls(
            auth=auth,
            parent=parent,
            parent_id=parent_id,
            certification_state=DomoCertificationState[data["state"]],
            last_updated=cd.convert_epoch_millisecond_to_datetime(data["lastUpdated"]),
            certification_type=data["processType"],
            certification_name=data["processName"],
        )
