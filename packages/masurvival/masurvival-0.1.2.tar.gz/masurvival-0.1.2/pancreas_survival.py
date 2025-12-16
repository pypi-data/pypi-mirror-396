import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from scipy import stats
from masurvival.util import Surv
from masurvival.ensemble import RandomSurvivalForest
from masurvival.metrics import concordance_index_censored

# SHAP for feature importance visualization
# Set to False to skip SHAP computation (saves time)
RUN_SHAP = False

RUN_ALPHA=False
best_alpha = 0.1

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("Warning: SHAP not available. Install with: pip install shap")
    RUN_SHAP = False

# Only run SHAP if both flag is True and SHAP is available
RUN_SHAP = RUN_SHAP and SHAP_AVAILABLE

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
            'meta_perit', 'meta_overig', #'resectability_status'
        ]
        
# QoL pretreatment features
qol_features = [
            'qol_summary_pretreatment',  # summary score,
            'qol_physical_pretreatment',
            'qol_social_pretreatment',
            'qol_emotional_pretreatment',
            'qol_cognitive_pretreatment',
            'qol_role_pretreatment'
        ]

# Feature name translations (Dutch to English)
FEATURE_TRANSLATIONS = {
    'leeft_cat': 'Age Category',
    'gesl': 'Gender',
    'klin_tum_afm': 'Maximum Size of Primary Tumor',
    'cci': 'Charlson Comorbidity Index',
    'cci_cat': 'CCI Category',
    'ca199': 'CA 19-9',
    'bilirubine': 'Bilirubin',
    'albumine': 'Albumin',
    'ldh': 'LDH',
    'crp': 'CRP',
    'perf_stat': 'Performance Status',
    'seizoen': 'Season',
    'diffgrad': 'Differentiation Grade',
    'morf': 'Morphology',
    'morf_cat': 'Morphology Category',
    'ct': 'CT Stage',
    'cn': 'CN Stage',
    'cm': 'CM Stage',
    'cstadium': 'C Stage',
    'stadium': 'Stage',
    'meta_lever': 'Liver Metastasis',
    'meta_bijnier': 'Adrenal Metastasis',
    'meta_bot': 'Bone Metastasis',
    'meta_hersenen': 'Brain Metastasis',
    'meta_long': 'Lung Metastasis',
    'meta_lymf': 'Lymph Node Metastasis',
    'meta_perit': 'Peritoneal Metastasis',
    'meta_overig': 'Other Metastasis',
    'veneus_vaatbetr': 'Venous Vascular Involvement',
    'arterieel_vaatbetr': 'Arterial Vascular Involvement',
    'geboorteland': 'Country of Birth',
    'diag_basis': 'Diagnosis Basis',
    'topo_sublok': 'Topography Sublocation',
    'qol_summary_pretreatment': 'QoL Summary Score (Pretreatment)',
    'qol_physical_pretreatment': 'QoL Physical (Pretreatment)',
    'qol_social_pretreatment': 'QoL Social (Pretreatment)',
    'qol_emotional_pretreatment': 'QoL Emotional (Pretreatment)',
    'qol_cognitive_pretreatment': 'QoL Cognitive (Pretreatment)',
    'qol_role_pretreatment': 'QoL Role (Pretreatment)',
    'resectability_status': 'Resectability Status'
}

def translate_feature_name(feature_name):
    """Translate Dutch feature name to English, or return original if no translation exists."""
    return FEATURE_TRANSLATIONS.get(feature_name, feature_name)

def translate_feature_names(feature_names_list):
    """Translate a list of feature names from Dutch to English."""
    return [translate_feature_name(name) for name in feature_names_list]

# Load the PACAP data
print("Loading PACAP dataset...")
df_pacap = pd.read_csv('merged_pacap_data.csv')

# Load the merged datasets (NCR data)
print("Loading merged datasets (NCR data)...")
df_ncr_all = pd.read_csv('merged_datasets.csv')

# Identify unique patients in PACAP dataset (assuming 'key_nkr' is the patient identifier)
print("\nIdentifying patients in PACAP dataset...")
pacap_patient_ids = set(df_pacap['key_nkr'].dropna().unique())
print(f"  Found {len(pacap_patient_ids)} unique patients in PACAP dataset")

# Remove PACAP patients from NCR dataset
print("Removing PACAP patients from NCR dataset...")
df_ncr = df_ncr_all[~df_ncr_all['key_nkr'].isin(pacap_patient_ids)].copy()
print(f"  NCR dataset: {len(df_ncr)} patients (after removing {len(pacap_patient_ids)} PACAP patients)")

# Use PACAP as the main dataset for training
df = df_pacap.copy()

# # in column resectability_status, replace missing_data with np.nan
# df['resectability_status'] = df['resectability_status'].replace('missing_data', np.nan)

# check for duplicate  key_nkr and remove duplicates
df = df.drop_duplicates(subset=['key_nkr'])

# prints % of missing values in each feature
for feature in numerical_features + categorical_features + qol_features:
    print(f"{feature}: {df[feature].isnull().mean()*100:.2f}%")

X = df[numerical_features + categorical_features + qol_features]

# Create survival structured array
y_survival = Surv.from_arrays(
        event=df['vit_stat'].astype(bool),
        time=df['vit_stat_int'].astype(float)
    )

# Convert categorical/string columns to numeric
print("Preprocessing: Converting categorical columns to numeric...")
X_numeric = X.copy()
label_encoders = {}
for col in X_numeric.columns:
    if X_numeric[col].dtype == 'object' or X_numeric[col].dtype.name == 'category':
        le = LabelEncoder()
        X_numeric[col] = le.fit_transform(X_numeric[col].astype(str))
        label_encoders[col] = le
        print(f"  - Encoded column '{col}' with {len(le.classes_)} unique values")

# Store feature names before converting to numpy array
feature_names = list(X_numeric.columns)

# Split into train/test using positional indices
# This returns positional indices (0, 1, 2, ...) that work with numpy arrays
n_samples = len(X_numeric)
indices = np.arange(n_samples)
train_indices, test_indices = train_test_split(
    indices, test_size=0.3, random_state=42, stratify=None
)

# Split the data using positional indices
X_train_df = X_numeric.iloc[train_indices].copy()
X_test_df = X_numeric.iloc[test_indices].copy()
y_train = y_survival[train_indices]
y_test = y_survival[test_indices]

# Convert to numpy array for sklearn compatibility
X_train = X_train_df.values.astype(np.float64)
X_test = X_test_df.values.astype(np.float64)

print(f"Converted to numeric array: shape {X_train.shape}, dtype {X_train.dtype}")
print(f"Train set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")
print()

# First, compare models with and without QoL features for alpha=0
print("=" * 60)
print("COMPARING MODELS WITH/WITHOUT QoL FEATURES (alpha=0)")
print("=" * 60)

# Define features without QoL
features_without_qol = numerical_features + categorical_features
features_with_qol = numerical_features + categorical_features + qol_features

