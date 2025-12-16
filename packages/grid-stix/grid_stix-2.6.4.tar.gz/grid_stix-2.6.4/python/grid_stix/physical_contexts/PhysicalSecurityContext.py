"""

      Physical Security Context – represents physical security events at grid facilities.


This class was automatically generated from the Grid-STIX ontology.

Namespace: http://www.anl.gov/sss/grid-stix-2.1-physical-contexts.owl

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

from ..base import GridSTIXDomainObject

from ..vocab import ResponseStatusOv

from ..vocab import SecurityEventTypeOv

from ..vocab import SecurityZoneTypeOv


class PhysicalSecurityContext(GridSTIXDomainObject):
    """

    Physical Security Context – represents physical security events at grid facilities.


    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-physical-security-context"

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
            ("x_facility_refs", ListProperty(StringProperty())),
            ("x_response_status", ListProperty(StringProperty())),
            ("x_security_event_type", ListProperty(StringProperty())),
            ("x_security_zone", ListProperty(StringProperty())),
            ("x_description", ListProperty(StringProperty())),
            ("x_detection_time", ListProperty(StringProperty())),
            ("x_severity", ListProperty(IntegerProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize PhysicalSecurityContext with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
