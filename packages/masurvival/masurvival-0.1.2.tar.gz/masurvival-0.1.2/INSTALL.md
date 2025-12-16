# Installing MASurvival Package

This package provides Missingness-Avoiding Survival Forest, an extension of scikit-survival with missingness-avoidance regularization.

## Installation Steps

### 1. Rename the Package Directory (if not already done)

If the directory is still named `sksurv`, run:

```bash
python rename_package.py
```

This will:
- Rename `sksurv/` to `masurvival/`
- Update all internal imports

### 2. Install the Package

#### Option A: Install in Editable Mode (Recommended for Development)

From the project root directory:

```bash
pip install -e .
```

This installs the package in "editable" mode, so changes to the code are immediately available without reinstalling.

#### Option B: Build and Install

```bash
pip install build
python -m build
pip install dist/masurvival-*.whl
```

### 3. Verify Installation

```python
from masurvival.ensemble import RandomSurvivalForest
from masurvival.datasets import load_breast_cancer

# Test that it works
X, y = load_breast_cancer()
print("Package installed successfully!")
```

## Using in Other Projects

Once installed, you can use MASurvival in any Python project:

```python
from masurvival.ensemble import RandomSurvivalForest
from masurvival.metrics import concordance_index_censored

# Create a model with missingness-avoidance regularization
rsf = RandomSurvivalForest(
    n_estimators=100,
    alpha=1.0,  # Missingness-avoidance parameter
    random_state=42
)

# Train and use as normal
rsf.fit(X_train, y_train)
predictions = rsf.predict(X_test)
```

## Key Features

- **Missingness-Avoidance Regularization**: The `alpha` parameter penalizes splits on features with missing values
- **Compatible API**: Works as a drop-in replacement for `RandomSurvivalForest` from scikit-survival
- **All Original Features**: Includes all features from scikit-survival

## Requirements

- Python >= 3.10
- Cython >= 3.0.10
- NumPy >= 2.0.0
- scikit-learn >= 1.6.1, < 1.8
- And other dependencies (see `pyproject.toml`)

## Troubleshooting

### Import Errors

If you get import errors, make sure:
1. The directory is renamed to `masurvival/`
2. The package is installed: `pip install -e .`
3. You're using the correct import: `from masurvival.ensemble import RandomSurvivalForest`

### Compilation Errors

If you encounter Cython compilation errors:
1. Make sure Cython is installed: `pip install Cython>=3.0.10`
2. Make sure you have a C++ compiler (Visual Studio Build Tools on Windows)
3. Try cleaning and rebuilding: `python setup.py clean` then `pip install -e .`




