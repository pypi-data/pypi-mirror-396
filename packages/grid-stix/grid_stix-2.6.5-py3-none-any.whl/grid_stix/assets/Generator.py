"""
A device that converts mechanical energy to electrical energy for use in an external circuit.

This class was automatically generated from the Grid-STIX ontology.

Namespace: http://www.anl.gov/sss/grid-stix-2.1-assets.owl

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


class Generator(GridSTIXDomainObject):
    """
    A device that converts mechanical energy to electrical energy for use in an external circuit.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-generator"

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
            ("x_efficiency_percentage", ListProperty(FloatProperty())),
            ("x_emission_rate_tons_mwh", ListProperty(FloatProperty())),
            ("x_fuel_type", ListProperty(StringProperty())),
            ("x_generator_technology", ListProperty(StringProperty())),
            ("x_minimum_load_mw", ListProperty(FloatProperty())),
            ("x_power_rating_mw", ListProperty(FloatProperty())),
            ("x_ramp_rate_mw_min", ListProperty(FloatProperty())),
            ("x_startup_time_minutes", ListProperty(IntegerProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize Generator with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
