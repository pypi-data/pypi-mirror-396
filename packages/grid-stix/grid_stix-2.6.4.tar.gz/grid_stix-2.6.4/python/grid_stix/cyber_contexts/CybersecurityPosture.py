"""

      Cybersecurity Posture – represents the current cybersecurity stance.


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

from ..vocab import AlertLevelOv

from ..vocab import AuthenticationRequirementOv

from ..vocab import DefensivePostureOv

from ..attack_patterns import GridMitigation

from ..vocab import IncidentResponseStatusOv

from ..vocab import MonitoringLevelOv

from ..physical_contexts import PhysicalSecurityContext

from ..vocab import TrustLevelOv


class CybersecurityPosture(GridSTIXDomainObject):
    """

    Cybersecurity Posture – represents the current cybersecurity stance.


    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-cybersecurity-posture"

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
            ("x_alert_level", ListProperty(StringProperty())),
            ("x_authentication_requirements", ListProperty(StringProperty())),
            ("x_authorized_by", ListProperty(StringProperty())),
            ("x_defensive_posture", ListProperty(StringProperty())),
            ("x_incident_response_status", ListProperty(StringProperty())),
            ("x_intelligence_sources", ListProperty(StringProperty())),
            ("x_monitoring_level", ListProperty(StringProperty())),
            ("x_trust_level", ListProperty(StringProperty())),
            ("x_compromises_physical_security", ListProperty(StringProperty())),
            ("x_implements_defense", ListProperty(StringProperty())),
            ("x_reason_for_level", ListProperty(StringProperty())),
            ("x_review_time", ListProperty(StringProperty())),
            ("x_special_access_controls", ListProperty(StringProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize CybersecurityPosture with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
