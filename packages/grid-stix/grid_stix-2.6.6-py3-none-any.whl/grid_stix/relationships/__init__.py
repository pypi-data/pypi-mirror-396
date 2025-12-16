"""
grid_stix.relationships - Generated Grid-STIX module

This module was automatically generated from the Grid-STIX ontology.
It contains Python classes corresponding to OWL classes in the ontology.
"""

# Import all classes from this module


from .AffectsOperationOfRelationship import AffectsOperationOfRelationship


from .AggregatesRelationship import AggregatesRelationship


from .AuthenticatesToRelationship import AuthenticatesToRelationship


from .AuthenticatesWithRelationship import AuthenticatesWithRelationship


from .AuthorizesAccessToRelationship import AuthorizesAccessToRelationship


from .CertifiedByRelationship import CertifiedByRelationship


from .ConnectsToRelationship import ConnectsToRelationship


from .ContainedInFacilityRelationship import ContainedInFacilityRelationship


from .ContainsRelationship import ContainsRelationship


from .ControlsRelationship import ControlsRelationship


from .ConvertsForRelationship import ConvertsForRelationship


from .DelegatesAuthorityToRelationship import DelegatesAuthorityToRelationship


from .DependsOnRelationship import DependsOnRelationship


from .EnforcesPolicyOnRelationship import EnforcesPolicyOnRelationship


from .FeedsPowerToRelationship import FeedsPowerToRelationship


from .FeedsRelationship import FeedsRelationship


from .GeneratesPowerForRelationship import GeneratesPowerForRelationship


from .GridRelationship import GridRelationship


from .HasVulnerabilityRelationship import HasVulnerabilityRelationship


from .IslandsFromRelationship import IslandsFromRelationship


from .LocatedAtRelationship import LocatedAtRelationship


from .MonitoredByEnvironmentalSensorRelationship import (
    MonitoredByEnvironmentalSensorRelationship,
)


from .MonitorsRelationship import MonitorsRelationship


from .MonitorsTrustOfRelationship import MonitorsTrustOfRelationship


from .ProducesWasteRelationship import ProducesWasteRelationship


from .ProtectsAssetRelationship import ProtectsAssetRelationship


from .ProtectsRelationship import ProtectsRelationship


from .SuppliedByRelationship import SuppliedByRelationship


from .TriggersRelationship import TriggersRelationship


from .TrustsRelationship import TrustsRelationship


from .UnionAllAssets import UnionAllAssets


from .UnionOTDeviceGridComponent import UnionOTDeviceGridComponent


from .UnionOTDeviceIdentity import UnionOTDeviceIdentity


from .UnionPhysicalAssetGridComponent import UnionPhysicalAssetGridComponent


from .UnionPhysicalAssetOTDevice import UnionPhysicalAssetOTDevice


from .UnionSecurityZoneLocation import UnionSecurityZoneLocation


from .UnionSecurityZoneOTDeviceCourseOfAction import (
    UnionSecurityZoneOTDeviceCourseOfAction,
)


from .VerifiesIdentityOfRelationship import VerifiesIdentityOfRelationship


from .WithinSecurityZoneRelationship import WithinSecurityZoneRelationship


# Resolve forward references


# Only call model_rebuild() if the class has this method (Pydantic models)
if hasattr(UnionAllAssets, "model_rebuild"):
    UnionAllAssets.model_rebuild()


# Only call model_rebuild() if the class has this method (Pydantic models)
if hasattr(UnionPhysicalAssetGridComponent, "model_rebuild"):
    UnionPhysicalAssetGridComponent.model_rebuild()


# Public API
__all__ = [
    "AffectsOperationOfRelationship",
    "AggregatesRelationship",
    "AuthenticatesToRelationship",
    "AuthenticatesWithRelationship",
    "AuthorizesAccessToRelationship",
    "CertifiedByRelationship",
    "ConnectsToRelationship",
    "ContainedInFacilityRelationship",
    "ContainsRelationship",
    "ControlsRelationship",
    "ConvertsForRelationship",
    "DelegatesAuthorityToRelationship",
    "DependsOnRelationship",
    "EnforcesPolicyOnRelationship",
    "FeedsPowerToRelationship",
    "FeedsRelationship",
    "GeneratesPowerForRelationship",
    "GridRelationship",
    "HasVulnerabilityRelationship",
    "IslandsFromRelationship",
    "LocatedAtRelationship",
    "MonitoredByEnvironmentalSensorRelationship",
    "MonitorsRelationship",
    "MonitorsTrustOfRelationship",
    "ProducesWasteRelationship",
    "ProtectsAssetRelationship",
    "ProtectsRelationship",
    "SuppliedByRelationship",
    "TriggersRelationship",
    "TrustsRelationship",
    "UnionAllAssets",
    "UnionOTDeviceGridComponent",
    "UnionOTDeviceIdentity",
    "UnionPhysicalAssetGridComponent",
    "UnionPhysicalAssetOTDevice",
    "UnionSecurityZoneLocation",
    "UnionSecurityZoneOTDeviceCourseOfAction",
    "VerifiesIdentityOfRelationship",
    "WithinSecurityZoneRelationship",
]