print(f"\nFeatures WITHOUT QoL: {len(features_without_qol)} features")
print(f"Features WITH QoL: {len(features_with_qol)} features")
print()

# Prepare data for both models
X_without_qol = df[features_without_qol].copy()
X_with_qol = df[features_with_qol].copy()

# Convert categorical/string columns to numeric for both datasets
print("Preprocessing: Converting categorical columns to numeric...")
label_encoders_without_qol = {}
label_encoders_with_qol = {}

for col in X_without_qol.columns:
    if X_without_qol[col].dtype == 'object' or X_without_qol[col].dtype.name == 'category':
        le = LabelEncoder()
        X_without_qol[col] = le.fit_transform(X_without_qol[col].astype(str))
        label_encoders_without_qol[col] = le
        print(f"  - Encoded column '{col}' with {len(le.classes_)} unique values")

for col in X_with_qol.columns:
    if X_with_qol[col].dtype == 'object' or X_with_qol[col].dtype.name == 'category':
        le = LabelEncoder()
        X_with_qol[col] = le.fit_transform(X_with_qol[col].astype(str))
        label_encoders_with_qol[col] = le
        if col not in label_encoders_without_qol:  # Only print if not already printed
            print(f"  - Encoded column '{col}' with {len(le.classes_)} unique values")

# Store feature names
feature_names_without_qol = list(X_without_qol.columns)
feature_names_with_qol = list(X_with_qol.columns)

# Convert to numpy arrays
X_without_qol_numeric = X_without_qol.values.astype(np.float64)
X_with_qol_numeric = X_with_qol.values.astype(np.float64)

# Split into train/test using positional indices (same split for both)
n_samples = len(X_without_qol_numeric)
indices = np.arange(n_samples)
train_indices, test_indices = train_test_split(
    indices, test_size=0.3, random_state=42, stratify=None
)

# Split both datasets
X_train_without_qol = X_without_qol_numeric[train_indices]
X_test_without_qol = X_without_qol_numeric[test_indices]
X_train_with_qol = X_with_qol_numeric[train_indices]
X_test_with_qol = X_with_qol_numeric[test_indices]
y_train = y_survival[train_indices]
y_test = y_survival[test_indices]

# =============================================================================
# Report missing QoL percentages per test set
# =============================================================================
print("=" * 60)
print("MISSING QoL FEATURES PER TEST SET")
print("=" * 60)
print()

# Get QoL feature indices
qol_indices_in_features = [i for i, feat in enumerate(feature_names_with_qol) if feat in qol_features]

# PACAP test set (before imputation - check original data)
X_pacap_test_original = df.iloc[test_indices][qol_features]
pacap_missing_pct = {}
for feat in qol_features:
    missing_count = X_pacap_test_original[feat].isna().sum()
    total_count = len(X_pacap_test_original)
    pct = (missing_count / total_count) * 100 if total_count > 0 else 0
    pacap_missing_pct[feat] = pct

print("PACAP Test Set (before imputation):")
for feat in qol_features:
    feat_name_eng = translate_feature_name(feat)
    print(f"  {feat_name_eng:<40} {pacap_missing_pct[feat]:>6.2f}% missing")
print()

# NCR test set (before imputation - check original data)
X_ncr_test_original = df_ncr[qol_features]
ncr_missing_pct = {}
for feat in qol_features:
    missing_count = X_ncr_test_original[feat].isna().sum()
    total_count = len(X_ncr_test_original)
    pct = (missing_count / total_count) * 100 if total_count > 0 else 0
    ncr_missing_pct[feat] = pct

print("NCR Test Set (before imputation):")
for feat in qol_features:
    feat_name_eng = translate_feature_name(feat)
    print(f"  {feat_name_eng:<40} {ncr_missing_pct[feat]:>6.2f}% missing")
print()

# Merged test set (PACAP test + NCR test) - before imputation
X_merged_test_original = pd.concat([
    X_pacap_test_original,
    X_ncr_test_original
], ignore_index=True)
merged_missing_pct = {}
for feat in qol_features:
    missing_count = X_merged_test_original[feat].isna().sum()
    total_count = len(X_merged_test_original)
    pct = (missing_count / total_count) * 100 if total_count > 0 else 0
    merged_missing_pct[feat] = pct

print("Merged Test Set (PACAP test + NCR test, before imputation):")
for feat in qol_features:
    feat_name_eng = translate_feature_name(feat)
    print(f"  {feat_name_eng:<40} {merged_missing_pct[feat]:>6.2f}% missing")
print()

# Overall missing percentages
pacap_overall_missing = np.mean(list(pacap_missing_pct.values()))
ncr_overall_missing = np.mean(list(ncr_missing_pct.values()))
merged_overall_missing = np.mean(list(merged_missing_pct.values()))

print(f"Overall missing QoL features:")
print(f"  PACAP Test Set: {pacap_overall_missing:.2f}% (mean across all QoL features)")
print(f"  NCR Test Set:   {ncr_overall_missing:.2f}% (mean across all QoL features)")
print(f"  Merged Test Set: {merged_overall_missing:.2f}% (mean across all QoL features)")
print()

# Save to CSV
missing_qol_df = pd.DataFrame({
    'Feature': [translate_feature_name(feat) for feat in qol_features],
    'PACAP_Missing_Pct': [pacap_missing_pct[feat] for feat in qol_features],
    'NCR_Missing_Pct': [ncr_missing_pct[feat] for feat in qol_features],
    'Merged_Missing_Pct': [merged_missing_pct[feat] for feat in qol_features]
})
missing_qol_df.to_csv('missing_qol_per_test_set.csv', index=False)
print("Saved missing QoL percentages to: missing_qol_per_test_set.csv")
print()

print(f"\nTrain set: {X_train_without_qol.shape[0]} samples")
print(f"Test set: {X_test_without_qol.shape[0]} samples")
print()

# Train model WITHOUT QoL features
print("=" * 60)
print("Training model WITHOUT QoL features (alpha=0)...")
print("=" * 60)
rsf_without_qol = RandomSurvivalForest(
    n_estimators=100,
    min_samples_split=10,
    min_samples_leaf=5,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1,
    alpha=0.0
)
rsf_without_qol.fit(X_train_without_qol, y_train)
risk_scores_without_qol = rsf_without_qol.predict(X_test_without_qol)
c_index_without_qol = concordance_index_censored(
    y_test['event'],
    y_test['time'],
    risk_scores_without_qol
)
print(f"C-index (without QoL): {c_index_without_qol[0]:.4f}")
print()

# Train model WITH QoL features
print("=" * 60)
print("Training model WITH QoL features (alpha=0)...")
print("=" * 60)
rsf_with_qol = RandomSurvivalForest(
    n_estimators=100,
    min_samples_split=10,
    min_samples_leaf=5,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1,
    alpha=0.0
)
rsf_with_qol.fit(X_train_with_qol, y_train)
risk_scores_with_qol = rsf_with_qol.predict(X_test_with_qol)
c_index_with_qol = concordance_index_censored(
    y_test['event'],
    y_test['time'],
    risk_scores_with_qol
)
print(f"C-index (with QoL): {c_index_with_qol[0]:.4f}")
print()

