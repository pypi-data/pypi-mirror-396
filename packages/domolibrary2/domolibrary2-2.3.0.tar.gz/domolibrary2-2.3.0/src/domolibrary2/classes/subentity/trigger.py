"""Classes for managing Domo trigger configurations (dataflow execution triggers)

This module extends the DomoSchedule system to handle complex trigger scenarios:
- Multiple triggers per entity (vs single schedule)
- Dataset-based triggers (in addition to time-based)
- Conditional execution logic
- Multiple event types per trigger

DomoTriggerEvent_Schedule leverages the DomoSchedule factory to parse schedule
configurations, ensuring consistency with how DomoStream and other entities handle
time-based execution.

Architecture:
    DomoTriggerSettings (container)
    └── DomoTrigger (individual trigger)
        ├── DomoTriggerEvent_Schedule --> DomoSchedule_Base (reuses schedule parsing)
        ├── DomoTriggerEvent_DatasetUpdated
        └── DomoTriggerCondition
"""

__all__ = [
    "TriggerEventType",
    "DomoTriggerEvent_Base",
    "DomoTriggerEvent_DatasetUpdated",
    "DomoTriggerEvent_Schedule",
    "DomoTriggerCondition",
    "DomoTrigger",
    "DomoTriggerSettings",
]


from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ...base.base import DomoBase, DomoEnumMixin
from .schedule import DomoSchedule, DomoSchedule_Base


class TriggerEventType(DomoEnumMixin, Enum):
    """Types of trigger events"""

    DATASET_UPDATED = "DATASET_UPDATED"
    SCHEDULE = "SCHEDULE"
    MANUAL = "MANUAL"
    WEBHOOK = "WEBHOOK"


@dataclass
class DomoTriggerEvent_Base(DomoBase, ABC):
    """Base class for trigger events"""

    event_type: TriggerEventType
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @abstractmethod
    def get_human_readable_description(self) -> str:
        """Get human-readable description of the trigger event"""
        pass

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "DomoTriggerEvent_Base":
        """Factory method to create appropriate trigger event subclass"""
        event_type = obj.get("type", "").upper()

        if event_type == "DATASET_UPDATED":
            return DomoTriggerEvent_DatasetUpdated.from_dict(obj)
        elif event_type == "SCHEDULE":
            return DomoTriggerEvent_Schedule.from_dict(obj)
        else:
            # Return a generic trigger event for unknown types
            return DomoTriggerEvent_Generic.from_dict(obj)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "type": self.event_type.value,
            **self.raw,
        }


@dataclass
class DomoTriggerEvent_Generic(DomoTriggerEvent_Base):
    """Generic trigger event for unknown/future types"""

    def get_human_readable_description(self) -> str:
        return f"{self.event_type.value} trigger"

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "DomoTriggerEvent_Generic":
        event_type_str = obj.get("type", "MANUAL").upper()
        try:
            event_type = TriggerEventType(event_type_str)
        except ValueError:
            event_type = TriggerEventType.MANUAL

        return cls(event_type=event_type, raw=obj)


@dataclass
class DomoTriggerEvent_DatasetUpdated(DomoTriggerEvent_Base):
    """Trigger event for dataset updates"""

    dataset_id: str = None
    trigger_on_data_changed: bool = False
    event_type: TriggerEventType = field(
        default=TriggerEventType.DATASET_UPDATED, init=False
    )

    def get_human_readable_description(self) -> str:
        """Get human-readable description"""
        change_text = (
            "when data changes" if self.trigger_on_data_changed else "on every update"
        )
        return f"Dataset {self.dataset_id} updated ({change_text})"

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "DomoTriggerEvent_DatasetUpdated":
        return cls(
            dataset_id=obj.get("datasetId"),
            trigger_on_data_changed=obj.get("triggerOnDataChanged", False),
            raw=obj,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "type": self.event_type.value,
            "datasetId": self.dataset_id,
            "triggerOnDataChanged": self.trigger_on_data_changed,
        }

    def export_as_dict(self, override_fn: Callable | None = None) -> dict[str, Any]:
        """Export event as unified dictionary format

        Args:
            override_fn: Optional function to override export logic

        Returns:
            dict: Unified event dictionary with readable format
        """
        if override_fn:
            return override_fn(self)

        return {
            "type": self.event_type.value,
            "datasetId": self.dataset_id,
            "triggerOnDataChanged": self.trigger_on_data_changed,
            "humanReadable": self.get_human_readable_description(),
        }


