# uncertain_variables

[![DOI](https://zenodo.org/badge/1114716179.svg)](https://doi.org/10.5281/zenodo.17904266)

A Python package for defining and handling variable sets with probability distributions for surrogate modelling and uncertainty quantification applications.

- Website: [https://buildchain.ilab.sztaki.hu/](https://buildchain.ilab.sztaki.hu/)
- Source code: [https://github.com/TRACE-Structures/uncertain_variables](https://github.com/TRACE-Structures/uncertain_variables)
- Bug reports: [https://github.com/TRACE-Structures/uncertain_variables/issues](https://github.com/TRACE-Structures/uncertain_variables/issues)

## Overview

The `uncertain_variables` package provides a comprehensive framework for working with random variables and their probability distributions in the context of uncertainty quantification (UQ) and surrogate modelling. It supports various sampling methods, polynomial chaos expansion (PCE) integration, and distribution transformations.

## Features

- **Multiple Distribution Types**: Normal, Uniform, Log-Normal, Beta, Exponential, and Wigner Semicircle distributions
- **Variable Management**: Create and manage sets of variables with associated probability distributions
- **Advanced Sampling Methods**: 
  - Monte Carlo (MC)
  - Quasi-Monte Carlo: Halton, Latin Hypercube (LHS), Sobol sequences
  - Saltelli sampling for sensitivity analysis
- **Polynomial Systems**: Support for orthogonal polynomial systems (Legendre, Hermite, Jacobi, Chebyshev, Laguerre)
- **Space Transformations**: Convert between parameter space, germ space, and standard normal space
- **Unit Conversion**: Built-in support for physical unit conversions using `pint`
- **GPC Integration**: Seamless integration with generalized Polynomial Chaos Expansion methods

## Core Components

### Distribution Classes

The package includes several distribution types in `distributions.py`:

- **`NormalDistribution`**: Gaussian distribution with mean and standard deviation
- **`UniformDistribution`**: Uniform distribution over [min, max]
- **`LogNormalDistribution`**: Log-normal distribution
- **`BetaDistribution`**: Beta distribution with shape parameters
- **`ExponentialDistribution`**: Exponential distribution with rate parameter
- **`WignerSemicircleDistribution`**: Wigner semicircle distribution
- **`TranslatedDistribution`**: Shifted and scaled version of any base distribution

Each distribution supports:
- Probability density function (`pdf`)
- Cumulative distribution function (`cdf`)
- Inverse CDF / Percent point function (`ppf`)
- Moment calculation (`mean`, `var`, `moments`)
- Sampling (`sample`)
- Space transformations (`dist2base`, `base2dist`)

### Variable Class

The `Variable` class represents a single random or deterministic variable:

- Associates a name with a distribution or fixed value
- Supports physical units with automatic conversion
- Provides access to distribution properties (mean, variance, pdf, cdf)
- Enables germ space transformations for polynomial chaos expansions

### VariableSet Class

The `VariableSet` class manages collections of variables:

- Add multiple variables with unique names
- Compute joint statistics (mean vector, variance vector, joint PDF)
- Generate samples using various methods
- Filter and create subsets of variables
- Support polynomial chaos expansion workflows

### Polynomial Systems

The `polysys.py` module implements orthogonal polynomial systems:

- **`LegendrePolynomials`**: For uniform distributions
- **`HermitePolynomials`**: For normal distributions
- **`JacobiPolynomials`**: For beta distributions
- **`ChebyshevTPolynomials`**: Chebyshev polynomials of the first kind
- **`ChebyshevUPolynomials`**: Chebyshev polynomials of the second kind
- **`LaguerrePolynomials`**: For exponential distributions

## Authors and acknowledgment
The code is developed by András Urbanics, Bence Popovics, Emese Vastag, Elmar Zander and Noémi Friedman in the TRACE-Structures group.

The research and the development is founded by the Eurpean Union as part of the BUILDCHAIN project.

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0-only). See the [LICENSE](https://github.com/TRACE-Structures/uncertain_variables/tree/main?tab=GPL-3.0-1-ov-file) file for details.

## Support

For issues, questions, or contributions, please refer to the project repository or contact the authors.