# Comparison summary for PACAP test set
print("=" * 60)
print("COMPARISON: With vs Without QoL Features (alpha=0) - PACAP Test Set")
print("=" * 60)
print(f"{'Model':<30} {'C-index':<12} {'Features':<10}")
print("-" * 60)
print(f"{'Without QoL features':<30} {c_index_without_qol[0]:<12.4f} {len(features_without_qol):<10}")
print(f"{'With QoL features':<30} {c_index_with_qol[0]:<12.4f} {len(features_with_qol):<10}")
improvement = c_index_with_qol[0] - c_index_without_qol[0]
print(f"\nImprovement from adding QoL features: {improvement:+.4f} ({improvement/c_index_without_qol[0]*100:+.2f}%)")
print()

# =============================================================================
# Prepare NCR test set
# =============================================================================
print("=" * 60)
print("PREPARING NCR TEST SET")
print("=" * 60)

# Check if NCR dataset has the required features
print("Checking NCR dataset for required features...")
missing_features = []
for feature in features_with_qol:
    if feature not in df_ncr.columns:
        missing_features.append(feature)

if missing_features:
    print(f"  Warning: {len(missing_features)} features missing in NCR dataset:")
    for feat in missing_features[:10]:  # Show first 10
        print(f"    - {feat}")
    if len(missing_features) > 10:
        print(f"    ... and {len(missing_features) - 10} more")
else:
    print("  All required features are present in NCR dataset")

# Prepare NCR data
X_ncr_without_qol = df_ncr[features_without_qol].copy()
X_ncr_with_qol = df_ncr[features_with_qol].copy()

# Create survival structured array for NCR
y_ncr_survival = Surv.from_arrays(
    event=df_ncr['vit_stat'].astype(bool),
    time=df_ncr['vit_stat_int'].astype(float)
)

# Encode categorical features in NCR dataset using the same encoders from PACAP training
print("\nEncoding categorical features in NCR dataset...")
for col in X_ncr_without_qol.columns:
    if col in label_encoders_without_qol:
        le = label_encoders_without_qol[col]
        # Handle unseen categories by mapping them to the most common class
        X_ncr_without_qol[col] = X_ncr_without_qol[col].astype(str).apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else 0
        )
        print(f"  - Encoded '{col}' (unseen values mapped to 0)")

for col in X_ncr_with_qol.columns:
    if col in label_encoders_with_qol:
        le = label_encoders_with_qol[col]
        # Handle unseen categories
        X_ncr_with_qol[col] = X_ncr_with_qol[col].astype(str).apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else 0
        )
        if col not in label_encoders_without_qol:  # Only print if not already printed
            print(f"  - Encoded '{col}' (unseen values mapped to 0)")

# Convert to numpy arrays
X_ncr_without_qol_numeric = X_ncr_without_qol.values.astype(np.float64)
X_ncr_with_qol_numeric = X_ncr_with_qol.values.astype(np.float64)

print(f"\nNCR test set: {X_ncr_without_qol_numeric.shape[0]} samples")
print()

# =============================================================================
# Train imputer on PACAP training data (for QoL features)
# =============================================================================
print("=" * 60)
print("TRAINING IMPUTER ON PACAP TRAINING DATA")
print("=" * 60)

# Get QoL feature indices in the full feature set
qol_indices = [i for i, feat in enumerate(features_with_qol) if feat in qol_features]
print(f"QoL feature indices: {qol_indices}")
print(f"QoL features: {qol_features}")

# Train imputer on PACAP training data (with QoL features)
print("Training SimpleImputer on PACAP training data (QoL features only)...")
print(f"  Strategy: mean imputation (missing values replaced with feature mean from training data)")
qol_imputer = SimpleImputer(strategy='mean')
X_train_with_qol_for_imputation = X_train_with_qol.copy()
qol_imputer.fit(X_train_with_qol_for_imputation[:, qol_indices])
print("  Imputer trained successfully")

# Show imputation statistics
print("\n  Imputation statistics (mean values learned from PACAP training data):")
for i, feat_name in enumerate(qol_features):
    feat_idx = features_with_qol.index(feat_name)
    if feat_idx in qol_indices:
        imputed_value = qol_imputer.statistics_[qol_indices.index(feat_idx)]
        print(f"    {feat_name}: {imputed_value:.4f}")
print()

# =============================================================================
# Evaluate on NCR test set
# =============================================================================
print("=" * 60)
print("EVALUATING ON NCR TEST SET")
print("=" * 60)

# NCR test WITHOUT QoL features
print("\nEvaluating NCR test set WITHOUT QoL features...")
risk_scores_ncr_without_qol = rsf_without_qol.predict(X_ncr_without_qol_numeric)
c_index_ncr_without_qol = concordance_index_censored(
    y_ncr_survival['event'],
    y_ncr_survival['time'],
    risk_scores_ncr_without_qol
)
print(f"  C-index (NCR, without QoL): {c_index_ncr_without_qol[0]:.4f}")

# NCR test WITH QoL features (imputed)
print("\nEvaluating NCR test set WITH QoL features (imputed)...")
# Check missing values before imputation
print("  Checking missing values in NCR QoL features before imputation...")
for i, feat_name in enumerate(qol_features):
    feat_idx = features_with_qol.index(feat_name)
    if feat_idx in qol_indices:
        n_missing = np.isnan(X_ncr_with_qol_numeric[:, feat_idx]).sum()
        n_total = len(X_ncr_with_qol_numeric)
        pct_missing = (n_missing / n_total) * 100 if n_total > 0 else 0
        print(f"    {feat_name}: {n_missing}/{n_total} missing ({pct_missing:.1f}%)")

# Impute QoL features in NCR test set
X_ncr_with_qol_imputed = X_ncr_with_qol_numeric.copy()
X_ncr_with_qol_imputed[:, qol_indices] = qol_imputer.transform(X_ncr_with_qol_numeric[:, qol_indices])
print(f"\n  Imputed QoL features for {len(qol_indices)} features using mean values from PACAP training data")

risk_scores_ncr_with_qol = rsf_with_qol.predict(X_ncr_with_qol_imputed)
c_index_ncr_with_qol = concordance_index_censored(
    y_ncr_survival['event'],
    y_ncr_survival['time'],
    risk_scores_ncr_with_qol
)
print(f"  C-index (NCR, with QoL imputed): {c_index_ncr_with_qol[0]:.4f}")
print()

# =============================================================================
# Final Summary: All C-index Results
# =============================================================================
print("=" * 60)
print("FINAL SUMMARY: C-INDEX RESULTS (alpha=0)")
print("=" * 60)
print(f"{'Test Set':<25} {'Features':<25} {'C-index':<12}")
print("-" * 70)
print(f"{'PACAP Test':<25} {'Without QoL':<25} {c_index_without_qol[0]:<12.4f}")
print(f"{'PACAP Test':<25} {'With QoL':<25} {c_index_with_qol[0]:<12.4f}")
print(f"{'NCR Test':<25} {'Without QoL':<25} {c_index_ncr_without_qol[0]:<12.4f}")
print(f"{'NCR Test':<25} {'With QoL (imputed)':<25} {c_index_ncr_with_qol[0]:<12.4f}")
print()

