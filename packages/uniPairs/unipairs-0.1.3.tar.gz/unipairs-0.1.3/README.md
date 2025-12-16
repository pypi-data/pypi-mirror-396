# uniPairs

_Univariate–guided interaction modeling in Python._

`uniPairs` implements procedures for discovering and estimating pairwise interactions in high-dimensional generalized linear models, built on top of the [`adelie`](https://jamesyang007.github.io/adelie) library.

The package provides:

- **UniLasso**
- **Lasso / GLM wrappers** over `adelie.grpnet` for Gaussian, binomial and Cox models  
- **UniPairs (one-stage and two-stage)** interaction models:
  - support for Gaussian, logistic, and Cox regression

---

## Installation

```bash
pip install uniPairs
