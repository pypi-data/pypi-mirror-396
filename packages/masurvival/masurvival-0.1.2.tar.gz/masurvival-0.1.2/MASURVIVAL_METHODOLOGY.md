# Missingness-Avoiding Survival Forest (MASurvival) Methodology

## Overview

The **Missingness-Avoiding Survival Forest (MASurvival)** is an extension of the Random Survival Forest algorithm that introduces a regularization mechanism to penalize splits on features with missing values. This approach allows the model to naturally avoid using features with high missingness rates during tree construction, without requiring explicit imputation or feature removal.

## Core Concept

Traditional survival forests handle missing values by routing them to child nodes based on impurity minimization. However, this approach doesn't explicitly discourage the use of features with many missing values. MASurvival introduces an **alpha (α) hyperparameter** that penalizes splits based on the number of missing values in a feature, encouraging the model to prefer features with complete data.

## Mathematical Formulation

### Standard Survival Forest Split Selection

In a standard survival forest, at each node, the algorithm selects the split that maximizes the **impurity improvement**:

```
best_split = argmax(impurity_improvement(feature, threshold))
```

The impurity improvement is typically measured using the log-rank statistic for survival data.

### MASurvival Split Selection

MASurvival modifies the split selection criterion by subtracting a penalty proportional to the number of missing values:

```
penalized_improvement = impurity_improvement - (α × n_missing)
```

Where:
- `impurity_improvement`: The standard log-rank improvement from the split
- `α` (alpha): The missingness-avoidance penalty coefficient (hyperparameter)
- `n_missing`: The number of samples with missing values for the feature in the current node

The algorithm then selects:

```
best_split = argmax(penalized_improvement)
```

### Effect of Alpha

- **α = 0**: No penalty applied. MASurvival behaves identically to a standard survival forest.
- **α > 0**: Features with missing values are penalized. Higher α values result in stronger avoidance of missing features.
- **α → ∞**: The model will completely avoid any feature with missing values (equivalent to feature removal).

## Implementation Details

### 1. Split Evaluation

For each candidate feature and threshold, the algorithm:

1. Calculates the standard impurity improvement using the log-rank criterion
2. Counts the number of missing values (`n_missing`) for that feature in the current node
3. Applies the penalty: `penalized_improvement = impurity_improvement - (α × n_missing)`
4. Selects the split with the highest penalized improvement

### 2. Missing Value Handling

MASurvival still handles missing values during tree construction:
- Missing values are routed to child nodes based on which assignment minimizes impurity
- The penalty is applied **per feature**, not per split threshold
- The penalty is proportional to the total number of missing values in the node for that feature

### 3. Code Implementation

The key modification is in the splitter's `node_split` function:

```cython
# Calculate standard impurity improvement
current_proxy_improvement = criterion.proxy_impurity_improvement()

# Apply missingness-avoidance penalty
if alpha > 0.0 and n_missing > 0:
    current_proxy_improvement = current_proxy_improvement - (alpha * n_missing)

# Select split with highest penalized improvement
if current_proxy_improvement > best_proxy_improvement:
    best_proxy_improvement = current_proxy_improvement
    best_split = current_split
```

## Advantages

1. **No Preprocessing Required**: Unlike imputation methods, MASurvival doesn't require filling missing values before training.

2. **Adaptive Feature Selection**: The model automatically learns to avoid features with high missingness when they don't provide sufficient benefit to overcome the penalty.

3. **Maintains Information**: Unlike feature removal, MASurvival can still use features with missing values if they provide substantial predictive power (i.e., if `impurity_improvement > α × n_missing`).

4. **Tunable Regularization**: The α parameter provides a continuous control between:
   - Standard survival forest behavior (α = 0)
   - Complete avoidance of missing features (α → ∞)

## Hyperparameter Selection

The optimal α value can be selected through:
- **Cross-validation**: Evaluate performance across different α values
- **Grid search**: Test a range of α values (e.g., 0.0, 0.1, 0.2, ..., 1.0)
- **Performance-based selection**: Choose α that maximizes C-index on validation/test sets

In your analysis, α = 0.1 was selected based on mean C-index performance across both PACAP and NCR test sets.

## Comparison with Alternative Strategies

### MASurvival vs. Feature Removal
- **Feature Removal**: Completely excludes features with missing values
- **MASurvival**: Allows use of features with missing values if beneficial, but penalizes them
- **Result**: MASurvival can outperform feature removal when missing features still provide useful information

### MASurvival vs. Imputation
- **Imputation**: Fills missing values with estimated values (e.g., mean)
- **MASurvival**: Avoids using missing features without imputing
- **Result**: MASurvival avoids potential bias from imputation while still leveraging complete features

## Performance Characteristics

Based on your results:

- **PACAP Test Set**: 
  - MASurvival (α=0.1): C-index = 0.670 ± 0.013
  - Significantly outperforms Feature Removal (p < 0.001)
  - No significant difference from Imputation (p = 0.279)

- **NCR Test Set**:
  - MASurvival (α=0.1): C-index = 0.722 ± 0.002
  - No significant differences from other strategies (all p ≥ 0.05)

## Technical Architecture

MASurvival is implemented by:
1. **Forking scikit-learn's tree modules**: Custom Cython implementations of `_splitter.pyx`, `_tree.pyx`, and related modules to support the α parameter
2. **Modifying the splitter**: Adding α to the splitter's `__cinit__` method and applying the penalty in `node_split_best` and `node_split_random` functions
3. **Extending SurvivalTree**: Adding α as a hyperparameter to the `SurvivalTree` class and passing it to the splitter during tree construction

## References

The implementation is based on:
- Random Survival Forests (Ishwaran et al., 2008)
- scikit-survival library (Pölsterl, 2020)
- scikit-learn's tree implementation

## Usage Example

```python
from masurvival.ensemble import RandomSurvivalForest

# Create MASurvival model with alpha=0.1
rsf = RandomSurvivalForest(
    n_estimators=100,
    alpha=0.1,  # Missingness-avoidance penalty
    random_state=42
)

# Train on data with missing values (no imputation needed)
rsf.fit(X_train, y_train)

# Predict risk scores
risk_scores = rsf.predict(X_test)
```

## Summary

MASurvival provides a principled approach to handling missing values in survival forests by introducing a regularization penalty that discourages splits on features with missing data. This allows the model to automatically balance the trade-off between using informative features with missing values versus avoiding them entirely, leading to improved performance in scenarios with high missingness rates.