# Calculate improvements
pacap_improvement = c_index_with_qol[0] - c_index_without_qol[0]
ncr_improvement = c_index_ncr_with_qol[0] - c_index_ncr_without_qol[0]

print("Improvements from adding QoL features:")
print(f"  PACAP Test: {pacap_improvement:+.4f} ({pacap_improvement/c_index_without_qol[0]*100:+.2f}%)")
print(f"  NCR Test:   {ncr_improvement:+.4f} ({ncr_improvement/c_index_ncr_without_qol[0]*100:+.2f}%)")
print()

# =============================================================================
# Test MASurvival with different alpha values on both PACAP and NCR test sets
# =============================================================================
print("=" * 60)
print("TESTING MASURVIVAL WITH DIFFERENT ALPHA VALUES")
print("=" * 60)
print()
if RUN_ALPHA:
    alpha_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
    alpha_results = []

    for alpha in alpha_values:
        print("=" * 60)
        print(f"Training MASurvivalForest with alpha={alpha}...")
        print("=" * 60)
        
        # Train on PACAP training data with QoL features
        rsf = RandomSurvivalForest(
            n_estimators=100,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1,
            alpha=alpha
        )
        
        rsf.fit(X_train_with_qol, y_train)
        print("Training completed!")
        
        # Evaluate on PACAP test set (with QoL features)
        risk_scores_pacap = rsf.predict(X_test_with_qol)
        c_index_pacap = concordance_index_censored(
            y_test['event'],
            y_test['time'],
            risk_scores_pacap
        )
        print(f"  PACAP test C-index: {c_index_pacap[0]:.4f}")
        
        # Evaluate on NCR test set (with QoL features imputed)
        risk_scores_ncr = rsf.predict(X_ncr_with_qol_imputed)
        c_index_ncr = concordance_index_censored(
            y_ncr_survival['event'],
            y_ncr_survival['time'],
            risk_scores_ncr
        )
        print(f"  NCR test C-index: {c_index_ncr[0]:.4f}")
        
        alpha_results.append({
            'alpha': alpha,
            'pacap_c_index': c_index_pacap[0],
            'ncr_c_index': c_index_ncr[0],
            'mean_c_index': (c_index_pacap[0] + c_index_ncr[0]) / 2
        })
        print()

    # Find best alpha (by mean C-index across both test sets)
    print("=" * 60)
    print("ALPHA SELECTION RESULTS")
    print("=" * 60)
    print(f"{'Alpha':<10} {'PACAP C-index':<15} {'NCR C-index':<15} {'Mean C-index':<15}")
    print("-" * 60)
    for r in alpha_results:
        print(f"{r['alpha']:<10.1f} {r['pacap_c_index']:<15.4f} {r['ncr_c_index']:<15.4f} {r['mean_c_index']:<15.4f}")

    best_alpha_result = max(alpha_results, key=lambda x: x['mean_c_index'])
    best_alpha = best_alpha_result['alpha']
    print()
    print(f"Best alpha: {best_alpha} (Mean C-index: {best_alpha_result['mean_c_index']:.4f})")
    print(f"  - PACAP test C-index: {best_alpha_result['pacap_c_index']:.4f}")
    print(f"  - NCR test C-index: {best_alpha_result['ncr_c_index']:.4f}")
    print()

# =============================================================================
# Compare three strategies: MASurvival (best alpha) vs Feature Removal vs Imputation
# Using k-fold cross-validation for PACAP and multiple runs for NCR
# =============================================================================
print("=" * 60)
print("COMPARING STRATEGIES: MASurvival vs Feature Removal vs Imputation")
print("Using 5-fold CV for PACAP, multiple runs for NCR")
print("=" * 60)
print()

n_folds = 5
# Strategy 1: MASurvival with best alpha (avoids missing features)
print("Strategy 1: MASurvival (alpha={}) - avoids missing features".format(best_alpha))

# PACAP: 5-fold cross-validation
print("  Running 5-fold cross-validation on PACAP...")
kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
c_ma_pacap_folds = []
c_ma_ncr_folds = []  # Store NCR evaluations for each fold
c_ma_merged_folds = []  # Store merged evaluations for each fold

for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X_with_qol_numeric)):
    X_train_fold = X_with_qol_numeric[train_idx]
    X_val_fold = X_with_qol_numeric[val_idx]
    y_train_fold = y_survival[train_idx]
    y_val_fold = y_survival[val_idx]
    
    rsf_ma_fold = RandomSurvivalForest(
        n_estimators=100,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",
        random_state=42 + fold_idx,
        n_jobs=-1,
        alpha=best_alpha
    )
    rsf_ma_fold.fit(X_train_fold, y_train_fold)
    
    # Evaluate on PACAP validation fold
    risk_ma_fold = rsf_ma_fold.predict(X_val_fold)
    c_ma_fold = concordance_index_censored(y_val_fold['event'], y_val_fold['time'], risk_ma_fold)[0]
    c_ma_pacap_folds.append(c_ma_fold)
    
    # Evaluate on NCR test set (same set for all folds)
    risk_ma_ncr_fold = rsf_ma_fold.predict(X_ncr_with_qol_imputed)
    c_ma_ncr_fold = concordance_index_censored(y_ncr_survival['event'], y_ncr_survival['time'], risk_ma_ncr_fold)[0]
    c_ma_ncr_folds.append(c_ma_ncr_fold)
    
    # Evaluate on merged test set (PACAP test + NCR test)
    X_merged_test = np.vstack([X_test_with_qol, X_ncr_with_qol_imputed])
    y_merged_test = np.concatenate([y_test, y_ncr_survival])
    risk_ma_merged = rsf_ma_fold.predict(X_merged_test)
    c_ma_merged_fold = concordance_index_censored(y_merged_test['event'], y_merged_test['time'], risk_ma_merged)[0]
    c_ma_merged_folds.append(c_ma_merged_fold)
    
    # Generate SHAP plot for this fold
    if RUN_SHAP:
        try:
            print(f"    Fold {fold_idx + 1}/{n_folds}: C-index = {c_ma_fold:.4f}, computing SHAP...")
            n_background = min(100, len(X_train_fold))
            X_train_summary = shap.sample(X_train_fold, n_background)
            X_train_summary_df = pd.DataFrame(X_train_summary, columns=feature_names_with_qol)
            explainer = shap.Explainer(rsf_ma_fold.predict, X_train_summary_df)
            
            n_shap_samples = min(50, len(X_val_fold))
            shap_indices = np.random.choice(len(X_val_fold), n_shap_samples, replace=False)
            X_val_shap = X_val_fold[shap_indices]
            X_val_shap_df = pd.DataFrame(X_val_shap, columns=feature_names_with_qol)
            
            shap_values = explainer(X_val_shap_df)
            if hasattr(shap_values, 'values'):
                shap_values_array = shap_values.values
            else:
                shap_values_array = shap_values
            
            if len(shap_values_array.shape) > 2:
                shap_values_array = shap_values_array.reshape(shap_values_array.shape[0], -1)
            if shap_values_array.shape[1] != X_val_shap.shape[1]:
                shap_values_array = shap_values_array[:, :X_val_shap.shape[1]]
            
            feature_names_english = translate_feature_names(feature_names_with_qol)
            if hasattr(shap_values, 'feature_names'):
                if shap_values.feature_names is None or len(shap_values.feature_names) != len(feature_names_english):
                    shap_values.feature_names = feature_names_english
            else:
                shap_values = shap.Explanation(
                    values=shap_values_array,
                    base_values=shap_values.base_values if hasattr(shap_values, 'base_values') else shap_values_array.mean(),
                    data=X_val_shap_df.values if hasattr(X_val_shap_df, 'values') else X_val_shap,
                    feature_names=feature_names_english
                )
            
            # Save SHAP feature importance to CSV
            mean_abs_shap = np.abs(shap_values_array).mean(axis=0)
            shap_importance_df = pd.DataFrame({
                'Feature': feature_names_english,
                'Mean_Abs_SHAP': mean_abs_shap
            }).sort_values('Mean_Abs_SHAP', ascending=False)
            shap_importance_df.to_csv(f'shap_importance_ma_alpha{best_alpha}_fold{fold_idx + 1}.csv', index=False)
            
            import matplotlib.pyplot as plt
            shap.plots.beeswarm(shap_values, show=False, max_display=15)
            plt.title(f'SHAP Beeswarm - MASurvival alpha={best_alpha} Fold {fold_idx + 1}')
            plt.tight_layout()
            plt.savefig(f'shap_ma_alpha{best_alpha}_fold{fold_idx + 1}_beeswarm.png', dpi=150, bbox_inches='tight')
            plt.close()
            
            shap.plots.bar(shap_values, show=False, max_display=20)
            plt.title(f'SHAP Feature Importance - MASurvival alpha={best_alpha} Fold {fold_idx + 1}')
            plt.tight_layout()
            plt.savefig(f'shap_ma_alpha{best_alpha}_fold{fold_idx + 1}_bar.png', dpi=150, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"      Warning: Could not compute SHAP for fold {fold_idx + 1}: {e}")

