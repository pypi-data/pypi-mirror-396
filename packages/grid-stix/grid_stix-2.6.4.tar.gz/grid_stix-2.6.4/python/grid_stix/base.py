"""
Grid-STIX Base Classes

This module provides base classes for all Grid-STIX objects that properly extend
the official STIX 2.1 library classes for grid-specific cybersecurity use cases.
"""

from __future__ import annotations

from typing import Optional, Any, Dict, List
from uuid import uuid4, uuid5, UUID
import hashlib
import json

from collections import OrderedDict

from stix2.v21 import _DomainObject, _RelationshipObject, _Observable  # type: ignore[import-untyped]
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


# Grid-STIX namespace UUID for deterministic UUID generation
GRID_STIX_NAMESPACE = UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


class DeterministicUUIDGenerator:
    """
    Generator for deterministic UUIDs based on Grid-STIX object properties.

    Uses UUID5 (namespace-based SHA-1 hashing) to generate consistent UUIDs
    for Grid-STIX objects based on their identity-defining properties.
    """

    @staticmethod
    def normalize_value(value: Any) -> str:
        """
        Normalize a property value for consistent UUID generation.

        Args:
            value: The property value to normalize

        Returns:
            Normalized string representation
        """
        if value is None:
            return ""
        elif isinstance(value, str):
            return value.lower().strip()
        elif isinstance(value, list):
            # Handle single-element lists by extracting the scalar value
            # This is common with OWL-generated properties that use ListProperty
            if len(value) == 1:
                return DeterministicUUIDGenerator.normalize_value(value[0])
            # For multi-element lists, sort and normalize each item
            normalized_items = [
                DeterministicUUIDGenerator.normalize_value(item) for item in value
            ]
            return json.dumps(sorted(normalized_items), sort_keys=True)
        elif isinstance(value, dict):
            # Sort dictionary keys and normalize values
            normalized_dict = {
                k: DeterministicUUIDGenerator.normalize_value(v)
                for k, v in value.items()
            }
            return json.dumps(normalized_dict, sort_keys=True)
        else:
            return str(value).lower().strip()

    @staticmethod
    def generate_uuid(object_type: str, properties: Dict[str, Any]) -> str:
        """
        Generate a deterministic UUID for a Grid-STIX object.

        Args:
            object_type: The STIX object type (e.g., 'x-grid-generator')
            properties: Dictionary of object properties

        Returns:
            Deterministic UUID string in STIX format

        Raises:
            ValueError: If required identity properties are missing or if no identity
                       properties are configured for the object type
        """
        # Get identity properties for this object type
        identity_props = IDENTITY_PROPERTY_CONFIG.get(object_type, [])

        if not identity_props:
            raise ValueError(
                f"CRITICAL: No identity properties configured for object type '{object_type}'. "
                f"Cannot generate deterministic UUID. This object type must be added to "
                f"IDENTITY_PROPERTY_CONFIG in base.py"
            )

        # Extract and validate identity property values
        identity_values = {}
        missing_props = []

        for prop in identity_props:
            if prop in properties and properties[prop] is not None:
                identity_values[prop] = properties[prop]
            else:
                missing_props.append(prop)

        if missing_props:
            raise ValueError(
                f"CRITICAL: Missing required identity properties for '{object_type}': {missing_props}. "
                f"Required properties: {identity_props}. "
                f"Provided properties: {list(properties.keys())}. "
                f"Deterministic UUID generation FAILED - object creation must be aborted."
            )

        # Create deterministic string from identity properties
        normalized_values = {}
        for prop, value in identity_values.items():
            normalized_values[prop] = DeterministicUUIDGenerator.normalize_value(value)

        # Sort by property name for consistency
        identity_string = json.dumps(normalized_values, sort_keys=True)

        # Generate UUID5 using Grid-STIX namespace
        uuid_obj = uuid5(GRID_STIX_NAMESPACE, identity_string)

        # Return in STIX format
        return f"{object_type}--{uuid_obj}"

    @staticmethod
    def validate_identity_properties(
        object_type: str, properties: Dict[str, Any]
    ) -> List[str]:
        """
        Validate that all required identity properties are present.

        Args:
            object_type: The STIX object type
            properties: Dictionary of object properties

        Returns:
            List of missing property names (empty if all present)
        """
        identity_props = IDENTITY_PROPERTY_CONFIG.get(object_type, [])
        missing_props = []

        for prop in identity_props:
            if prop not in properties or properties[prop] is None:
                missing_props.append(prop)

        return missing_props


