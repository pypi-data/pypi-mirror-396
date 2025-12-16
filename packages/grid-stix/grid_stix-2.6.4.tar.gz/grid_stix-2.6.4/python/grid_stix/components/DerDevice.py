"""
An individual DER device inside a group of DER that collectively form a system.

This class was automatically generated from the Grid-STIX ontology.

Namespace: http://www.anl.gov/sss/grid-stix-2.1-components.owl

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

from .Derms import Derms

from .FacilityEnergyManagementSystem import FacilityEnergyManagementSystem

from .HumanMachineInterface import HumanMachineInterface

from .SensorInputs import SensorInputs


# Forward references will be resolved after all classes are defined


class DerDevice(GridSTIXDomainObject):
    """
    An individual DER device inside a group of DER that collectively form a system.


    This is an abstract class - it should not be instantiated directly.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-der-device"

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
            ("x_backup_communication_path", ListProperty(StringProperty())),
            ("x_owned_by", ListProperty(StringProperty())),
            ("x_reports_to", ListProperty(StringProperty())),
            ("x_accessed_through", ListProperty(StringProperty())),
            ("x_managed_by", ListProperty(StringProperty())),
            ("x_monitored_by", ListProperty(StringProperty())),
            ("x_der_function_capability", ListProperty(StringProperty())),
            ("x_grid_support_functions", ListProperty(StringProperty())),
            ("x_inverter_type", ListProperty(StringProperty())),
            ("x_nameplate_capacity", ListProperty(FloatProperty())),
            ("x_reactive_power_capability", ListProperty(FloatProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize DerDevice with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