@dataclass
class DomoTriggerEvent_Schedule(DomoTriggerEvent_Base):
    """Trigger event for scheduled execution

    Uses DomoSchedule factory to parse and interpret schedule configurations,
    ensuring consistency with Stream and other schedule implementations.
    """

    schedule_id: str | None = None
    schedule: DomoSchedule_Base | None = None  # Can be any DomoSchedule subclass
    event_type: TriggerEventType = field(default=TriggerEventType.SCHEDULE, init=False)

    def get_human_readable_description(self) -> str:
        """Get human-readable description

        For schedule triggers, returns the cron expression when available,
        otherwise returns a human-friendly description.

        Returns:
            str: Human-readable description like "0 47 12 ? * MON *" or "Schedule: Daily at 12:00"
        """
        if self.schedule:
            # For custom cron schedules, show the expression instead of generic "Custom schedule"
            from .schedule import DomoCronSchedule, ScheduleFrequencyEnum

            if (
                self.schedule.frequency == ScheduleFrequencyEnum.CUSTOM_CRON
                and isinstance(self.schedule, DomoCronSchedule)
                and self.schedule.schedule_expression
            ):
                return self.schedule.schedule_expression

            return self.schedule.get_human_readable_schedule()
        return "Scheduled trigger"

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "DomoTriggerEvent_Schedule":
        """Create schedule event from trigger event dict

        Leverages DomoSchedule factory to determine the appropriate schedule type
        (Simple, Cron, or Advanced) based on the schedule data structure.
        """
        schedule_id = obj.get("id")
        schedule_data = obj.get("schedule")

        # Parse schedule if present using DomoSchedule factory
        schedule = None
        if schedule_data:
            # Build cron expression for DomoSchedule
            cron_expr = cls._build_cron_expression(schedule_data)

            # Create schedule dict for DomoSchedule factory
            schedule_dict = {
                "scheduleExpression": cron_expr,
                "timezone": schedule_data.get("timezone"),
            }

            # Use DomoSchedule factory to determine appropriate schedule type
            # This ensures consistency with how Streams handle schedules
            schedule_class = DomoSchedule.determine_schedule_type(schedule_dict)
            schedule = schedule_class.from_dict(schedule_dict, parent=None)

            # Store raw schedule data for round-trip serialization
            schedule.raw["raw_schedule"] = schedule_data

        return cls(schedule_id=schedule_id, schedule=schedule, raw=obj)

    @staticmethod
    def _build_cron_expression(schedule_data: dict[str, Any]) -> str:
        """Build cron expression from schedule components"""
        # Cron format: second minute hour dayOfMonth month dayOfWeek year
        components = [
            schedule_data.get("second", "0"),
            schedule_data.get("minute", "0"),
            schedule_data.get("hour", "*"),
            schedule_data.get("dayOfMonth", "*"),
            schedule_data.get("month", "*"),
            schedule_data.get("dayOfWeek", "*"),
        ]

        if "year" in schedule_data:
            components.append(schedule_data["year"])

        return " ".join(components)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            "type": self.event_type.value,
        }

        if self.schedule_id:
            result["id"] = self.schedule_id

        if self.schedule and hasattr(self.schedule, "raw"):
            raw_schedule = self.schedule.raw.get("raw_schedule")
            if raw_schedule:
                result["schedule"] = raw_schedule

        return result

    def export_as_dict(self, override_fn: Callable | None = None) -> dict[str, Any]:
        """Export event as unified dictionary format

        Args:
            override_fn: Optional function to override export logic

        Returns:
            dict: Unified event dictionary with readable format
        """
        if override_fn:
            return override_fn(self)

        result = {
            "type": self.event_type.value,
            "humanReadable": self.get_human_readable_description(),
        }

        if self.schedule_id:
            result["scheduleId"] = self.schedule_id

        # Include schedule details using DomoSchedule's export_as_dict
        if self.schedule:
            result["schedule"] = self.schedule.export_as_dict()

        return result


