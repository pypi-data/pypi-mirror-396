"""
Differential Evolution Algorithm Variants.

This module organizes DE algorithms into categories:
- classic: Traditional DE variants (DE/rand/1, DE/best/1, etc.)
- adaptive: Self-adaptive parameter control (JADE, SHADE, etc.)
- multi_population: Multi-population and ensemble methods
- hybrid: Hybrid and enhanced variants

Each category contains specialized implementations optimized for
different problem characteristics.
"""

from pyrade.algorithms.classic import (
    ClassicDE,
    DErand1bin,
    DEbest1bin,
    DEcurrentToBest1bin,
    DErand2bin,
    DEbest2bin,
    DEcurrentToRand1bin,
    DERandToBest1bin,
    DErand1exp,
    DErand1EitherOrBin,
)

__all__ = [
    "ClassicDE",
    "DErand1bin",
    "DEbest1bin", 
    "DEcurrentToBest1bin",
    "DErand2bin",
    "DEbest2bin",
    "DEcurrentToRand1bin",
    "DERandToBest1bin",
    "DErand1exp",
    "DErand1EitherOrBin",
]
