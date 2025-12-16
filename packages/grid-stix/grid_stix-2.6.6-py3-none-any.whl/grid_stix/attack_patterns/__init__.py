"""
grid_stix.attack_patterns - Generated Grid-STIX module

This module was automatically generated from the Grid-STIX ontology.
It contains Python classes corresponding to OWL classes in the ontology.
"""

# Import all classes from this module


from .CyberAttackPattern import CyberAttackPattern


from .FirmwareAttackPattern import FirmwareAttackPattern


from .GridAttackPattern import GridAttackPattern


from .GridMitigation import GridMitigation


from .ImpactType import ImpactType


from .PhysicalAttackPattern import PhysicalAttackPattern


from .ProtocolAttackPattern import ProtocolAttackPattern


from .SocialEngineeringAttackPattern import SocialEngineeringAttackPattern


# Resolve forward references


# Only call model_rebuild() if the class has this method (Pydantic models)
if hasattr(GridAttackPattern, "model_rebuild"):
    GridAttackPattern.model_rebuild()


# Only call model_rebuild() if the class has this method (Pydantic models)
if hasattr(GridMitigation, "model_rebuild"):
    GridMitigation.model_rebuild()


# Public API
__all__ = [
    "CyberAttackPattern",
    "FirmwareAttackPattern",
    "GridAttackPattern",
    "GridMitigation",
    "ImpactType",
    "PhysicalAttackPattern",
    "ProtocolAttackPattern",
    "SocialEngineeringAttackPattern",
]
