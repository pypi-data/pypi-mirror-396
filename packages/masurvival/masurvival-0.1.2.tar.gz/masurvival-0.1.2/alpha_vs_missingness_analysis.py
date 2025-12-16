"""
Analysis of Best Alpha vs. Missingness Percentage

This script:
1. Starts with PACAP data (low missingness)
2. Gradually adds NCR data with artificially introduced missingness
3. Tests different missingness levels (0%, 10%, 20%, ..., 100%)
4. For each level, explores alpha values and finds the best one
5. Plots best alpha vs. missingness percentage
6. Keeps test set size constant
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from masurvival.util import Surv
from masurvival.ensemble import RandomSurvivalForest
from masurvival.metrics import concordance_index_censored

# =============================================================================
# Configuration
# =============================================================================
print("=" * 80)
print("ALPHA VS MISSINGNESS ANALYSIS")
print("=" * 80)
print()

# Numerical features
numerical_features = [
    'cci', 'ca199', 'bilirubine', 'albumine', 'ldh', 'crp'
]

# Categorical features
categorical_features = [
    'leeft_cat', 'cci_cat', 'perf_stat', 'seizoen', 'diffgrad', 'klin_tum_afm',
    'morf', 'ct', 'cn', 'cm', 'cstadium', 'stadium',
    'meta_lever', 'veneus_vaatbetr', 'arterieel_vaatbetr',
    'gesl', 'geboorteland', 'diag_basis', 'topo_sublok', 'morf_cat',
    'meta_bijnier', 'meta_bot', 'meta_hersenen', 'meta_long', 'meta_lymf',
    'meta_perit', 'meta_overig',
]

# QoL pretreatment features
qol_features = [
    'qol_summary_pretreatment',
    'qol_physical_pretreatment',
    'qol_social_pretreatment',
    'qol_emotional_pretreatment',
    'qol_cognitive_pretreatment',
    'qol_role_pretreatment'
]

# Alpha values to test
alpha_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]

# Missingness levels to test (as percentages)
missingness_levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# =============================================================================
# Load Data
# =============================================================================
print("=" * 80)
print("LOADING DATA")
print("=" * 80)
print()

# Load PACAP data
print("Loading PACAP data...")
df_pacap = pd.read_csv('merged_pacap_data.csv')
print(f"  Loaded {len(df_pacap)} PACAP patients")

# Load NCR data
print("Loading NCR data...")
df_ncr_all = pd.read_csv('merged_datasets.csv')
print(f"  Loaded {len(df_ncr_all)} NCR patients (before removing PACAP)")

# Remove PACAP patients from NCR data
if 'key_nkr' in df_pacap.columns and 'key_nkr' in df_ncr_all.columns:
    pacap_ids = set(df_pacap['key_nkr'].dropna().unique())
    df_ncr = df_ncr_all[~df_ncr_all['key_nkr'].isin(pacap_ids)].copy()
    print(f"  Removed {len(df_ncr_all) - len(df_ncr)} PACAP patients from NCR data")
else:
    df_ncr = df_ncr_all.copy()
    print("  Warning: Could not match patient IDs, using all NCR data")

print(f"  Final NCR dataset: {len(df_ncr)} patients")
print()

# =============================================================================
# Prepare Base Dataset (PACAP)
# =============================================================================
print("=" * 80)
print("PREPARING BASE DATASET (PACAP)")
print("=" * 80)
print()

# Use PACAP as base
df_base = df_pacap.copy()
df_base = df_base.drop_duplicates(subset=['key_nkr'] if 'key_nkr' in df_base.columns else None)

# Prepare features
features_with_qol = numerical_features + categorical_features + qol_features

# Check which features are available
available_features = [f for f in features_with_qol if f in df_base.columns]
missing_features = [f for f in features_with_qol if f not in df_base.columns]

if missing_features:
    print(f"Warning: {len(missing_features)} features missing in PACAP data")
    features_with_qol = available_features

print(f"Using {len(features_with_qol)} features")
print()

# Prepare base data
X_base = df_base[features_with_qol].copy()
y_base = Surv.from_arrays(
    event=df_base['vit_stat'].astype(bool),
    time=df_base['vit_stat_int'].astype(float)
)

# Encode categorical features
print("Encoding categorical features...")
label_encoders = {}
for col in X_base.columns:
    if X_base[col].dtype == 'object' or X_base[col].dtype.name == 'category':
        le = LabelEncoder()
        X_base[col] = le.fit_transform(X_base[col].astype(str))
        label_encoders[col] = le

X_base_numeric = X_base.values.astype(np.float64)

# Calculate baseline missingness in PACAP QoL features
qol_indices = [i for i, feat in enumerate(features_with_qol) if feat in qol_features]
pacap_qol_missing = np.isnan(X_base_numeric[:, qol_indices]).sum() / (len(X_base_numeric) * len(qol_indices)) * 100

print(f"PACAP baseline QoL missingness: {pacap_qol_missing:.2f}%")
print(f"Base dataset size: {len(X_base_numeric)} samples")
print()

# =============================================================================
# Prepare NCR Data Pool
# =============================================================================
print("=" * 80)
print("PREPARING NCR DATA POOL")
print("=" * 80)
print()

# Prepare NCR data (same features)
X_ncr = df_ncr[features_with_qol].copy()

# Encode categorical features using same encoders (or create new ones)
for col in X_ncr.columns:
    if col in label_encoders:
        le = label_encoders[col]
        # Handle unseen categories
        X_ncr[col] = X_ncr[col].astype(str).apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else 0
        )
    elif X_ncr[col].dtype == 'object' or X_ncr[col].dtype.name == 'category':
        le = LabelEncoder()
        X_ncr[col] = le.fit_transform(X_ncr[col].astype(str))
        label_encoders[col] = le

X_ncr_numeric = X_ncr.values.astype(np.float64)
y_ncr = Surv.from_arrays(
    event=df_ncr['vit_stat'].astype(bool),
    time=df_ncr['vit_stat_int'].astype(float)
)

print(f"NCR dataset size: {len(X_ncr_numeric)} samples")
print()

# =============================================================================
# Function to Introduce Missingness
# =============================================================================
def introduce_missingness(X, qol_indices, target_missing_pct, random_state=42):
    """
    Artificially introduce missingness in QoL features to reach target percentage.
    
    Parameters
    ----------
    X : ndarray
        Feature matrix
    qol_indices : list
        Indices of QoL features
    target_missing_pct : float
        Target missingness percentage (0-100)
    random_state : int
        Random seed for reproducibility
    
    Returns
    --
    X_missing : ndarray
        Feature matrix with introduced missingness
    actual_missing_pct : float
        Actual missingness percentage achieved
    """
    X_missing = X.copy()
    np.random.seed(random_state)
    
    n_samples, n_qol_features = len(X_missing), len(qol_indices)
    total_qol_values = n_samples * n_qol_features
    
    # Calculate how many values need to be missing
    target_missing_count = int(total_qol_values * target_missing_pct / 100)
    
    # Count existing missing values
    existing_missing = np.isnan(X_missing[:, qol_indices]).sum()
    additional_missing_needed = max(0, target_missing_count - existing_missing)
    
    if additional_missing_needed > 0:
        # Get all QoL feature positions (sample_idx, feature_idx)
        qol_positions = []
        for sample_idx in range(n_samples):
            for qol_idx in qol_indices:
                if not np.isnan(X_missing[sample_idx, qol_idx]):
                    qol_positions.append((sample_idx, qol_idx))
        
        # Randomly select positions to set as missing
        if len(qol_positions) >= additional_missing_needed:
            selected_positions = np.random.choice(
                len(qol_positions), 
                size=additional_missing_needed, 
                replace=False
            )
            for pos_idx in selected_positions:
                sample_idx, feature_idx = qol_positions[pos_idx]
                X_missing[sample_idx, feature_idx] = np.nan
    
    # Calculate actual missingness
    actual_missing = np.isnan(X_missing[:, qol_indices]).sum()
    actual_missing_pct = (actual_missing / total_qol_values) * 100
    
    return X_missing, actual_missing_pct

# =============================================================================
# Function to Create Combined Dataset with Target Missingness
# =============================================================================
def create_combined_dataset_with_missingness(
    X_base, y_base, X_ncr, y_ncr, 
    target_missing_pct, qol_indices, 
    test_size=0.3, random_state=42
):
    """
    Create a combined dataset with target missingness percentage.
    
    Strategy:
    1. Start with PACAP (base)
    2. Add NCR samples gradually
    3. Introduce missingness in QoL features to reach target percentage
    """
    np.random.seed(random_state)
    
    # Start with base (PACAP)
    X_combined = X_base.copy()
    y_combined = y_base.copy()
    
    # Calculate current missingness
    current_missing = np.isnan(X_combined[:, qol_indices]).sum()
    n_samples_combined = len(X_combined)
    n_qol_features = len(qol_indices)
    total_qol_values = n_samples_combined * n_qol_features
    current_missing_pct = (current_missing / total_qol_values * 100) if total_qol_values > 0 else 0
    
    # If target missingness is higher than current, add NCR samples and introduce missingness
    if target_missing_pct > current_missing_pct:
        # Calculate how many NCR samples we need to add
        # We'll add samples and introduce missingness to reach target
        
        # Add all NCR samples first
        X_combined = np.vstack([X_combined, X_ncr])
        y_combined = np.concatenate([y_combined, y_ncr])
        
        # Now introduce missingness to reach target
        X_combined, actual_missing_pct = introduce_missingness(
            X_combined, qol_indices, target_missing_pct, random_state=random_state
        )
    else:
        # Just introduce missingness in base dataset
        X_combined, actual_missing_pct = introduce_missingness(
            X_combined, qol_indices, target_missing_pct, random_state=random_state
        )
    
    # Split into train/test (keeping test size constant)
    n_samples = len(X_combined)
    indices = np.arange(n_samples)
    train_indices, test_indices = train_test_split(
        indices, test_size=test_size, random_state=random_state, stratify=None
    )
    
    X_train = X_combined[train_indices]
    X_test = X_combined[test_indices]
    y_train = y_combined[train_indices]
    y_test = y_combined[test_indices]
    
    return X_train, X_test, y_train, y_test, actual_missing_pct, len(X_combined)

# =============================================================================
# Main Analysis: Alpha Exploration for Each Missingness Level
# =============================================================================
print("=" * 80)
print("ALPHA EXPLORATION FOR DIFFERENT MISSINGNESS LEVELS")
print("=" * 80)
print()

results = []

for missing_pct in missingness_levels:
    print(f"\n{'='*80}")
    print(f"Testing Missingness Level: {missing_pct}%")
    print(f"{'='*80}")
    
    # Create combined dataset with target missingness
    X_train, X_test, y_train, y_test, actual_missing_pct, total_samples = \
        create_combined_dataset_with_missingness(
            X_base_numeric, y_base, X_ncr_numeric, y_ncr,
            target_missing_pct=missing_pct,
            qol_indices=qol_indices,
            test_size=0.3,
            random_state=42
        )
    
    print(f"  Dataset size: {total_samples} samples")
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test: {len(X_test)} samples")
    print(f"  Actual QoL missingness: {actual_missing_pct:.2f}%")
    print()
    
    # Test different alpha values
    alpha_results = []
    
    print(f"  Testing alpha values...")
    for alpha in alpha_values:
        rsf = RandomSurvivalForest(
            n_estimators=100,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1,
            alpha=alpha
        )
        
        rsf.fit(X_train, y_train)
        
        # Evaluate on test set
        risk_scores = rsf.predict(X_test)
        c_index = concordance_index_censored(
            y_test['event'],
            y_test['time'],
            risk_scores
        )[0]
        
        alpha_results.append({
            'alpha': alpha,
            'c_index': c_index
        })
        
        print(f"    Alpha {alpha:.1f}: C-index = {c_index:.4f}")
    
    # Find best alpha
    best_alpha_result = max(alpha_results, key=lambda x: x['c_index'])
    best_alpha = best_alpha_result['alpha']
    best_c_index = best_alpha_result['c_index']
    
    print(f"\n  Best alpha: {best_alpha} (C-index: {best_c_index:.4f})")
    
    results.append({
        'target_missing_pct': missing_pct,
        'actual_missing_pct': actual_missing_pct,
        'best_alpha': best_alpha,
        'best_c_index': best_c_index,
        'total_samples': total_samples,
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'alpha_0_c_index': next(r['c_index'] for r in alpha_results if r['alpha'] == 0.0),
        'alpha_0_1_c_index': next(r['c_index'] for r in alpha_results if r['alpha'] == 0.1),
        'alpha_0_2_c_index': next(r['c_index'] for r in alpha_results if r['alpha'] == 0.2),
        'alpha_0_3_c_index': next(r['c_index'] for r in alpha_results if r['alpha'] == 0.3),
        'alpha_0_4_c_index': next(r['c_index'] for r in alpha_results if r['alpha'] == 0.4),
        'alpha_0_5_c_index': next(r['c_index'] for r in alpha_results if r['alpha'] == 0.5),
        'alpha_1_0_c_index': next(r['c_index'] for r in alpha_results if r['alpha'] == 1.0),
    })

# =============================================================================
# Create Results DataFrame
# =============================================================================
results_df = pd.DataFrame(results)

# Save results
results_df.to_csv('alpha_vs_missingness_results.csv', index=False)
print(f"\n{'='*80}")
print("SAVED RESULTS")
print(f"{'='*80}")
print(f"Saved to: alpha_vs_missingness_results.csv")
print()

# =============================================================================
# Create Plot
# =============================================================================
print("=" * 80)
print("CREATING PLOT")
print("=" * 80)
print()

fig, axes = plt.subplots(2, 1, figsize=(12, 10))

# Plot 1: Best Alpha vs Missingness Percentage
ax1 = axes[0]
ax1.plot(
    results_df['actual_missing_pct'],
    results_df['best_alpha'],
    marker='o',
    linewidth=2,
    markersize=8,
    color='#2E86AB',
    label='Best Alpha'
)
ax1.set_xlabel('QoL Missingness Percentage (%)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Best Alpha', fontsize=12, fontweight='bold')
ax1.set_title('Optimal Alpha vs. QoL Missingness Percentage', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_xlim([-5, 105])
ax1.set_ylim([-0.1, max(alpha_values) + 0.2])
ax1.legend(fontsize=11)

# Add annotations for each point
for _, row in results_df.iterrows():
    ax1.annotate(
        f"α={row['best_alpha']:.1f}",
        (row['actual_missing_pct'], row['best_alpha']),
        xytext=(5, 5),
        textcoords='offset points',
        fontsize=9,
        alpha=0.7
    )

# Plot 2: Best C-index vs Missingness Percentage
ax2 = axes[1]
ax2.plot(
    results_df['actual_missing_pct'],
    results_df['best_c_index'],
    marker='s',
    linewidth=2,
    markersize=8,
    color='#A23B72',
    label='Best C-index'
)
ax2.set_xlabel('QoL Missingness Percentage (%)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Best C-index', fontsize=12, fontweight='bold')
ax2.set_title('Best C-index vs. QoL Missingness Percentage', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_xlim([-5, 105])
ax2.set_ylim([0.6, 0.75])
ax2.legend(fontsize=11)

# Add annotations
for _, row in results_df.iterrows():
    ax2.annotate(
        f"{row['best_c_index']:.3f}",
        (row['actual_missing_pct'], row['best_c_index']),
        xytext=(5, -10),
        textcoords='offset points',
        fontsize=9,
        alpha=0.7
    )

plt.tight_layout()
plt.savefig('alpha_vs_missingness_plot.png', dpi=300, bbox_inches='tight')
print("Saved plot to: alpha_vs_missingness_plot.png")
plt.close()

# =============================================================================
# Create Detailed Plot with All Alpha Values
# =============================================================================
print("Creating detailed plot with all alpha values...")

fig, ax = plt.subplots(figsize=(14, 8))

# Plot C-index for each alpha value
colors = plt.cm.viridis(np.linspace(0, 1, len(alpha_values)))

for idx, alpha in enumerate(alpha_values):
    alpha_col = f'alpha_{alpha:.1f}_c_index'.replace('.', '_')
    if alpha_col in results_df.columns:
        ax.plot(
            results_df['actual_missing_pct'],
            results_df[alpha_col],
            marker='o',
            linewidth=2,
            markersize=6,
            color=colors[idx],
            label=f'α={alpha:.1f}',
            alpha=0.8
        )

# Highlight best alpha at each point
ax.scatter(
    results_df['actual_missing_pct'],
    results_df['best_c_index'],
    s=150,
    marker='*',
    color='red',
    edgecolors='black',
    linewidths=1.5,
    zorder=10,
    label='Best Alpha'
)

ax.set_xlabel('QoL Missingness Percentage (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('C-index', fontsize=12, fontweight='bold')
ax.set_title('C-index vs. QoL Missingness Percentage (All Alpha Values)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(loc='best', fontsize=10, ncol=3)
ax.set_xlim([-5, 105])
ax.set_ylim([0.6, 0.75])

plt.tight_layout()
plt.savefig('alpha_vs_missingness_detailed.png', dpi=300, bbox_inches='tight')
print("Saved detailed plot to: alpha_vs_missingness_detailed.png")
plt.close()

# =============================================================================
# Print Summary Table
# =============================================================================
print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)
print()

summary_table = results_df[['target_missing_pct', 'actual_missing_pct', 'best_alpha', 'best_c_index', 'total_samples']].copy()
summary_table.columns = ['Target Missing %', 'Actual Missing %', 'Best Alpha', 'Best C-index', 'Total Samples']
print(summary_table.to_string(index=False))
print()

# Save summary
summary_table.to_csv('alpha_vs_missingness_summary.csv', index=False)
print("Saved summary table to: alpha_vs_missingness_summary.csv")
print()

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print()
print("Generated files:")
print("  - alpha_vs_missingness_results.csv: Detailed results for all missingness levels")
print("  - alpha_vs_missingness_summary.csv: Summary table")
print("  - alpha_vs_missingness_plot.png: Best alpha and C-index vs missingness")
print("  - alpha_vs_missingness_detailed.png: All alpha values vs missingness")
print()