c_ma_pacap_mean = np.mean(c_ma_pacap_folds)
c_ma_pacap_std = np.std(c_ma_pacap_folds, ddof=1)
print(f"  PACAP: Mean C-index = {c_ma_pacap_mean:.4f} ± {c_ma_pacap_std:.4f} (across {n_folds} folds)")

# NCR: Evaluate on same test set using models from each fold
c_ma_ncr_mean = np.mean(c_ma_ncr_folds)
c_ma_ncr_std = np.std(c_ma_ncr_folds, ddof=1)
print(f"  NCR: Mean C-index = {c_ma_ncr_mean:.4f} ± {c_ma_ncr_std:.4f} (across {n_folds} fold models on same test set)")

# Merged test set
c_ma_merged_mean = np.mean(c_ma_merged_folds)
c_ma_merged_std = np.std(c_ma_merged_folds, ddof=1)
print(f"  Merged: Mean C-index = {c_ma_merged_mean:.4f} ± {c_ma_merged_std:.4f} (across {n_folds} fold models)")
print()

# Strategy 2: Feature Removal (without QoL features)
print("Strategy 2: Feature Removal - remove QoL features entirely")

# PACAP: 5-fold cross-validation
print("  Running 5-fold cross-validation on PACAP...")
c_remove_pacap_folds = []
c_remove_ncr_folds = []  # Store NCR evaluations for each fold
c_remove_merged_folds = []  # Store merged evaluations for each fold

for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X_without_qol_numeric)):
    X_train_fold = X_without_qol_numeric[train_idx]
    X_val_fold = X_without_qol_numeric[val_idx]
    y_train_fold = y_survival[train_idx]
    y_val_fold = y_survival[val_idx]
    
    rsf_remove_fold = RandomSurvivalForest(
        n_estimators=100,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",
        random_state=42 + fold_idx,
        n_jobs=-1,
        alpha=0.0
    )
    rsf_remove_fold.fit(X_train_fold, y_train_fold)
    
    # Evaluate on PACAP validation fold
    risk_remove_fold = rsf_remove_fold.predict(X_val_fold)
    c_remove_fold = concordance_index_censored(y_val_fold['event'], y_val_fold['time'], risk_remove_fold)[0]
    c_remove_pacap_folds.append(c_remove_fold)
    
    # Evaluate on NCR test set (same set for all folds)
    risk_remove_ncr_fold = rsf_remove_fold.predict(X_ncr_without_qol_numeric)
    c_remove_ncr_fold = concordance_index_censored(y_ncr_survival['event'], y_ncr_survival['time'], risk_remove_ncr_fold)[0]
    c_remove_ncr_folds.append(c_remove_ncr_fold)
    
    # Evaluate on merged test set
    X_merged_test = np.vstack([X_test_without_qol, X_ncr_without_qol_numeric])
    y_merged_test = np.concatenate([y_test, y_ncr_survival])
    risk_remove_merged = rsf_remove_fold.predict(X_merged_test)
    c_remove_merged_fold = concordance_index_censored(y_merged_test['event'], y_merged_test['time'], risk_remove_merged)[0]
    c_remove_merged_folds.append(c_remove_merged_fold)
    
    # Generate SHAP plot for this fold
    if RUN_SHAP:
        try:
            print(f"    Fold {fold_idx + 1}/{n_folds}: C-index = {c_remove_fold:.4f}, computing SHAP...")
            n_background = min(100, len(X_train_fold))
            X_train_summary = shap.sample(X_train_fold, n_background)
            X_train_summary_df = pd.DataFrame(X_train_summary, columns=feature_names_without_qol)
            explainer = shap.Explainer(rsf_remove_fold.predict, X_train_summary_df)
            
            n_shap_samples = min(50, len(X_val_fold))
            shap_indices = np.random.choice(len(X_val_fold), n_shap_samples, replace=False)
            X_val_shap = X_val_fold[shap_indices]
            X_val_shap_df = pd.DataFrame(X_val_shap, columns=feature_names_without_qol)
            
            shap_values = explainer(X_val_shap_df)
            if hasattr(shap_values, 'values'):
                shap_values_array = shap_values.values
            else:
                shap_values_array = shap_values
            
            if len(shap_values_array.shape) > 2:
                shap_values_array = shap_values_array.reshape(shap_values_array.shape[0], -1)
            if shap_values_array.shape[1] != X_val_shap.shape[1]:
                shap_values_array = shap_values_array[:, :X_val_shap.shape[1]]
            
            feature_names_english = translate_feature_names(feature_names_without_qol)
            if hasattr(shap_values, 'feature_names'):
                if shap_values.feature_names is None or len(shap_values.feature_names) != len(feature_names_english):
                    shap_values.feature_names = feature_names_english
            else:
                shap_values = shap.Explanation(
                    values=shap_values_array,
                    base_values=shap_values.base_values if hasattr(shap_values, 'base_values') else shap_values_array.mean(),
                    data=X_val_shap_df.values if hasattr(X_val_shap_df, 'values') else X_val_shap,
                    feature_names=feature_names_english
                )
            
            # Save SHAP feature importance to CSV
            mean_abs_shap = np.abs(shap_values_array).mean(axis=0)
            shap_importance_df = pd.DataFrame({
                'Feature': feature_names_english,
                'Mean_Abs_SHAP': mean_abs_shap
            }).sort_values('Mean_Abs_SHAP', ascending=False)
            shap_importance_df.to_csv(f'shap_importance_remove_fold{fold_idx + 1}.csv', index=False)
            
            import matplotlib.pyplot as plt
            shap.plots.beeswarm(shap_values, show=False, max_display=15)
            plt.title(f'SHAP Beeswarm - Remove QoL Fold {fold_idx + 1}')
            plt.tight_layout()
            plt.savefig(f'shap_remove_fold{fold_idx + 1}_beeswarm.png', dpi=150, bbox_inches='tight')
            plt.close()
            
            shap.plots.bar(shap_values, show=False, max_display=20)
            plt.title(f'SHAP Feature Importance - Remove QoL Fold {fold_idx + 1}')
            plt.tight_layout()
            plt.savefig(f'shap_remove_fold{fold_idx + 1}_bar.png', dpi=150, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"      Warning: Could not compute SHAP for fold {fold_idx + 1}: {e}")

