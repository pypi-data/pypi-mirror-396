"""
Current operational state relevant for zero trust policy decisions by OPA.

This class was automatically generated from the Grid-STIX ontology.

Namespace: http://www.anl.gov/sss/grid-stix-2.1-cyber-contexts.owl

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


class PolicyDecisionContext(GridSTIXDomainObject):
    """
    Current operational state relevant for zero trust policy decisions by OPA.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-policy-decision-context"

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
            ("x_active_threats_count", ListProperty(IntegerProperty())),
            ("x_automated_response_enabled", ListProperty(BooleanProperty())),
            ("x_context_validity_duration", ListProperty(StringProperty())),
            ("x_critical_asset_offline_count", ListProperty(IntegerProperty())),
            ("x_current_grid_state", ListProperty(StringProperty())),
            ("x_cyber_incident_level", ListProperty(StringProperty())),
            ("x_decision_context_id", ListProperty(StringProperty())),
            ("x_decision_timestamp", ListProperty(StringProperty())),
            ("x_der_participation_rate", ListProperty(FloatProperty())),
            ("x_emergency_mode_active", ListProperty(BooleanProperty())),
            ("x_frequency_deviation", ListProperty(FloatProperty())),
            ("x_maintenance_window_active", ListProperty(BooleanProperty())),
            ("x_market_conditions", ListProperty(StringProperty())),
            ("x_operator_alert_level", ListProperty(StringProperty())),
            ("x_peak_demand_period", ListProperty(BooleanProperty())),
            ("x_regulatory_compliance_status", ListProperty(StringProperty())),
            ("x_security_posture_level", ListProperty(StringProperty())),
            ("x_system_load_factor", ListProperty(FloatProperty())),
            ("x_voltage_stability_margin", ListProperty(FloatProperty())),
            ("x_weather_impact_level", ListProperty(StringProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize PolicyDecisionContext with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
