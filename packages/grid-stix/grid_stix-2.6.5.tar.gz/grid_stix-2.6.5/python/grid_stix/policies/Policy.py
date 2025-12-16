"""
Base class for all policy types applied in grid environments.

This class was automatically generated from the Grid-STIX ontology.

Namespace: http://www.anl.gov/sss/grid-stix-2.1-policies.owl

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

from ..assets import GridComponent

from ..assets import OTDevice

from .PolicyAction import PolicyAction

from ..vocab import ResponseLevelOv

from ..assets import SecurityZone


class Policy(GridSTIXDomainObject):
    """
    Base class for all policy types applied in grid environments.


    This is an abstract class - it should not be instantiated directly.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-policy"

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
            ("x_applies_to_component", ListProperty(StringProperty())),
            ("x_applies_to_device", ListProperty(StringProperty())),
            ("x_applies_to_zone", ListProperty(StringProperty())),
            ("x_authorized_by", ListProperty(StringProperty())),
            ("x_created_by", ListProperty(StringProperty())),
            ("x_enforcement_action", ListProperty(StringProperty())),
            ("x_enforcement_level", ListProperty(StringProperty())),
            ("x_object_marking_refs", ListProperty(StringProperty())),
            ("x_api_endpoints", ListProperty(StringProperty())),
            ("x_approval_workflow", ListProperty(StringProperty())),
            ("x_audit_requirement", ListProperty(BooleanProperty())),
            ("x_business_justification", ListProperty(StringProperty())),
            ("x_communication_plan", ListProperty(StringProperty())),
            ("x_compliance_level", ListProperty(StringProperty())),
            ("x_compliance_percentage", ListProperty(FloatProperty())),
            ("x_condition_expression", ListProperty(StringProperty())),
            ("x_conflict_resolution", ListProperty(StringProperty())),
            ("x_cost_benefit_analysis", ListProperty(StringProperty())),
            ("x_data_sources", ListProperty(StringProperty())),
            ("x_dependencies", ListProperty(StringProperty())),
            ("x_deployment_status", ListProperty(StringProperty())),
            ("x_deployment_target", ListProperty(StringProperty())),
            ("x_development_phase", ListProperty(StringProperty())),
            ("x_documentation_references", ListProperty(StringProperty())),
            ("x_effective_from", ListProperty(StringProperty())),
            ("x_effective_until", ListProperty(StringProperty())),
            ("x_emergency_override", ListProperty(BooleanProperty())),
            ("x_enforcement_mechanism", ListProperty(StringProperty())),
            ("x_escalation_procedure", ListProperty(StringProperty())),
            ("x_exception_handling", ListProperty(StringProperty())),
            ("x_execution_frequency", ListProperty(StringProperty())),
            ("x_governance_framework", ListProperty(StringProperty())),
            ("x_grid_impact_level", ListProperty(StringProperty())),
            ("x_impact_assessment", ListProperty(StringProperty())),
            ("x_integration_points", ListProperty(StringProperty())),
            ("x_lifecycle_stage", ListProperty(StringProperty())),
            ("x_maintenance_schedule", ListProperty(StringProperty())),
            ("x_monitoring_interval", ListProperty(IntegerProperty())),
            ("x_notification_channels", ListProperty(StringProperty())),
            ("x_operational_window", ListProperty(StringProperty())),
            ("x_performance_impact", ListProperty(StringProperty())),
            ("x_policy_group", ListProperty(StringProperty())),
            ("x_policy_id", ListProperty(StringProperty())),
            ("x_policy_language", ListProperty(StringProperty())),
            ("x_policy_rule", ListProperty(StringProperty())),
            ("x_priority", ListProperty(IntegerProperty())),
            ("x_regulatory_mapping", ListProperty(StringProperty())),
            ("x_reliability_impact", ListProperty(StringProperty())),
            ("x_resource_type", ListProperty(StringProperty())),
            ("x_risk_level", ListProperty(StringProperty())),
            ("x_rollback_procedure", ListProperty(StringProperty())),
            ("x_safety_considerations", ListProperty(StringProperty())),
            ("x_stakeholder_groups", ListProperty(StringProperty())),
            ("x_subject_type", ListProperty(StringProperty())),
            ("x_technology_stack", ListProperty(StringProperty())),
            ("x_testing_status", ListProperty(StringProperty())),
            ("x_training_requirement", ListProperty(BooleanProperty())),
            ("x_validation_criteria", ListProperty(StringProperty())),
            ("x_version", ListProperty(StringProperty())),
            ("x_violation_count", ListProperty(IntegerProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize Policy with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