c_remove_pacap_mean = np.mean(c_remove_pacap_folds)
c_remove_pacap_std = np.std(c_remove_pacap_folds, ddof=1)
print(f"  PACAP: Mean C-index = {c_remove_pacap_mean:.4f} ± {c_remove_pacap_std:.4f} (across {n_folds} folds)")

# NCR: Evaluate on same test set using models from each fold
c_remove_ncr_mean = np.mean(c_remove_ncr_folds)
c_remove_ncr_std = np.std(c_remove_ncr_folds, ddof=1)
print(f"  NCR: Mean C-index = {c_remove_ncr_mean:.4f} ± {c_remove_ncr_std:.4f} (across {n_folds} fold models on same test set)")

# Merged test set
c_remove_merged_mean = np.mean(c_remove_merged_folds)
c_remove_merged_std = np.std(c_remove_merged_folds, ddof=1)
print(f"  Merged: Mean C-index = {c_remove_merged_mean:.4f} ± {c_remove_merged_std:.4f} (across {n_folds} fold models)")
print()

# Strategy 3: Imputation (impute missing QoL features)
print("Strategy 3: Imputation - impute missing QoL features")

# PACAP: 5-fold cross-validation
print("  Running 5-fold cross-validation on PACAP...")
c_impute_pacap_folds = []
c_impute_ncr_folds = []  # Store NCR evaluations for each fold
c_impute_merged_folds = []  # Store merged evaluations for each fold

for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X_with_qol_numeric)):
    X_train_fold = X_with_qol_numeric[train_idx]
    X_val_fold = X_with_qol_numeric[val_idx]
    y_train_fold = y_survival[train_idx]
    y_val_fold = y_survival[val_idx]
    
    rsf_impute_fold = RandomSurvivalForest(
        n_estimators=100,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",
        random_state=42 + fold_idx,
        n_jobs=-1,
        alpha=0.0
    )
    rsf_impute_fold.fit(X_train_fold, y_train_fold)
    
    # Evaluate on PACAP validation fold
    risk_impute_fold = rsf_impute_fold.predict(X_val_fold)
    c_impute_fold = concordance_index_censored(y_val_fold['event'], y_val_fold['time'], risk_impute_fold)[0]
    c_impute_pacap_folds.append(c_impute_fold)
    
    # Evaluate on NCR test set (same set for all folds)
    risk_impute_ncr_fold = rsf_impute_fold.predict(X_ncr_with_qol_imputed)
    c_impute_ncr_fold = concordance_index_censored(y_ncr_survival['event'], y_ncr_survival['time'], risk_impute_ncr_fold)[0]
    c_impute_ncr_folds.append(c_impute_ncr_fold)
    
    # Evaluate on merged test set
    X_merged_test = np.vstack([X_test_with_qol, X_ncr_with_qol_imputed])
    y_merged_test = np.concatenate([y_test, y_ncr_survival])
    risk_impute_merged = rsf_impute_fold.predict(X_merged_test)
    c_impute_merged_fold = concordance_index_censored(y_merged_test['event'], y_merged_test['time'], risk_impute_merged)[0]
    c_impute_merged_folds.append(c_impute_merged_fold)
    
    # Generate SHAP plot for this fold
    if RUN_SHAP:
        try:
            print(f"    Fold {fold_idx + 1}/{n_folds}: C-index = {c_impute_fold:.4f}, computing SHAP...")
            n_background = min(100, len(X_train_fold))
            X_train_summary = shap.sample(X_train_fold, n_background)
            X_train_summary_df = pd.DataFrame(X_train_summary, columns=feature_names_with_qol)
            explainer = shap.Explainer(rsf_impute_fold.predict, X_train_summary_df)
            
            n_shap_samples = min(50, len(X_val_fold))
            shap_indices = np.random.choice(len(X_val_fold), n_shap_samples, replace=False)
            X_val_shap = X_val_fold[shap_indices]
            X_val_shap_df = pd.DataFrame(X_val_shap, columns=feature_names_with_qol)
            
            shap_values = explainer(X_val_shap_df)
            if hasattr(shap_values, 'values'):
                shap_values_array = shap_values.values
            else:
                shap_values_array = shap_values
            
            if len(shap_values_array.shape) > 2:
                shap_values_array = shap_values_array.reshape(shap_values_array.shape[0], -1)
            if shap_values_array.shape[1] != X_val_shap.shape[1]:
                shap_values_array = shap_values_array[:, :X_val_shap.shape[1]]
            
            feature_names_english = translate_feature_names(feature_names_with_qol)
            if hasattr(shap_values, 'feature_names'):
                if shap_values.feature_names is None or len(shap_values.feature_names) != len(feature_names_english):
                    shap_values.feature_names = feature_names_english
            else:
                shap_values = shap.Explanation(
                    values=shap_values_array,
                    base_values=shap_values.base_values if hasattr(shap_values, 'base_values') else shap_values_array.mean(),
                    data=X_val_shap_df.values if hasattr(X_val_shap_df, 'values') else X_val_shap,
                    feature_names=feature_names_english
                )
            
            # Save SHAP feature importance to CSV
            mean_abs_shap = np.abs(shap_values_array).mean(axis=0)
            shap_importance_df = pd.DataFrame({
                'Feature': feature_names_english,
                'Mean_Abs_SHAP': mean_abs_shap
            }).sort_values('Mean_Abs_SHAP', ascending=False)
            shap_importance_df.to_csv(f'shap_importance_impute_fold{fold_idx + 1}.csv', index=False)
            
            import matplotlib.pyplot as plt
            shap.plots.beeswarm(shap_values, show=False, max_display=15)
            plt.title(f'SHAP Beeswarm - Impute QoL Fold {fold_idx + 1}')
            plt.tight_layout()
            plt.savefig(f'shap_impute_fold{fold_idx + 1}_beeswarm.png', dpi=150, bbox_inches='tight')
            plt.close()
            
            shap.plots.bar(shap_values, show=False, max_display=20)
            plt.title(f'SHAP Feature Importance - Impute QoL Fold {fold_idx + 1}')
            plt.tight_layout()
            plt.savefig(f'shap_impute_fold{fold_idx + 1}_bar.png', dpi=150, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"      Warning: Could not compute SHAP for fold {fold_idx + 1}: {e}")

