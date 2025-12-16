"""
Represents attack techniques specific to grid environments.

This class was automatically generated from the Grid-STIX ontology.

Namespace: http://www.anl.gov/sss/grid-stix-2.1-attack-patterns.owl

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

from ..vocab import DetectionMethodOv

from ..assets import GridComponent

from ..events_observables import GridEvent

from ..vocab import GridProtocolOv

from .ImpactType import ImpactType

from ..assets import OTDevice

from ..assets import SecurityZone


# Forward references will be resolved after all classes are defined


class GridAttackPattern(GridSTIXDomainObject):
    """
    Represents attack techniques specific to grid environments.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-grid-attack-pattern"

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
            ("x_affects_grid_component", ListProperty(StringProperty())),
            ("x_affects_ot_device", ListProperty(StringProperty())),
            ("x_affects_protocol", ListProperty(StringProperty())),
            ("x_has_detection_method", ListProperty(StringProperty())),
            ("x_has_impact_type", ListProperty(StringProperty())),
            ("x_has_mitigation", ListProperty(StringProperty())),
            ("x_indicated_by", ListProperty(StringProperty())),
            ("x_phase_in_kill_chain", ListProperty(StringProperty())),
            ("x_related_to", ListProperty(StringProperty())),
            ("x_targets_zone", ListProperty(StringProperty())),
            ("x_attributed_to", ListProperty(StringProperty())),
            ("x_access_level_required", ListProperty(StringProperty())),
            ("x_actor_motivation", ListProperty(StringProperty())),
            ("x_attack_id", ListProperty(StringProperty())),
            ("x_attack_objective", ListProperty(StringProperty())),
            ("x_business_continuity_impact", ListProperty(StringProperty())),
            ("x_campaign_association", ListProperty(StringProperty())),
            ("x_capec_id", ListProperty(StringProperty())),
            ("x_cascading_effects", ListProperty(BooleanProperty())),
            ("x_compliance_controls", ListProperty(StringProperty())),
            ("x_containment_procedures", ListProperty(StringProperty())),
            ("x_customers_affected", ListProperty(IntegerProperty())),
            ("x_cwe_id", ListProperty(StringProperty())),
            ("x_d3fend_id", ListProperty(StringProperty())),
            ("x_detection_difficulty", ListProperty(IntegerProperty())),
            ("x_detection_signatures", ListProperty(StringProperty())),
            ("x_detection_time", ListProperty(IntegerProperty())),
            ("x_estimated_downtime", ListProperty(IntegerProperty())),
            ("x_estimated_financial_impact", ListProperty(FloatProperty())),
            ("x_execution_time", ListProperty(IntegerProperty())),
            ("x_exploitability_score", ListProperty(FloatProperty())),
            ("x_forensic_artifacts", ListProperty(StringProperty())),
            ("x_frequency_impact", ListProperty(BooleanProperty())),
            ("x_grid_target", ListProperty(StringProperty())),
            ("x_impact_scope", ListProperty(StringProperty())),
            ("x_impact_score", ListProperty(FloatProperty())),
            ("x_likelihood_of_success", ListProperty(FloatProperty())),
            ("x_load_shedding_risk", ListProperty(BooleanProperty())),
            ("x_network_requirements", ListProperty(StringProperty())),
            ("x_overall_risk_score", ListProperty(FloatProperty())),
            ("x_persistence_capability", ListProperty(BooleanProperty())),
            ("x_preparation_time", ListProperty(IntegerProperty())),
            ("x_prerequisites", ListProperty(StringProperty())),
            ("x_prevention_measures", ListProperty(StringProperty())),
            ("x_protection_system_impact", ListProperty(BooleanProperty())),
            ("x_recovery_procedures", ListProperty(StringProperty())),
            ("x_recovery_time", ListProperty(IntegerProperty())),
            ("x_regulatory_framework", ListProperty(StringProperty())),
            ("x_reporting_requirement", ListProperty(BooleanProperty())),
            ("x_required_tools", ListProperty(StringProperty())),
            ("x_response_procedure", ListProperty(StringProperty())),
            ("x_restoration_cost", ListProperty(FloatProperty())),
            ("x_scada_system_impact", ListProperty(BooleanProperty())),
            ("x_severity", ListProperty(IntegerProperty())),
            ("x_skill_level_required", ListProperty(IntegerProperty())),
            ("x_stealth_level", ListProperty(IntegerProperty())),
            ("x_threat_actor_sophistication", ListProperty(StringProperty())),
            ("x_ttp_signature", ListProperty(StringProperty())),
            ("x_voltage_impact", ListProperty(BooleanProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize GridAttackPattern with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
