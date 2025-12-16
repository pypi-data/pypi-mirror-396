"""
Combined PACAP and NCR Analysis Script

This script:
1. Combines PACAP and NCR datasets
2. Explores different alpha values for MASurvival
3. Selects best alpha based on performance
4. Runs k-fold cross-validation with best alpha
5. Reports missing value percentages
6. Generates results tables
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder
from masurvival.util import Surv
from masurvival.ensemble import RandomSurvivalForest
from masurvival.metrics import concordance_index_censored

# =============================================================================
# Configuration
# =============================================================================
print("=" * 80)
print("COMBINED PACAP AND NCR ANALYSIS")
print("=" * 80)
print()

# Numerical features (baseline clinical variables)
numerical_features = [
    'cci', 'ca199', 'bilirubine', 'albumine', 'ldh', 'crp'
]

# Categorical features (baseline clinical variables)
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

# Feature name translations (Dutch to English)
FEATURE_TRANSLATIONS = {
    'qol_summary_pretreatment': 'QoL Summary Score (Pretreatment)',
    'qol_physical_pretreatment': 'QoL Physical (Pretreatment)',
    'qol_social_pretreatment': 'QoL Social (Pretreatment)',
    'qol_emotional_pretreatment': 'QoL Emotional (Pretreatment)',
    'qol_cognitive_pretreatment': 'QoL Cognitive (Pretreatment)',
    'qol_role_pretreatment': 'QoL Role (Pretreatment)',
}

def translate_feature_name(feature_name):
    """Translate Dutch feature name to English."""
    return FEATURE_TRANSLATIONS.get(feature_name, feature_name.replace('_', ' ').title())

# =============================================================================
# Load and Combine Data
# =============================================================================
print("=" * 80)
print("LOADING AND COMBINING DATA")
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

# Combine datasets
print("\nCombining PACAP and NCR datasets...")
df_combined = pd.concat([df_pacap, df_ncr], ignore_index=True)
print(f"  Combined dataset: {len(df_combined)} patients")
print(f"    - PACAP: {len(df_pacap)} patients")
print(f"    - NCR: {len(df_ncr)} patients")
print()

# Remove duplicates if any
df_combined = df_combined.drop_duplicates(subset=['key_nkr'] if 'key_nkr' in df_combined.columns else None)
print(f"  After removing duplicates: {len(df_combined)} patients")
print()

# =============================================================================
# Report Missing Value Percentages
# =============================================================================
print("=" * 80)
print("MISSING VALUE PERCENTAGES")
print("=" * 80)
print()

all_features = numerical_features + categorical_features + qol_features
missing_stats = []

for feature in all_features:
    if feature in df_combined.columns:
        missing_count = df_combined[feature].isna().sum()
        total_count = len(df_combined)
        pct_missing = (missing_count / total_count) * 100 if total_count > 0 else 0
        missing_stats.append({
            'Feature': feature,
            'Missing_Count': missing_count,
            'Total_Count': total_count,
            'Missing_Pct': pct_missing
        })

missing_df = pd.DataFrame(missing_stats)
missing_df = missing_df.sort_values('Missing_Pct', ascending=False)

print("All Features (sorted by missing percentage):")
print("-" * 80)
for _, row in missing_df.iterrows():
    feat_name = translate_feature_name(row['Feature'])
    print(f"  {feat_name:<50} {row['Missing_Pct']:>6.2f}% ({row['Missing_Count']}/{row['Total_Count']})")
print()

# QoL features specifically
print("QoL Features:")
print("-" * 80)
qol_missing = missing_df[missing_df['Feature'].isin(qol_features)]
for _, row in qol_missing.iterrows():
    feat_name = translate_feature_name(row['Feature'])
    print(f"  {feat_name:<50} {row['Missing_Pct']:>6.2f}% ({row['Missing_Count']}/{row['Total_Count']})")
print()

# Overall statistics
overall_missing_pct = missing_df['Missing_Pct'].mean()
qol_overall_missing_pct = qol_missing['Missing_Pct'].mean() if len(qol_missing) > 0 else 0

print(f"Overall missing percentage:")
print(f"  All features: {overall_missing_pct:.2f}% (mean)")
print(f"  QoL features: {qol_overall_missing_pct:.2f}% (mean)")
print()

# Save missing value statistics
missing_df.to_csv('combined_missing_value_statistics.csv', index=False)
print("Saved missing value statistics to: combined_missing_value_statistics.csv")
print()

# =============================================================================
# Prepare Data
# =============================================================================
print("=" * 80)
print("PREPARING DATA")
print("=" * 80)
print()

# Define features with QoL
features_with_qol = numerical_features + categorical_features + qol_features

# Prepare feature data
X = df_combined[features_with_qol].copy()

# Create survival structured array
y_survival = Surv.from_arrays(
    event=df_combined['vit_stat'].astype(bool),
    time=df_combined['vit_stat_int'].astype(float)
)

print(f"Total samples: {len(X)}")
print(f"Total features: {len(features_with_qol)}")
print(f"  - Numerical: {len(numerical_features)}")
print(f"  - Categorical: {len(categorical_features)}")
print(f"  - QoL: {len(qol_features)}")
print()

# Convert categorical/string columns to numeric
print("Encoding categorical features...")
label_encoders = {}
for col in X.columns:
    if X[col].dtype == 'object' or X[col].dtype.name == 'category':
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le
        print(f"  - Encoded '{col}' with {len(le.classes_)} unique values")

# Store feature names
feature_names = list(X.columns)

# Convert to numpy array
X_numeric = X.values.astype(np.float64)

print(f"\nData prepared: {X_numeric.shape[0]} samples, {X_numeric.shape[1]} features")
print()

# =============================================================================
# Alpha Exploration
# =============================================================================
print("=" * 80)
print("ALPHA EXPLORATION")
print("=" * 80)
print()

# Use a train/test split for alpha exploration
from sklearn.model_selection import train_test_split

n_samples = len(X_numeric)
indices = np.arange(n_samples)
train_indices, test_indices = train_test_split(
    indices, test_size=0.3, random_state=42, stratify=None
)

X_train = X_numeric[train_indices]
X_test = X_numeric[test_indices]
y_train = y_survival[train_indices]
y_test = y_survival[test_indices]

print(f"Train set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")
print()

# Test different alpha values
alpha_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
alpha_results = []

print("Testing alpha values...")
print(f"{'Alpha':<10} {'C-index':<15} {'Status':<20}")
print("-" * 50)

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
    
    print(f"{alpha:<10.1f} {c_index:<15.4f} {'Testing...':<20}")

# Find best alpha
best_alpha_result = max(alpha_results, key=lambda x: x['c_index'])
best_alpha = best_alpha_result['alpha']

print()
print(f"Best alpha: {best_alpha} (C-index: {best_alpha_result['c_index']:.4f})")
print()

# Save alpha exploration results
alpha_df = pd.DataFrame(alpha_results)
alpha_df.to_csv('combined_alpha_exploration.csv', index=False)
print("Saved alpha exploration results to: combined_alpha_exploration.csv")
print()

# =============================================================================
# K-Fold Cross-Validation with Best Alpha
# =============================================================================
print("=" * 80)
print(f"K-FOLD CROSS-VALIDATION (alpha={best_alpha})")
print("=" * 80)
print()

n_folds = 5
kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)

cv_results = []
fold_c_indices = []

print(f"Running {n_folds}-fold cross-validation...")
print()

for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X_numeric)):
    X_train_fold = X_numeric[train_idx]
    X_val_fold = X_numeric[val_idx]
    y_train_fold = y_survival[train_idx]
    y_val_fold = y_survival[val_idx]
    
    # Train model
    rsf_fold = RandomSurvivalForest(
        n_estimators=100,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",
        random_state=42 + fold_idx,
        n_jobs=-1,
        alpha=best_alpha
    )
    
    rsf_fold.fit(X_train_fold, y_train_fold)
    
    # Evaluate
    risk_fold = rsf_fold.predict(X_val_fold)
    c_index_fold = concordance_index_censored(
        y_val_fold['event'],
        y_val_fold['time'],
        risk_fold
    )[0]
    
    fold_c_indices.append(c_index_fold)
    
    print(f"  Fold {fold_idx + 1}/{n_folds}: C-index = {c_index_fold:.4f}")
    
    cv_results.append({
        'Fold': fold_idx + 1,
        'Alpha': best_alpha,
        'C_index': c_index_fold
    })

# Calculate statistics
mean_c_index = np.mean(fold_c_indices)
std_c_index = np.std(fold_c_indices, ddof=1)

print()
print(f"Cross-validation results (alpha={best_alpha}):")
print(f"  Mean C-index: {mean_c_index:.4f} ± {std_c_index:.4f}")
print(f"  Range: [{min(fold_c_indices):.4f}, {max(fold_c_indices):.4f}]")
print()

# Save CV results
cv_df = pd.DataFrame(cv_results)
cv_df.to_csv('combined_cv_results.csv', index=False)
print("Saved CV results to: combined_cv_results.csv")
print()

# =============================================================================
# Summary Table
# =============================================================================
print("=" * 80)
print("SUMMARY RESULTS")
print("=" * 80)
print()

def format_3sf(value, std):
    """Format value and std to 3 significant figures."""
    if value == 0:
        return "0.000 ± 0.000"
    value_str = f"{value:.3g}"
    std_str = f"{std:.3g}"
    return f"{value_str} ± {std_str}"

summary_data = {
    'Dataset': 'Combined (PACAP + NCR)',
    'Total_Samples': len(df_combined),
    'PACAP_Samples': len(df_pacap),
    'NCR_Samples': len(df_ncr),
    'Total_Features': len(features_with_qol),
    'Best_Alpha': best_alpha,
    'CV_Mean_C_index': mean_c_index,
    'CV_Std_C_index': std_c_index,
    'CV_Formatted': format_3sf(mean_c_index, std_c_index),
    'Overall_Missing_Pct': overall_missing_pct,
    'QoL_Missing_Pct': qol_overall_missing_pct
}

summary_df = pd.DataFrame([summary_data])
print(summary_df.to_string(index=False))
print()

# Save summary
summary_df.to_csv('combined_analysis_summary.csv', index=False)
print("Saved summary to: combined_analysis_summary.csv")
print()

# =============================================================================
# Detailed Results Table
# =============================================================================
print("=" * 80)
print("DETAILED RESULTS TABLE")
print("=" * 80)
print()

results_table = pd.DataFrame({
    'Strategy': ['MASurvival (Combined Dataset)'],
    'Best_Alpha': [best_alpha],
    'CV_Mean_C_index': [mean_c_index],
    'CV_Std_C_index': [std_c_index],
    'CV_Formatted': [format_3sf(mean_c_index, std_c_index)],
    'N_Folds': [n_folds],
    'Total_Samples': [len(df_combined)],
    'Overall_Missing_Pct': [overall_missing_pct],
    'QoL_Missing_Pct': [qol_overall_missing_pct]
})

print(results_table.to_string(index=False))
print()

results_table.to_csv('combined_detailed_results.csv', index=False)
print("Saved detailed results to: combined_detailed_results.csv")
print()

# =============================================================================
# Alpha Exploration Summary
# =============================================================================
print("=" * 80)
print("ALPHA EXPLORATION SUMMARY")
print("=" * 80)
print()

alpha_summary = pd.DataFrame(alpha_results)
alpha_summary = alpha_summary.sort_values('c_index', ascending=False)

print(alpha_summary.to_string(index=False))
print()

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print()
print("Generated files:")
print("  - combined_missing_value_statistics.csv: Missing value percentages for all features")
print("  - combined_alpha_exploration.csv: Alpha exploration results")
print("  - combined_cv_results.csv: K-fold CV results per fold")
print("  - combined_analysis_summary.csv: Overall summary")
print("  - combined_detailed_results.csv: Detailed results table")
print()