# Configuration mapping object types to their identity-defining properties
IDENTITY_PROPERTY_CONFIG = {
    # Assets
    "x-grid-generator": [
        "name",
        "x_asset_id",
        "x_power_rating_mw",
        "x_fuel_type",
        "x_owner_organization",
    ],
    "x-grid-transformer": [
        "name",
        "x_voltage_primary_kv",
        "x_voltage_secondary_kv",
        "x_power_rating_mva",
    ],
    "x-grid-substation": [
        "name",
        "x_asset_id",
        "x_high_voltage_level_kv",
        "x_substation_type",
        "x_gps_coordinates",
    ],
    "x-grid-transmission-line": [
        "name",
        "x_asset_id",
        "x_voltage_level_kv",
        "x_length_km",
        "x_conductor_type",
    ],
    "x-grid-distribution-line": [
        "name",
        "x_asset_id",
        "x_voltage_level_kv",
        "x_length_km",
        "x_service_area",
    ],
    "x-grid-control-center": [
        "name",
        "x_asset_id",
        "x_control_area",
        "x_operator_organization",
    ],
    "x-grid-physical-asset": ["name", "x_asset_id", "x_asset_type", "x_location"],
    "x-grid-physical-grid-asset": [
        "name",
        "x_asset_id",
        "x_grid_function",
        "x_voltage_level_kv",
    ],
    "x-grid-grid-component": ["name", "x_grid_component_type", "x_manufacturer"],
    "x-grid-distribution-line": [
        "name",
        "x_grid_component_type",
        "x_voltage_level_kv",
        "x_length_km",
    ],
    "x-grid-transmission-line": [
        "name",
        "x_grid_component_type",
        "x_voltage_level_kv",
        "x_length_km",
        "x_conductor_type",
    ],
    "x-grid-operational-grid-entity": [
        "name",
        "x_entity_id",
        "x_operational_role",
        "x_jurisdiction",
    ],
    "x-grid-ot-device": ["name", "x_device_id", "x_device_type", "x_ip_address"],
    "x-grid-otdevice": ["name", "x_device_id", "x_device_type", "x_ip_address"],
    "x-grid-electronic-security-perimeter": [
        "name",
        "x_perimeter_id",
        "x_security_level",
        "x_protected_assets",
    ],
    "x-grid-physical-security-perimeter": [
        "name",
        "x_perimeter_id",
        "x_physical_barriers",
        "x_access_controls",
    ],
    "x-grid-security-zone": [
        "name",
        "x_zone_id",
        "x_security_classification",
        "x_contained_assets",
    ],
    "x-grid-supplier": [
        "name",
        "x_supplier_id",
        "x_supplier_type",
        "x_products_services",
    ],
    "x-grid-supply-chain-risk": [
        "name",
        "x_risk_id",
        "x_risk_category",
        "x_affected_suppliers",
    ],
    "x-grid-physical-asset": ["name"],  # Abstract class with minimal properties
    "x-grid-security-zone": ["name"],
    "x-grid-grid-attack-pattern": ["name"],
    # Context types - use semantic properties
    "x-grid-weather-context": ["first_observed", "x_weather_type"],
    "x-grid-natural-disaster-context": ["first_observed", "x_disaster_type"],
    "x-grid-maintenance-context": ["first_observed", "x_maintenance_type"],
    "x-grid-outage-context": ["first_observed", "x_outage_type"],
    "x-grid-grid-operating-condition-context": [
        "first_observed",
        "x_grid_operating_condition",
    ],
    "x-grid-emergency-response-context": ["first_observed", "x_emergency_type"],
    "x-grid-physical-security-context": ["first_observed", "x_security_event_type"],
    "x-grid-operational-context": ["first_observed", "x_operational_mode"],
    "x-grid-der-operational-context": ["first_observed", "x_der_resource_id"],
    # Components (unhyphenated versions match generator output)
    "x-grid-smart-meter": ["name", "x_asset_id", "x_ip_address", "x_mac_address"],
    "x-grid-smartmeter": ["name", "x_asset_id", "x_ip_address", "x_mac_address"],
    "x-grid-battery-energy-storage-system": [
        "name",
        "x_bess_system_id",
        "x_capacity_kwh",
        "x_bess_power_rating_kw",
    ],
    "x-grid-batteryenergystoragesystem": [
        "name",
        "x_bess_system_id",
        "x_capacity_kwh",
        "x_bess_power_rating_kw",
    ],
    "x-grid-inverter": ["name", "x_device_id", "x_power_rating_kw", "x_inverter_type"],
    "x-grid-photovoltaic-system": [
        "name",
        "x_system_id",
        "x_capacity_kw",
        "x_panel_type",
    ],
    "x-grid-windturbine": [
        "name",
        "x_turbine_id",
        "x_wind_capacity_kw",
        "x_hub_height_m",
    ],
    "x-grid-nuclearpowerplant": [
        "name",
        "x_plant_id",
        "x_reactor_type",
        "x_capacity_mw",
    ],
    "x-grid-electric-vehicle": [
        "name",
        "x_vehicle_id",
        "x_battery_capacity_kwh",
        "x_charging_standard",
    ],
    "x-grid-electric-vehicle-supply-equipment": [
        "name",
        "x_equipment_id",
        "x_power_level",
        "x_connector_type",
    ],
    "x-grid-distributed-energy-resource": [
        "name",
        "x_resource_id",
        "x_resource_type",
        "x_capacity_kw",
    ],
    "x-grid-microgrid": [
        "name",
        "x_microgrid_id",
        "x_islanding_capability",
        "x_connected_resources",
    ],
    "x-grid-sensor": ["name", "x_sensor_id", "x_measurement_type", "x_location"],
    "x-grid-smart-inverter": [
        "name",
        "x_device_id",
        "x_grid_support_functions",
        "x_communication_protocol",
    ],
    "x-grid-derms": [
        "name",
        "x_system_id",
        "x_managed_resources",
        "x_control_algorithms",
    ],
    "x-grid-distribution-management-system": [
        "name",
        "x_system_id",
        "x_controlled_feeders",
        "x_automation_level",
    ],
    "x-grid-advanced-metering-network": [
        "name",
        "x_network_id",
        "x_communication_technology",
        "x_meter_count",
    ],
    "x-grid-meter-data-management-system": [
        "name",
        "x_system_id",
        "x_data_sources",
        "x_analytics_capabilities",
    ],
    "x-grid-facility-energy-management-system": [
        "name",
        "x_system_id",
        "x_facility_type",
        "x_controlled_loads",
    ],
    "x-grid-human-machine-interface": [
        "name",
        "x_interface_id",
        "x_system_type",
        "x_user_roles",
    ],
    "x-grid-nuclear-power-plant": [
        "name",
        "x_plant_id",
        "x_reactor_type",
        "x_capacity_mw",
    ],
    "x-grid-fossil-fuel-plant": ["name", "x_plant_id", "x_fuel_type", "x_capacity_mw"],
    "x-grid-renewable-generation-facility": [
        "name",
        "x_facility_id",
        "x_generation_type",
        "x_capacity_mw",
    ],
    "x-grid-centralized-generation-facility": [
        "name",
        "x_facility_id",
        "x_generation_technology",
        "x_capacity_mw",
    ],
    "x-grid-fuel-cell": ["name", "x_device_id", "x_fuel_type", "x_power_rating_kw"],
    "x-grid-generation-asset": [
        "name",
        "x_asset_id",
        "x_generation_type",
        "x_capacity_mw",
    ],
    "x-grid-distribution-asset": [
        "name",
        "x_asset_id",
        "x_voltage_level_kv",
        "x_asset_function",
    ],
    # Cyber Contexts
    "x-grid-cybersecurity-posture": [
        "x_trust_level",
        "x_alert_level",
        "x_defensive_posture",
        "x_authorized_by",
    ],
    "x-grid-communication-session": [
        "x_session_id",
        "x_protocol_type",
        "x_session_start_time",
    ],
    "x-grid-network-segment": ["x_segment_id", "x_network_type", "x_security_zone"],
    "x-grid-api-endpoint": [
        "x_endpoint_url",
        "x_service_type",
        "x_authentication_method",
    ],
    "x-grid-certificate-context": [
        "x_certificate_id",
        "x_issuer",
        "x_subject",
        "x_serial_number",
    ],
    "x-grid-credential-context": [
        "x_credential_type",
        "x_username",
        "x_authentication_method",
    ],
    "x-grid-policy-decision-context": [
        "x_decision_id",
        "x_policy_set",
        "x_decision_time",
    ],
    "x-grid-policy-decision-point": [
        "x_pdp_id",
        "x_policy_engine",
        "x_decision_algorithms",
    ],
    "x-grid-policy-enforcement-point": [
        "x_pep_id",
        "x_enforcement_mechanism",
        "x_protected_resource",
    ],
    "x-grid-trust-broker": [
        "x_broker_id",
        "x_trust_algorithms",
        "x_participant_entities",
    ],
    "x-grid-real-time-trust-assessment": [
        "x_assessment_id",
        "x_trust_metrics",
        "x_assessment_time",
    ],
    "x-grid-risk-assessment": [
        "x_assessment_id",
        "x_risk_factors",
        "x_assessment_methodology",
    ],
    "x-grid-continuous-monitoring-agent": [
        "x_agent_id",
        "x_monitoring_scope",
        "x_data_sources",
    ],
    "x-grid-identity-verification-service": [
        "x_service_id",
        "x_verification_methods",
        "x_identity_providers",
    ],
    "x-grid-isolation-policy": [
        "x_policy_id",
        "x_isolation_criteria",
        "x_enforcement_actions",
    ],
    "x-grid-der-aggregator": [
        "x_aggregator_id",
        "x_aggregated_resources",
        "x_market_participation",
    ],
    "x-grid-grid-service-contract": [
        "x_contract_id",
        "x_service_type",
        "x_contracting_parties",
    ],
    # Attack Patterns
    "x-grid-cyber-attack-pattern": ["name", "x_capec_id", "x_attack_id"],
    "x-grid-physical-attack-pattern": ["name", "x_capec_id", "x_attack_id"],
    "x-grid-protocol-attack-pattern": ["name", "x_target_protocol", "x_attack_vector"],
    "x-grid-firmware-attack-pattern": [
        "name",
        "x_target_firmware",
        "x_exploitation_method",
    ],
    "x-grid-social-engineering-attack-pattern": [
        "name",
        "x_target_role",
        "x_manipulation_technique",
    ],
    "x-grid-grid-attack-pattern": ["name", "x_grid_target", "x_attack_objective"],
    "x-grid-grid-mitigation": ["name", "x_mitigation_type", "x_protected_assets"],
    "x-grid-impact-type": ["name", "x_impact_category", "x_severity_level"],
    # Events/Observables
    "x-grid-grid-event": ["x_event_type", "x_timestamp", "x_source_component"],
    "x-grid-alarm-event": [
        "x_alarm_type",
        "x_timestamp",
        "x_source_component",
        "x_severity",
    ],
    "x-grid-grid-telemetry": [
        "x_measurement_type",
        "x_measurement_timestamp",
        "x_source_device",
        "x_value",
    ],
    "x-grid-grid-protocol-traffic": [
        "x_protocol",
        "x_source_ip",
        "x_destination_ip",
        "x_source_port",
        "x_destination_port",
    ],
    "x-grid-authentication-event": [
        "x_user_ref",
        "x_authentication_factor",
        "x_authentication_result",
        "x_session_id",
    ],
    "x-grid-operational-event": [
        "x_event_type",
        "x_timestamp",
        "x_operational_context",
    ],
    "x-grid-maintenance-event": ["x_maintenance_type", "x_timestamp", "x_target_asset"],
    "x-grid-security-event": ["x_event_type", "x_timestamp", "x_security_context"],
    # Relationships
    "x-grid-grid-relationship": ["x_source_ref", "x_target_ref", "x_relationship_type"],
    "x-grid-connects-to-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-affects-operation-of-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-controls-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-feeds-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-feeds-power-to-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-located-at-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-monitors-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-supplied-by-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-authenticates-to-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-authenticates-with-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-authorizes-access-to-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-aggregates-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-certified-by-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-contained-in-facility-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-contains-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-converts-for-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-delegates-authority-to-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-depends-on-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-enforces-policy-on-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-generates-power-for-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-has-vulnerability-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-islands-from-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-monitored-by-environmental-sensor-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-monitors-trust-of-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-produces-waste-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-protects-asset-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-protects-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-triggers-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-trusts-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-verifies-identity-of-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    "x-grid-within-security-zone-relationship": [
        "x_source_ref",
        "x_target_ref",
        "x_relationship_type",
    ],
    # Nuclear Safeguards
    "x-grid-nuclear-facility": [
        "name",
        "x_facility_id",
        "x_facility_type",
        "x_safeguards_level",
    ],
    "x-grid-nuclear-material": [
        "x_material_id",
        "x_material_type",
        "x_enrichment_level",
    ],
    "x-grid-safeguards-system": [
        "x_system_id",
        "x_monitoring_capabilities",
        "x_detection_methods",
    ],
    # Policies
    "x-grid-access-policy": ["name"],
    "x-grid-security-policy": [
        "name",
        "x_policy_id",
        "x_policy_type",
        "x_enforcement_level",
    ],
    "x-grid-operational-policy": [
        "name",
        "x_policy_id",
        "x_operational_domain",
        "x_compliance_requirements",
    ],
    "x-grid-emergency-response-policy": [
        "name",
        "x_policy_id",
        "x_response_type",
        "x_activation_criteria",
    ],
    # Additional Components and Systems
    "x-grid-scada-system": [
        "name",
        "x_system_id",
        "x_controlled_assets",
        "x_communication_protocols",
    ],
    "x-grid-energy-management-system": [
        "name",
        "x_system_id",
        "x_optimization_algorithms",
        "x_controlled_resources",
    ],
    "x-grid-load-dispatch-center": [
        "name",
        "x_center_id",
        "x_dispatch_area",
        "x_generation_resources",
    ],
    "x-grid-protection-relay": [
        "name",
        "x_device_id",
        "x_protection_functions",
        "x_communication_protocol",
    ],
    "x-grid-circuit-breaker": [
        "name",
        "x_device_id",
        "x_voltage_rating_kv",
        "x_current_rating_a",
    ],
    "x-grid-capacitor-bank": [
        "name",
        "x_device_id",
        "x_reactive_power_mvar",
        "x_voltage_level_kv",
    ],
    "x-grid-voltage-regulator": [
        "name",
        "x_device_id",
        "x_regulation_range",
        "x_control_method",
    ],
    "x-grid-power-line-carrier": [
        "name",
        "x_device_id",
        "x_frequency_range",
        "x_communication_protocol",
    ],
    "x-grid-phasor-measurement-unit": [
        "name",
        "x_device_id",
        "x_sampling_rate",
        "x_gps_synchronization",
    ],
    "x-grid-wide-area-monitoring-system": [
        "name",
        "x_system_id",
        "x_monitored_area",
        "x_pmu_count",
    ],
}


