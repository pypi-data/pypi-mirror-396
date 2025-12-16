"""
Represents natural disaster events affecting the grid.

This class was automatically generated from the Grid-STIX ontology.

Namespace: http://www.anl.gov/sss/grid-stix-2.1-environmental-contexts.owl

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

from ..vocab import CommunicationsStatusOv

from ..vocab import DisasterDeclarationLevelOv

from ..vocab import DisasterTypeOv

from ..operational_contexts import GridOperatingConditionContext

from ..vocab import TransportationStatusOv

from .WeatherContext import WeatherContext


class NaturalDisasterContext(GridSTIXDomainObject):
    """
    Represents natural disaster events affecting the grid.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-natural-disaster-context"

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
            ("x_affected_region_refs", ListProperty(StringProperty())),
            ("x_associated_weather_context", ListProperty(StringProperty())),
            ("x_communications_status", ListProperty(StringProperty())),
            ("x_declaring_authority", ListProperty(StringProperty())),
            ("x_disaster_declaration_level", ListProperty(StringProperty())),
            ("x_disaster_type", ListProperty(StringProperty())),
            ("x_evacuation_zones_refs", ListProperty(StringProperty())),
            ("x_object_marking_refs", ListProperty(StringProperty())),
            ("x_transportation_status", ListProperty(StringProperty())),
            ("x_influences_operational_context", ListProperty(StringProperty())),
            ("x_projected_end_time", ListProperty(StringProperty())),
            ("x_severity", ListProperty(IntegerProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize NaturalDisasterContext with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
