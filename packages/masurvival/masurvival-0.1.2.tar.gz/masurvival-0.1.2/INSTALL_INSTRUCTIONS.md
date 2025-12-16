# Installing MASurvival Package

## Quick Installation (Recommended)

### For Python 3.11 or earlier (or with NumPy 1.x):

```bash
# Install in editable mode (recommended for development)
pip install -e .
```

This will:
- Build all Cython extensions automatically
- Install the package in editable mode (changes take effect immediately)
- Install all dependencies

### For Python 3.13 with NumPy 2.x (Current Issue):

The package has compatibility issues with NumPy 2.x. You have two options:

#### Option 1: Downgrade NumPy (Quickest Fix)

```bash
# Downgrade NumPy to 1.x
pip install "numpy<2.0"

# Then install the package
pip install -e .
```

#### Option 2: Use Python 3.11 Environment

```bash
# Create a new environment with Python 3.11
conda create -n masurvival python=3.11
conda activate masurvival

# Install dependencies
pip install "numpy<2.0" "Cython>=3.0.10" "packaging>=24.2"

# Install the package
pip install -e .
```

## Verify Installation

After installation, verify it works:

```python
from masurvival.ensemble import RandomSurvivalForest
print("MASurvival installed successfully!")
```

## Building Extensions Manually (if needed)

If you encounter issues during installation, you can build extensions manually:

```bash
# Build all extensions
python setup.py build_ext --inplace

# Or build only specific extensions needed for RandomSurvivalForest
python build_coxnet_only.py
```

## Installation Methods

### 1. Editable Installation (Development Mode)
```bash
pip install -e .
```
- Changes to source code are immediately available
- Best for development
- Extensions are built automatically

### 2. Regular Installation
```bash
pip install .
```
- Installs as a regular package
- Changes require reinstallation
- Extensions are built automatically

### 3. Build Wheel and Install
```bash
pip install build
python -m build
pip install dist/masurvival-*.whl
```
- Creates a distributable wheel file
- Can be shared with others
- Extensions are pre-compiled

## Troubleshooting

### Issue: NumPy 2.x Compatibility Error
**Error**: `'subarray': is not a member of '_PyArray_Descr'`

**Solution**: Downgrade NumPy to 1.x:
```bash
pip install "numpy<2.0"
```

### Issue: Missing Cython
**Error**: `ModuleNotFoundError: No module named 'Cython'`

**Solution**: Install Cython:
```bash
pip install "Cython>=3.0.10"
```

### Issue: Missing Eigen Library
**Error**: `eigen/Eigen directory not found`

**Solution**: Initialize git submodules:
```bash
git submodule update --init --recursive
```

### Issue: Missing Compiled Extensions
**Error**: `ModuleNotFoundError: No module named 'masurvival.linear_model._coxnet'`

**Solution**: Build extensions manually:
```bash
python setup.py build_ext --inplace
```

## Dependencies

Required dependencies (installed automatically):
- numpy (>=1.20.0, <2.0 for compatibility)
- pandas (>=2.0.0)
- scikit-learn (>=1.6.1, <1.8)
- scipy (>=1.3.2)
- Cython (>=3.0.10)
- joblib
- numexpr
- ecos
- osqp (>=1.0.2)

## Notes

- The package uses `setuptools-scm` for version management
- All Cython extensions are built during installation
- The package is compatible with Python 3.10, 3.11, 3.12, and 3.13
- NumPy 2.x compatibility is being worked on but not yet fully supported