class GridSTIXDomainObject(_DomainObject):  # type: ignore[misc]
    """
    Base class for Grid-STIX Domain Objects extending STIX 2.1 SDOs.

    This is an abstract base class. Concrete Grid-STIX classes should define
    their own _type and extend _properties appropriately.
    """

    # Base properties that all Grid-STIX domain objects should have
    # Concrete classes will extend this with their own _type and specific properties
    _base_properties = OrderedDict(
        [
            ("x_grid_context", DictionaryProperty()),
            ("x_operational_status", StringProperty()),
            ("x_compliance_framework", ListProperty(StringProperty)),
            ("x_grid_component_type", StringProperty()),
            ("x_criticality_level", IntegerProperty()),
        ]
    )


class GridSTIXRelationshipObject(_RelationshipObject):  # type: ignore[misc]
    """
    Base class for Grid-STIX Relationship Objects extending STIX 2.1 SROs.

    This is an abstract base class. Concrete Grid-STIX relationship classes
    should define their own _type and extend _properties appropriately.
    """

    # Base properties that all Grid-STIX relationship objects should have
    _base_properties = OrderedDict(
        [
            ("x_grid_relationship_context", DictionaryProperty()),
            ("x_physical_connection", BooleanProperty()),
            ("x_logical_connection", BooleanProperty()),
            ("x_power_flow_direction", StringProperty()),
        ]
    )


class GridSTIXObservableObject(_Observable):  # type: ignore[misc]
    """
    Base class for Grid-STIX Cyber Observable Objects extending STIX 2.1 SCOs.

    This is an abstract base class. Concrete Grid-STIX observable classes
    should define their own _type and extend _properties appropriately.
    """

    # Base properties that all Grid-STIX observable objects should have
    _base_properties = OrderedDict(
        [
            ("x_grid_measurement_type", StringProperty()),
            ("x_sensor_location", StringProperty()),
            ("x_measurement_unit", StringProperty()),
            ("x_sampling_rate", FloatProperty()),
        ]
    )
