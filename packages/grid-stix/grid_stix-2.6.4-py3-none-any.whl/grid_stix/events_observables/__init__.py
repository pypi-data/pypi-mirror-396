"""
grid_stix.events_observables - Generated Grid-STIX module

This module was automatically generated from the Grid-STIX ontology.
It contains Python classes corresponding to OWL classes in the ontology.
"""

# Import all classes from this module


from .AlarmEvent import AlarmEvent


from .AnomalyEvent import AnomalyEvent


from .AuthenticationEvent import AuthenticationEvent


from .ConfigurationEvent import ConfigurationEvent


from .ControlActionEvent import ControlActionEvent


from .FirmwareEvent import FirmwareEvent


from .GridEvent import GridEvent


from .GridProtocolTraffic import GridProtocolTraffic


from .GridTelemetry import GridTelemetry


from .MaintenanceEvent import MaintenanceEvent


from .PhysicalAccessEvent import PhysicalAccessEvent


from .StateChangeEvent import StateChangeEvent


# Resolve forward references


# Only call model_rebuild() if the class has this method (Pydantic models)
if hasattr(GridEvent, "model_rebuild"):
    GridEvent.model_rebuild()


# Public API
__all__ = [
    "AlarmEvent",
    "AnomalyEvent",
    "AuthenticationEvent",
    "ConfigurationEvent",
    "ControlActionEvent",
    "FirmwareEvent",
    "GridEvent",
    "GridProtocolTraffic",
    "GridTelemetry",
    "MaintenanceEvent",
    "PhysicalAccessEvent",
    "StateChangeEvent",
]
