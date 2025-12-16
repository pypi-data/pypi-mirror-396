"""
An OT device's software or firmware component, e.g., PLC or SCADA module.

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

from .GridComponent import GridComponent

from ..vocab import OTDeviceTypeOv


class OTDevice(GridSTIXDomainObject):
    """
    An OT device's software or firmware component, e.g., PLC or SCADA module.


    This is an abstract class - it should not be instantiated directly.

    """

    # STIX type identifier for this Grid-STIX object
    _type = "x-grid-ot-device"

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
            ("x_device_type", ListProperty(StringProperty())),
            ("x_monitors", ListProperty(StringProperty())),
            ("x_access_control_list", ListProperty(StringProperty())),
            ("x_authentication_methods", ListProperty(StringProperty())),
            ("x_authentication_required", ListProperty(BooleanProperty())),
            ("x_certificate_expiry_date", ListProperty(StringProperty())),
            ("x_communication_heartbeat_interval", ListProperty(IntegerProperty())),
            ("x_control_logic_checksum", ListProperty(StringProperty())),
            ("x_device_id", ListProperty(StringProperty())),
            ("x_encryption_enabled", ListProperty(BooleanProperty())),
            ("x_endpoint_protection_status", ListProperty(StringProperty())),
            ("x_engineering_workstation_access", ListProperty(BooleanProperty())),
            ("x_firmware_version", ListProperty(StringProperty())),
            ("x_historian_data_retention", ListProperty(IntegerProperty())),
            ("x_hmi_interface_available", ListProperty(BooleanProperty())),
            ("x_ip_address", ListProperty(StringProperty())),
            ("x_log_retention_period", ListProperty(IntegerProperty())),
            ("x_logging_enabled", ListProperty(BooleanProperty())),
            ("x_mac_address", ListProperty(StringProperty())),
            ("x_network_isolation_status", ListProperty(StringProperty())),
            ("x_network_segment", ListProperty(StringProperty())),
            ("x_port_number", ListProperty(IntegerProperty())),
            ("x_protocol", ListProperty(StringProperty())),
            ("x_remote_access_enabled", ListProperty(BooleanProperty())),
            ("x_safety_system_integration", ListProperty(BooleanProperty())),
            ("x_security_patch_level", ListProperty(StringProperty())),
            ("x_supported_protocols", ListProperty(StringProperty())),
            ("x_vpn_required", ListProperty(BooleanProperty())),
        ]
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize OTDevice with Grid-STIX properties."""
        # Set STIX type if not provided
        if "type" not in kwargs:
            kwargs["type"] = self._type

        # Generate deterministic ID if not provided
        if "id" not in kwargs:
            from ..base import DeterministicUUIDGenerator

            # Generate deterministic UUID - will raise ValueError if required properties missing
            kwargs["id"] = DeterministicUUIDGenerator.generate_uuid(self._type, kwargs)

        super().__init__(**kwargs)
