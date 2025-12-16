# Changelog

All notable changes to NeutroLab will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-10

### Added
- Initial release of NeutroLab library
- Five neutrosophication methods as described in the paper:
  - **KMeansNeutrosophic**: K-Means clustering with sigmoid membership functions (Proposed)
    - Achieves TRUE independence of T, I, F components
    - Equations 2, 3, 4 from paper
  - **ParabolicNeutrosophic**: Classical parabolic approach (Equation 5)
  - **ThresholdNeutrosophic**: Threshold distance method (Equation 7)
  - **KDENeutrosophic**: Kernel density estimation approach (Equations 8-11)
  - **FuzzyNeutrosophic**: Fuzzy membership with triangular functions (Equation 12)
- Utility functions:
  - `normalize_data()`: Min-Max normalization (Equation 1)
  - `validate_input()`: Input validation and reshaping
  - `compute_statistics()`: Statistical analysis including metrics from paper
  - `compare_methods()`: Method comparison utility
  - `compute_correlation()`: Correlation between indeterminacy distributions
  - `compute_distance()`: Distance metrics between neutrosophic sets
  - `compute_tf_consistency()`: T+F Consistency metric (Equation 13)
- Comprehensive test suite verifying conformity with paper formulas
- Full type hints support
- MIT License

### Paper Reference
Based on: "A Comparative Analysis of Data-Driven and Model-Based Neutrosophication 
Methods: Advancing True Neutrosophic Logic in Medical Data Transformation"

Authors: Leyva-Vázquez, M. Y., Cevallos-Torres, L., Mar Cornelio, O., & Smarandache, F.

## [Planned] Future Releases

### [1.1.0] - Planned
- Neutrosophic Qualitative Comparative Analysis (QCA)
- Enhanced visualization utilities

### [1.2.0] - Planned
- Neutrosophic Tsatlin Machine
- Single-Valued Neutrosophic Sets (SVNS) operations

### [2.0.0] - Planned
- Interval-Valued Neutrosophic Sets
- Neutrosophic Cognitive Maps
- Multi-criteria decision making tools
