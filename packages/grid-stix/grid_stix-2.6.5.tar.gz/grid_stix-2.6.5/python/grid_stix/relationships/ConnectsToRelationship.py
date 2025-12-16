"""
Relationship indicating a physical or logical connection between components.

This class was automatically generated from the Grid-STIX ontology.

Namespace: http://www.anl.gov/sss/grid-stix-2.1-relationships.owl

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

from ..base import GridSTIXRelationshipObject


class ConnectsToRelationship(GridSTIXRelationshipObject):
    """
    Relationship indicating a physical or logical connection between components.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-connects-to-relationship"

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
            ("x_bandwidth_mbps", ListProperty(FloatProperty())),
            ("x_connection_type", ListProperty(StringProperty())),
            ("x_encryption_enabled", ListProperty(BooleanProperty())),
            ("x_encryption_protocol", ListProperty(StringProperty())),
            ("x_interface_specification", ListProperty(StringProperty())),
            ("x_latency_ms", ListProperty(FloatProperty())),
            ("x_protocol_version", ListProperty(StringProperty())),
            ("x_throughput_mbps", ListProperty(FloatProperty())),
            ("x_voltage_level_kv", ListProperty(FloatProperty())),
            ("x_source_ref", StringProperty()),
            ("x_target_ref", StringProperty()),
            ("x_relationship_type", StringProperty()),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize ConnectsToRelationship with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