@dataclass
class DomoTriggerCondition(DomoBase):
    """Condition that must be met for trigger to fire"""

    condition_type: str = None
    parameters: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "DomoTriggerCondition":
        return cls(
            condition_type=obj.get("type"),
            parameters=obj.get("parameters", {}),
            raw=obj,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "type": self.condition_type,
            "parameters": self.parameters,
            **{k: v for k, v in self.raw.items() if k not in ["type", "parameters"]},
        }

    def export_as_dict(self, override_fn: Callable | None = None) -> dict[str, Any]:
        """Export condition as unified dictionary format

        Args:
            override_fn: Optional function to override export logic

        Returns:
            dict: Unified condition dictionary with readable format
        """
        if override_fn:
            return override_fn(self)

        return {
            "type": self.condition_type,
            "parameters": self.parameters,
            "humanReadable": self.get_human_readable_description(),
        }

    def get_human_readable_description(self) -> str:
        """Get human-readable description of the condition"""
        if not self.condition_type:
            return "No conditions"
        return f"Condition: {self.condition_type}"


@dataclass
class DomoTrigger(DomoBase):
    """A single trigger configuration with events and conditions"""

    trigger_id: int
    title: str = None
    trigger_events: list[DomoTriggerEvent_Base] = field(default_factory=list)
    trigger_conditions: list[DomoTriggerCondition] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "DomoTrigger":
        """Create DomoTrigger from dictionary"""
        trigger_events = [
            DomoTriggerEvent_Base.from_dict(event)
            for event in obj.get("triggerEvents", [])
        ]

        trigger_conditions = [
            DomoTriggerCondition.from_dict(condition)
            for condition in obj.get("triggerConditions", [])
        ]

        return cls(
            trigger_id=obj.get("triggerId"),
            title=obj.get("title"),
            trigger_events=trigger_events,
            trigger_conditions=trigger_conditions,
            raw=obj,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "triggerId": self.trigger_id,
            "title": self.title,
            "triggerEvents": [event.to_dict() for event in self.trigger_events],
            "triggerConditions": [
                condition.to_dict() for condition in self.trigger_conditions
            ],
        }

    def export_as_dict(self, override_fn: Callable | None = None) -> dict[str, Any]:
        """Export trigger as unified dictionary format

        Args:
            override_fn: Optional function to override export logic

        Returns:
            dict: Unified trigger dictionary with readable format
        """
        if override_fn:
            return override_fn(self)

        return {
            "triggerId": self.trigger_id,
            "title": self.title,
            "triggerEvents": [
                (
                    event.export_as_dict()
                    if hasattr(event, "export_as_dict")
                    else event.to_dict()
                )
                for event in self.trigger_events
            ],
            "triggerConditions": [
                (
                    condition.export_as_dict()
                    if hasattr(condition, "export_as_dict")
                    else condition.to_dict()
                )
                for condition in self.trigger_conditions
            ],
            "humanReadable": self.get_human_readable_description(),
        }

    def get_human_readable_description(self) -> str:
        """Get human-readable description of the trigger"""
        parts = []

        if self.title:
            parts.append(f"'{self.title}'")

        # Describe events
        if self.trigger_events:
            event_descriptions = [
                event.get_human_readable_description() for event in self.trigger_events
            ]
            parts.append(f"Events: {'; '.join(event_descriptions)}")

        # Describe conditions
        if self.trigger_conditions:
            condition_descriptions = [
                condition.get_human_readable_description()
                for condition in self.trigger_conditions
            ]
            parts.append(f"Conditions: {'; '.join(condition_descriptions)}")

        return " | ".join(parts) if parts else f"Trigger {self.trigger_id}"

    def has_schedule_event(self) -> bool:
        """Check if this trigger has a schedule event"""
        return any(
            isinstance(event, DomoTriggerEvent_Schedule)
            for event in self.trigger_events
        )

    def has_dataset_event(self) -> bool:
        """Check if this trigger has a dataset update event"""
        return any(
            isinstance(event, DomoTriggerEvent_DatasetUpdated)
            for event in self.trigger_events
        )

    def get_schedule_events(self) -> list[DomoTriggerEvent_Schedule]:
        """Get all schedule events from this trigger"""
        return [
            event
            for event in self.trigger_events
            if isinstance(event, DomoTriggerEvent_Schedule)
        ]

    def get_dataset_events(self) -> list[DomoTriggerEvent_DatasetUpdated]:
        """Get all dataset update events from this trigger"""
        return [
            event
            for event in self.trigger_events
            if isinstance(event, DomoTriggerEvent_DatasetUpdated)
        ]

    def __str__(self) -> str:
        return self.get_human_readable_description()


