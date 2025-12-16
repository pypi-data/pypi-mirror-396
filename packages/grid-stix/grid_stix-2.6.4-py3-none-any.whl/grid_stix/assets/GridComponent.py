"""
A grid component such as circuit breakers, switches, or relays.

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

from ..vocab import EnvironmentalImpactCategoryOv

from .PhysicalAsset import PhysicalAsset

from ..vocab import RegulatoryClassificationOv

from ..relationships import UnionAllAssets


# Forward references will be resolved after all classes are defined


class GridComponent(GridSTIXDomainObject):
    """
    A grid component such as circuit breakers, switches, or relays.


    This is an abstract class - it should not be instantiated directly.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-grid-component"

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
            ("x_environmental_characteristics", ListProperty(StringProperty())),
            ("x_regulatory_requirements", ListProperty(StringProperty())),
            ("x_specialized_properties", ListProperty(StringProperty())),
            ("x_component_of", ListProperty(StringProperty())),
            ("x_depends_on", ListProperty(StringProperty())),
            ("x_has_vulnerability", ListProperty(StringProperty())),
            ("x_protected_by", ListProperty(StringProperty())),
            ("x_shares_network_with", ListProperty(StringProperty())),
            ("x_connects_to", ListProperty(StringProperty())),
            ("x_feeds", ListProperty(StringProperty())),
            ("x_has_vulnerability", ListProperty(StringProperty())),
            ("x_protects_asset", ListProperty(StringProperty())),
            ("x_provides_service_to", ListProperty(StringProperty())),
            ("x_regulates_voltage", ListProperty(StringProperty())),
            ("x_synchronizes_with", ListProperty(StringProperty())),
            ("x_has_vulnerability", ListProperty(StringProperty())),
            ("x_authentication_enabled", ListProperty(BooleanProperty())),
            ("x_authentication_method", ListProperty(StringProperty())),
            ("x_boot_loader_version", ListProperty(StringProperty())),
            ("x_certificate_expiry_date", ListProperty(StringProperty())),
            ("x_communication_encrypted", ListProperty(BooleanProperty())),
            ("x_default_credentials_changed", ListProperty(BooleanProperty())),
            ("x_encryption_protocol", ListProperty(StringProperty())),
            ("x_firmware_update_available", ListProperty(BooleanProperty())),
            ("x_firmware_version", ListProperty(StringProperty())),
            ("x_installation_date", ListProperty(StringProperty())),
            ("x_ip_address", ListProperty(StringProperty())),
            ("x_last_communication_time", ListProperty(StringProperty())),
            ("x_last_firmware_update", ListProperty(StringProperty())),
            ("x_last_maintenance_date", ListProperty(StringProperty())),
            ("x_mac_address", ListProperty(StringProperty())),
            ("x_manufacturer", ListProperty(StringProperty())),
            ("x_model_number", ListProperty(StringProperty())),
            ("x_network_protocol", ListProperty(StringProperty())),
            ("x_operational_status", ListProperty(StringProperty())),
            ("x_serial_number", ListProperty(StringProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize GridComponent with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
