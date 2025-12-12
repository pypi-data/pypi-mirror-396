"""
Utility module containing boundary handling and termination criteria.
"""

from pyrade.utils.boundary import (
    BoundaryHandler,
    ClipBoundary,
    ReflectBoundary,
    RandomBoundary,
    WrapBoundary,
    MidpointBoundary,
)
from pyrade.utils.termination import (
    TerminationCriterion,
    MaxIterations,
    FitnessThreshold,
    NoImprovement,
    MaxTime,
    FitnessVariance,
)

__all__ = [
    "BoundaryHandler",
    "ClipBoundary",
    "ReflectBoundary",
    "RandomBoundary",
    "WrapBoundary",
    "MidpointBoundary",
    "TerminationCriterion",
    "MaxIterations",
    "FitnessThreshold",
    "NoImprovement",
    "MaxTime",
    "FitnessVariance",
]