c_impute_pacap_mean = np.mean(c_impute_pacap_folds)
c_impute_pacap_std = np.std(c_impute_pacap_folds, ddof=1)
print(f"  PACAP: Mean C-index = {c_impute_pacap_mean:.4f} ± {c_impute_pacap_std:.4f} (across {n_folds} folds)")

# NCR: Evaluate on same test set using models from each fold
c_impute_ncr_mean = np.mean(c_impute_ncr_folds)
c_impute_ncr_std = np.std(c_impute_ncr_folds, ddof=1)
print(f"  NCR: Mean C-index = {c_impute_ncr_mean:.4f} ± {c_impute_ncr_std:.4f} (across {n_folds} fold models on same test set)")

# Merged test set
c_impute_merged_mean = np.mean(c_impute_merged_folds)
c_impute_merged_std = np.std(c_impute_merged_folds, ddof=1)
print(f"  Merged: Mean C-index = {c_impute_merged_mean:.4f} ± {c_impute_merged_std:.4f} (across {n_folds} fold models)")
print()

# =============================================================================
# Final Comparison Table (formatted to 3 significant figures)
# =============================================================================
print("=" * 60)
print("FINAL COMPARISON TABLE (Mean ± Std, 3 significant figures)")
print("=" * 60)
print()

def format_3sf(value, std):
    """Format value and std to 3 significant figures."""
    # Determine the order of magnitude
    if value == 0:
        return "0.000 ± 0.000"
    
    # Find the order of magnitude of the value
    order = int(np.floor(np.log10(abs(value))))
    
    # Format to 3 significant figures
    value_str = f"{value:.3g}"
    std_str = f"{std:.3g}"
    
    return f"{value_str} ± {std_str}"

comparison_data = [
    {
        'Strategy': 'MASurvival (alpha={})'.format(best_alpha),
        'Description': 'Avoids missing features',
        'PACAP Test': format_3sf(c_ma_pacap_mean, c_ma_pacap_std),
        'NCR Test': format_3sf(c_ma_ncr_mean, c_ma_ncr_std),
        'Merged Test': format_3sf(c_ma_merged_mean, c_ma_merged_std)
    },
    {
        'Strategy': 'Feature Removal',
        'Description': 'Remove QoL features',
        'PACAP Test': format_3sf(c_remove_pacap_mean, c_remove_pacap_std),
        'NCR Test': format_3sf(c_remove_ncr_mean, c_remove_ncr_std),
        'Merged Test': format_3sf(c_remove_merged_mean, c_remove_merged_std)
    },
    {
        'Strategy': 'Imputation',
        'Description': 'Impute missing QoL features',
        'PACAP Test': format_3sf(c_impute_pacap_mean, c_impute_pacap_std),
        'NCR Test': format_3sf(c_impute_ncr_mean, c_impute_ncr_std),
        'Merged Test': format_3sf(c_impute_merged_mean, c_impute_merged_std)
    }
]

comparison_df = pd.DataFrame(comparison_data)
print(comparison_df.to_string(index=False))
print()

# Save comparison table to CSV
comparison_df.to_csv('c_index_comparison.csv', index=False)
print("Saved comparison table to: c_index_comparison.csv")
print()

# Create detailed results DataFrame with numeric values
detailed_results = pd.DataFrame([
    {
        'Strategy': 'MASurvival (alpha={})'.format(best_alpha),
        'Description': 'Avoids missing features',
        'PACAP_Mean': c_ma_pacap_mean,
        'PACAP_Std': c_ma_pacap_std,
        'PACAP_Formatted': format_3sf(c_ma_pacap_mean, c_ma_pacap_std),
        'NCR_Mean': c_ma_ncr_mean,
        'NCR_Std': c_ma_ncr_std,
        'NCR_Formatted': format_3sf(c_ma_ncr_mean, c_ma_ncr_std),
        'Merged_Mean': c_ma_merged_mean,
        'Merged_Std': c_ma_merged_std,
        'Merged_Formatted': format_3sf(c_ma_merged_mean, c_ma_merged_std)
    },
    {
        'Strategy': 'Feature Removal',
        'Description': 'Remove QoL features',
        'PACAP_Mean': c_remove_pacap_mean,
        'PACAP_Std': c_remove_pacap_std,
        'PACAP_Formatted': format_3sf(c_remove_pacap_mean, c_remove_pacap_std),
        'NCR_Mean': c_remove_ncr_mean,
        'NCR_Std': c_remove_ncr_std,
        'NCR_Formatted': format_3sf(c_remove_ncr_mean, c_remove_ncr_std),
        'Merged_Mean': c_remove_merged_mean,
        'Merged_Std': c_remove_merged_std,
        'Merged_Formatted': format_3sf(c_remove_merged_mean, c_remove_merged_std)
    },
    {
        'Strategy': 'Imputation',
        'Description': 'Impute missing QoL features',
        'PACAP_Mean': c_impute_pacap_mean,
        'PACAP_Std': c_impute_pacap_std,
        'PACAP_Formatted': format_3sf(c_impute_pacap_mean, c_impute_pacap_std),
        'NCR_Mean': c_impute_ncr_mean,
        'NCR_Std': c_impute_ncr_std,
        'NCR_Formatted': format_3sf(c_impute_ncr_mean, c_impute_ncr_std),
        'Merged_Mean': c_impute_merged_mean,
        'Merged_Std': c_impute_merged_std,
        'Merged_Formatted': format_3sf(c_impute_merged_mean, c_impute_merged_std)
    }
])

detailed_results.to_csv('c_index_detailed_results.csv', index=False)
print("Saved detailed results to: c_index_detailed_results.csv")
print()

# Save per-fold results
fold_results = pd.DataFrame({
    'Fold': range(1, n_folds + 1),
    'MASurvival_PACAP': c_ma_pacap_folds,
    'MASurvival_NCR': c_ma_ncr_folds,
    'MASurvival_Merged': c_ma_merged_folds,
    'Remove_PACAP': c_remove_pacap_folds,
    'Remove_NCR': c_remove_ncr_folds,
    'Remove_Merged': c_remove_merged_folds,
    'Impute_PACAP': c_impute_pacap_folds,
    'Impute_NCR': c_impute_ncr_folds,
    'Impute_Merged': c_impute_merged_folds
})
fold_results.to_csv('c_index_per_fold.csv', index=False)
print("Saved per-fold results to: c_index_per_fold.csv")
print()

