"""
Detected anomalies in grid behavior or patterns.

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

from ..relationships import UnionAllAssets


class AnomalyEvent(GridSTIXObservableObject):
    """
    Detected anomalies in grid behavior or patterns.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-anomaly-event"

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
            ("x_indicates_compromise", ListProperty(StringProperty())),
            ("x_anomaly_type", ListProperty(StringProperty())),
            ("x_baseline_value", ListProperty(FloatProperty())),
            ("x_confidence_score", ListProperty(FloatProperty())),
            ("x_detection_algorithm", ListProperty(StringProperty())),
            ("x_deviation_magnitude", ListProperty(FloatProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize AnomalyEvent with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
