"""
Base class for all grid-related events and observables.

This class was automatically generated from the Grid-STIX ontology.

Namespace: http://www.anl.gov/sss/grid-stix-2.1-events-observables.owl

"""

from __future__ import annotations

from typing import Optional, Any, List, Dict
from collections import OrderedDict

from stix2.properties import (  # type: ignore[import-untyped]
    StringProperty,
    IntegerProperty,
    BooleanProperty,
    FloatProperty,
    ListProperty,
    DictionaryProperty,
    TimestampProperty,
    IDProperty,
    TypeProperty,
)
from stix2.utils import NOW  # type: ignore[import-untyped]


# External imports

from ..base import GridSTIXObservableObject

from .AlarmEvent import AlarmEvent

from ..vocab import DetectionMethodOv

from ..operational_contexts import EmergencyResponseContext

from ..assets import GridComponent

from ..assets import OTDevice

from ..policies import Policy

from ..assets import SecurityZone


# Forward references will be resolved after all classes are defined


class GridEvent(GridSTIXObservableObject):
    """
    Base class for all grid-related events and observables.


    This is an abstract class - it should not be instantiated directly.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-grid-event"

    # STIX properties definition following official STIX patterns
    _properties = OrderedDict(
        [
            ("type", TypeProperty(_type, spec_version="2.1")),
            ("spec_version", StringProperty(fixed="2.1")),
            ("id", IDProperty(_type, spec_version="2.1")),
            (
                "created",
                TimestampProperty(
                    default=lambda: NOW,
                    precision="millisecond",
                    precision_constraint="min",
                ),
            ),
            (
                "modified",
                TimestampProperty(
                    default=lambda: NOW,
                    precision="millisecond",
                    precision_constraint="min",
                ),
            ),
            ("name", StringProperty()),
            ("description", StringProperty()),
            # Grid-STIX base properties
            ("x_grid_context", DictionaryProperty()),
            ("x_operational_status", StringProperty()),
            ("x_compliance_framework", ListProperty(StringProperty)),
            ("x_grid_component_type", StringProperty()),
            ("x_criticality_level", IntegerProperty()),
            ("x_component_ref", ListProperty(StringProperty())),
            ("x_detection_method", ListProperty(StringProperty())),
            ("x_device_ref", ListProperty(StringProperty())),
            ("x_related_to", ListProperty(StringProperty())),
            ("x_sensor_ref", ListProperty(StringProperty())),
            ("x_zone_ref", ListProperty(StringProperty())),
            ("x_creates_alert_for", ListProperty(StringProperty())),
            ("x_leads_to", ListProperty(StringProperty())),
            ("x_requires_response", ListProperty(StringProperty())),
            ("x_triggers_policy", ListProperty(StringProperty())),
            ("x_description", ListProperty(StringProperty())),
            ("x_event_id", ListProperty(StringProperty())),
            ("x_severity", ListProperty(IntegerProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize GridEvent with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