@dataclass
class DomoTriggerSettings(DomoBase):
    """Manager for trigger settings (collection of triggers)"""

    triggers: list[DomoTrigger] = field(default_factory=list)
    zone_id: str = "UTC"
    locale: str = "en_US"
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    parent: Any = None  # Parent entity (e.g., DomoDataflow)

    @classmethod
    def from_dict(
        cls, obj: dict[str, Any], parent: Any = None
    ) -> "DomoTriggerSettings":
        """Create DomoTriggerSettings from dictionary"""
        triggers = [
            DomoTrigger.from_dict(trigger) for trigger in obj.get("triggers", [])
        ]

        return cls(
            triggers=triggers,
            zone_id=obj.get("zoneId", "UTC"),
            locale=obj.get("locale", "en_US"),
            parent=parent,
            raw=obj,
        )

    @classmethod
    def from_parent(
        cls, parent: Any, obj: dict[str, Any] | None = None
    ) -> "DomoTriggerSettings":
        """Create from parent entity"""
        if obj is None:
            obj = {}

        return cls.from_dict(obj, parent=parent)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "triggers": [trigger.to_dict() for trigger in self.triggers],
            "zoneId": self.zone_id,
            "locale": self.locale,
        }

    def export_as_dict(self, override_fn: Callable | None = None) -> dict[str, Any]:
        """Export trigger settings as unified dictionary format

        Calls export_as_dict on each trigger to get detailed, readable format.

        Args:
            override_fn: Optional function to override export logic

        Returns:
            dict: Unified trigger settings dictionary with readable format
        """
        if override_fn:
            return override_fn(self)

        return {
            "triggers": [trigger.export_as_dict() for trigger in self.triggers],
            "zoneId": self.zone_id,
            "locale": self.locale,
            "summary": self.get_human_readable_summary(),
            "stats": {
                "totalTriggers": len(self.triggers),
                "scheduleTriggers": len(self.get_schedule_triggers()),
                "datasetTriggers": len(self.get_dataset_triggers()),
            },
        }

    def get_trigger_by_id(self, trigger_id: int) -> DomoTrigger | None:
        """Get a specific trigger by ID"""
        for trigger in self.triggers:
            if trigger.trigger_id == trigger_id:
                return trigger
        return None

    def get_schedule_triggers(self) -> list[DomoTrigger]:
        """Get all triggers that have schedule events"""
        return [trigger for trigger in self.triggers if trigger.has_schedule_event()]

    def get_dataset_triggers(self) -> list[DomoTrigger]:
        """Get all triggers that have dataset update events"""
        return [trigger for trigger in self.triggers if trigger.has_dataset_event()]

    def has_any_schedules(self) -> bool:
        """Check if any trigger has a schedule event"""
        return len(self.get_schedule_triggers()) > 0

    def has_any_dataset_triggers(self) -> bool:
        """Check if any trigger has dataset update events"""
        return len(self.get_dataset_triggers()) > 0

    def get_human_readable_summary(self) -> str:
        """Get human-readable summary of all triggers"""
        if not self.triggers:
            return "No triggers configured"

        parts = []
        for trigger in self.triggers:
            parts.append(f"  • {trigger.get_human_readable_description()}")

        return f"Triggers ({len(self.triggers)}):\n" + "\n".join(parts)

    def __len__(self) -> int:
        return len(self.triggers)

    def __iter__(self):
        return iter(self.triggers)

    def __getitem__(self, index):
        return self.triggers[index]

    def __str__(self) -> str:
        return self.get_human_readable_summary()
