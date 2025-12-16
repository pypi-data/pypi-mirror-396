"""
NeutroLab: A Unified Library for Neutrosophic Learning, Configuration Analysis, and Logical Machines
=====================================================================================================

A comprehensive Python library implementing neutrosophic set theory methods for
transforming crisp data into neutrosophic values, with extensible architecture
for advanced neutrosophic computing.

This library implements the methods described in:
"A Comparative Analysis of Data-Driven and Model-Based Neutrosophication Methods:
Advancing True Neutrosophic Logic in Medical Data Transformation"

Current Neutrosophication Methods:
1. K-Means Clustering with Sigmoid Membership Functions (Proposed - Data-driven)
2. Parabolic Method (Classical - Model-based)
3. Threshold Distance Method (Semi-novel - Model-based)
4. Kernel Density Estimation (KDE) (Established - Density-based)
5. Fuzzy Membership with Triangular Functions (Classical - Model-based)

Future Extensions (Planned):
- Neutrosophic Qualitative Comparative Analysis (QCA)
- Neutrosophic Tsatlin Machine
- Single-Valued Neutrosophic Sets (SVNS) Operations
- Interval-Valued Neutrosophic Sets
- Neutrosophic Cognitive Maps

Authors:
    Maikel Yelandi Leyva-Vázquez (maikel.leyvav@ug.edu.ec)
    Florentin Smarandache

Version: 1.0.0
License: MIT

References:
    [1] Smarandache, F. (1998). Neutrosophy/neutrosophic probability, set, and logic.
    [2] Smarandache, F. (2014). Introduction to Neutrosophic Statistics.
    [3] Wang, H., et al. (2010). Single valued neutrosophic sets.
"""

__version__ = "1.0.0"
__author__ = "Maikel Yelandi Leyva-Vázquez"
__email__ = "maikel.leyvav@ug.edu.ec"
__license__ = "MIT"

# Neutrosophication Methods
from .methods.base import NeutrosophicMethod
from .methods.kmeans import KMeansNeutrosophic
from .methods.parabolic import ParabolicNeutrosophic
from .methods.threshold import ThresholdNeutrosophic
from .methods.kde import KDENeutrosophic
from .methods.fuzzy import FuzzyNeutrosophic

# Utility Functions
from .utils import (
    normalize_data,
    validate_input,
    compute_statistics,
    compare_methods,
    compute_correlation,
    compute_distance,
    compute_tf_consistency
)

__all__ = [
    # Base class
    'NeutrosophicMethod',
    # Neutrosophication methods
    'KMeansNeutrosophic',
    'ParabolicNeutrosophic',
    'ThresholdNeutrosophic',
    'KDENeutrosophic',
    'FuzzyNeutrosophic',
    # Utilities
    'normalize_data',
    'validate_input',
    'compute_statistics',
    'compare_methods',
    'compute_correlation',
    'compute_distance',
    'compute_tf_consistency',
]