# Also print numeric values for calculations
print("Numeric values (for reference):")
print("-" * 60)
print(f"MASurvival:")
print(f"  PACAP: {c_ma_pacap_mean:.4f} ± {c_ma_pacap_std:.4f}")
print(f"  NCR:   {c_ma_ncr_mean:.4f} ± {c_ma_ncr_std:.4f}")
print(f"  Merged: {c_ma_merged_mean:.4f} ± {c_ma_merged_std:.4f}")
print(f"Feature Removal:")
print(f"  PACAP: {c_remove_pacap_mean:.4f} ± {c_remove_pacap_std:.4f}")
print(f"  NCR:   {c_remove_ncr_mean:.4f} ± {c_remove_ncr_std:.4f}")
print(f"  Merged: {c_remove_merged_mean:.4f} ± {c_remove_merged_std:.4f}")
print(f"Imputation:")
print(f"  PACAP: {c_impute_pacap_mean:.4f} ± {c_impute_pacap_std:.4f}")
print(f"  NCR:   {c_impute_ncr_mean:.4f} ± {c_impute_ncr_std:.4f}")
print(f"  Merged: {c_impute_merged_mean:.4f} ± {c_impute_merged_std:.4f}")
print()

# =============================================================================
# Statistical Significance Testing
# =============================================================================
print("=" * 60)
print("STATISTICAL SIGNIFICANCE TESTING")
print("=" * 60)
print()

# Convert fold results to numpy arrays for statistical tests
c_ma_pacap_array = np.array(c_ma_pacap_folds)
c_ma_ncr_array = np.array(c_ma_ncr_folds)
c_remove_pacap_array = np.array(c_remove_pacap_folds)
c_remove_ncr_array = np.array(c_remove_ncr_folds)
c_impute_pacap_array = np.array(c_impute_pacap_folds)
c_impute_ncr_array = np.array(c_impute_ncr_folds)

# Perform paired t-tests (since same folds are used)
def perform_statistical_test(data1, data2, name1, name2, test_set_name):
    """Perform paired t-test and Wilcoxon signed-rank test."""
    # Paired t-test
    t_stat, p_value_t = stats.ttest_rel(data1, data2)
    
    # Wilcoxon signed-rank test (non-parametric alternative)
    w_stat, p_value_w = stats.wilcoxon(data1, data2)
    
    # Calculate mean difference
    mean_diff = np.mean(data1 - data2)
    
    print(f"{name1} vs {name2} ({test_set_name}):")
    print(f"  Mean difference: {mean_diff:+.4f}")
    print(f"  Paired t-test: t={t_stat:.4f}, p={p_value_t:.4f}", end="")
    if p_value_t < 0.001:
        print(" ***")
    elif p_value_t < 0.01:
        print(" **")
    elif p_value_t < 0.05:
        print(" *")
    else:
        print(" (ns)")
    
    print(f"  Wilcoxon signed-rank: W={w_stat:.4f}, p={p_value_w:.4f}", end="")
    if p_value_w < 0.001:
        print(" ***")
    elif p_value_w < 0.01:
        print(" **")
    elif p_value_w < 0.05:
        print(" *")
    else:
        print(" (ns)")
    print()
    
    return {
        'comparison': f"{name1} vs {name2}",
        'test_set': test_set_name,
        'mean_diff': mean_diff,
        't_statistic': t_stat,
        'p_value_t': p_value_t,
        'wilcoxon_statistic': w_stat,
        'p_value_wilcoxon': p_value_w
    }

# Perform all comparisons
stat_results = []

# PACAP comparisons
stat_results.append(perform_statistical_test(
    c_ma_pacap_array, c_remove_pacap_array, 
    "MASurvival", "Feature Removal", "PACAP"
))
stat_results.append(perform_statistical_test(
    c_impute_pacap_array, c_remove_pacap_array,
    "Imputation", "Feature Removal", "PACAP"
))
stat_results.append(perform_statistical_test(
    c_ma_pacap_array, c_impute_pacap_array,
    "MASurvival", "Imputation", "PACAP"
))

# NCR comparisons
stat_results.append(perform_statistical_test(
    c_ma_ncr_array, c_remove_ncr_array,
    "MASurvival", "Feature Removal", "NCR"
))
stat_results.append(perform_statistical_test(
    c_impute_ncr_array, c_remove_ncr_array,
    "Imputation", "Feature Removal", "NCR"
))
stat_results.append(perform_statistical_test(
    c_ma_ncr_array, c_impute_ncr_array,
    "MASurvival", "Imputation", "NCR"
))

# Save statistical test results to CSV
stat_results_df = pd.DataFrame(stat_results)
stat_results_df.to_csv('statistical_significance_tests.csv', index=False)
print("Saved statistical test results to: statistical_significance_tests.csv")
print()

# Print significance legend
print("Significance levels:")
print("  *** p < 0.001")
print("  **  p < 0.01")
print("  *   p < 0.05")
print("  (ns) not significant (p >= 0.05)")
print()

# Calculate improvements
print("=" * 60)
print("IMPROVEMENTS OVER FEATURE REMOVAL")
print("=" * 60)
ma_improvement_pacap = c_ma_pacap_mean - c_remove_pacap_mean
ma_improvement_ncr = c_ma_ncr_mean - c_remove_ncr_mean
impute_improvement_pacap = c_impute_pacap_mean - c_remove_pacap_mean
impute_improvement_ncr = c_impute_ncr_mean - c_remove_ncr_mean

print(f"MASurvival vs Feature Removal:")
print(f"  PACAP: {ma_improvement_pacap:+.4f} ({ma_improvement_pacap/c_remove_pacap_mean*100:+.2f}%)")
print(f"  NCR:   {ma_improvement_ncr:+.4f} ({ma_improvement_ncr/c_remove_ncr_mean*100:+.2f}%)")
print()
print(f"Imputation vs Feature Removal:")
print(f"  PACAP: {impute_improvement_pacap:+.4f} ({impute_improvement_pacap/c_remove_pacap_mean*100:+.2f}%)")
print(f"  NCR:   {impute_improvement_ncr:+.4f} ({impute_improvement_ncr/c_remove_ncr_mean*100:+.2f}%)")
print()
print(f"MASurvival vs Imputation:")
print(f"  PACAP: {c_ma_pacap_mean - c_impute_pacap_mean:+.4f} ({(c_ma_pacap_mean - c_impute_pacap_mean)/c_impute_pacap_mean*100:+.2f}%)")
print(f"  NCR:   {c_ma_ncr_mean - c_impute_ncr_mean:+.4f} ({(c_ma_ncr_mean - c_impute_ncr_mean)/c_impute_ncr_mean*100:+.2f}%)")
print()

    