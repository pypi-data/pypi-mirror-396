"""
Base class for all grid-specific relationships.

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


class GridRelationship(GridSTIXRelationshipObject):
    """
    Base class for all grid-specific relationships.


    This is an abstract class - it should not be instantiated directly.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-grid-relationship"

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
            ("x_access_control_level", ListProperty(StringProperty())),
            ("x_anomaly_score", ListProperty(FloatProperty())),
            ("x_availability_percentage", ListProperty(FloatProperty())),
            ("x_business_criticality", ListProperty(StringProperty())),
            ("x_compliance_status", ListProperty(StringProperty())),
            ("x_confidence_level", ListProperty(FloatProperty())),
            ("x_configuration_details", ListProperty(StringProperty())),
            ("x_correlation_strength", ListProperty(FloatProperty())),
            ("x_cost_impact", ListProperty(FloatProperty())),
            ("x_duration_seconds", ListProperty(IntegerProperty())),
            ("x_end_date", ListProperty(StringProperty())),
            ("x_environmental_factor", ListProperty(StringProperty())),
            ("x_frequency_hz", ListProperty(FloatProperty())),
            ("x_frequency_regulation_capability", ListProperty(BooleanProperty())),
            ("x_historical_pattern", ListProperty(StringProperty())),
            ("x_last_verified_date", ListProperty(StringProperty())),
            ("x_learning_model_applied", ListProperty(StringProperty())),
            ("x_lifecycle_stage", ListProperty(StringProperty())),
            ("x_load_condition", ListProperty(StringProperty())),
            ("x_load_following_capability", ListProperty(BooleanProperty())),
            ("x_maintenance_status", ListProperty(StringProperty())),
            ("x_operational_mode", ListProperty(StringProperty())),
            ("x_predictive_indicator", ListProperty(BooleanProperty())),
            ("x_quality_score", ListProperty(FloatProperty())),
            ("x_redundancy_level", ListProperty(StringProperty())),
            ("x_regulatory_requirement", ListProperty(StringProperty())),
            ("x_reliability", ListProperty(FloatProperty())),
            ("x_risk_score", ListProperty(FloatProperty())),
            ("x_schedule_pattern", ListProperty(StringProperty())),
            ("x_sla_requirement", ListProperty(StringProperty())),
            ("x_source_credibility", ListProperty(StringProperty())),
            ("x_stability_margin", ListProperty(FloatProperty())),
            ("x_start_date", ListProperty(StringProperty())),
            ("x_threat_level", ListProperty(StringProperty())),
            ("x_troubleshooting_info", ListProperty(StringProperty())),
            ("x_validation_status", ListProperty(StringProperty())),
            ("x_vendor_specific_data", ListProperty(StringProperty())),
            ("x_verification_method", ListProperty(StringProperty())),
            ("x_source_ref", StringProperty()),
            ("x_target_ref", StringProperty()),
            ("x_relationship_type", StringProperty()),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize GridRelationship with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
