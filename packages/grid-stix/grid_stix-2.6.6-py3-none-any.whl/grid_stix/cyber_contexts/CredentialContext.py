"""
Context information about user and device credentials for authentication decisions.

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


class CredentialContext(GridSTIXDomainObject):
    """
    Context information about user and device credentials for authentication decisions.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-credential-context"

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
            ("x_access_scope", ListProperty(StringProperty())),
            ("x_authentication_level", ListProperty(StringProperty())),
            ("x_credential_age", ListProperty(StringProperty())),
            ("x_credential_id", ListProperty(StringProperty())),
            ("x_credential_strength_score", ListProperty(FloatProperty())),
            ("x_credential_type", ListProperty(StringProperty())),
            ("x_last_authentication_time", ListProperty(StringProperty())),
            ("x_multi_factor_enabled", ListProperty(BooleanProperty())),
            ("x_privilege_level", ListProperty(StringProperty())),
            ("x_rotation_required", ListProperty(BooleanProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize CredentialContext with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
