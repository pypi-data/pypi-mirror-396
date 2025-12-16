"""
Script to plot pretreatment QoL summary vs. survival.

This script:
1. Loads PACAP and NCR datasets
2. Calculates pretreatment QoL summary (sum of QoL features)
3. Creates survival plots stratified by QoL summary (e.g., high vs low QoL)
4. Generates Kaplan-Meier curves and other survival visualizations
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from masurvival.util import Surv
from masurvival.nonparametric import kaplan_meier_estimator
from masurvival.compare import compare_survival
from scipy import stats

# Set style
sns.set_style("whitegrid")
rcParams['figure.figsize'] = (12, 8)
rcParams['font.size'] = 12

# QoL features (pretreatment) - matching pancreas_survival.py
qol_features = [
    'qol_summary_pretreatment',  # summary score
    'qol_physical_pretreatment',
    'qol_social_pretreatment',
    'qol_emotional_pretreatment',
    'qol_cognitive_pretreatment',
    'qol_role_pretreatment'
]

# Feature translations for English names
FEATURE_TRANSLATIONS = {
    'qol_summary_pretreatment': 'QoL Summary (Pretreatment)',
    'qol_physical_pretreatment': 'QoL Physical (Pretreatment)',
    'qol_emotional_pretreatment': 'QoL Emotional (Pretreatment)',
    'qol_social_pretreatment': 'QoL Social (Pretreatment)',
    'qol_functional_pretreatment': 'QoL Functional (Pretreatment)',
    'leeft_cat': 'Age Category',
    'gesl': 'Gender',
    'klin_tum_afm': 'Maximum Size of Primary Tumor',
}

def translate_feature_name(feat_name):
    """Translate feature name from Dutch to English."""
    return FEATURE_TRANSLATIONS.get(feat_name, feat_name.replace('_', ' ').title())

# =============================================================================
# Load Data
# =============================================================================
print("=" * 60)
print("LOADING DATA")
print("=" * 60)
print()

# Load PACAP data
print("Loading PACAP data...")
df_pacap = pd.read_csv('merged_pacap_data.csv')
print(f"  Loaded {len(df_pacap)} PACAP patients")

# Load NCR data
print("Loading NCR data...")
df_ncr_all = pd.read_csv('merged_datasets.csv')
print(f"  Loaded {len(df_ncr_all)} NCR patients (before removing PACAP)")

# Remove PACAP patients from NCR data (using key_nkr as patient identifier)
if 'key_nkr' in df_pacap.columns and 'key_nkr' in df_ncr_all.columns:
    pacap_ids = set(df_pacap['key_nkr'].dropna().unique())
    df_ncr = df_ncr_all[~df_ncr_all['key_nkr'].isin(pacap_ids)].copy()
    print(f"  Removed {len(df_ncr_all) - len(df_ncr)} PACAP patients from NCR data")
else:
    df_ncr = df_ncr_all.copy()
    print("  Warning: Could not match patient IDs (key_nkr), using all NCR data")

print(f"  Final NCR dataset: {len(df_ncr)} patients")
print()

# =============================================================================
# Prepare QoL Summary
# =============================================================================
print("=" * 60)
print("PREPARING QoL SUMMARY")
print("=" * 60)
print()

def calculate_qol_summary(df, qol_features, dataset_name):
    """Calculate QoL summary for a dataset."""
    print(f"\n{dataset_name}:")
    
    # Check which QoL features are available
    available_qol = [f for f in qol_features if f in df.columns]
    missing_qol = [f for f in qol_features if f not in df.columns]
    
    if missing_qol:
        print(f"  Warning: Missing QoL features: {missing_qol}")
    
    if not available_qol:
        print(f"  Error: No QoL features available!")
        return None, None, None
    
    print(f"  Available QoL features: {available_qol}")
    
    # Calculate summary (sum of available QoL features)
    qol_data = df[available_qol].copy()
    
    # Count missing values per patient
    n_missing_per_patient = qol_data.isna().sum(axis=1)
    n_available_per_patient = len(available_qol) - n_missing_per_patient
    
    # Calculate sum only for patients with at least some QoL data
    qol_summary = qol_data.sum(axis=1)
    
    # Set to NaN if all QoL features are missing
    qol_summary[n_missing_per_patient == len(available_qol)] = np.nan
    
    # Calculate mean QoL (average of available features) as alternative
    qol_mean = qol_data.mean(axis=1)
    qol_mean[n_missing_per_patient == len(available_qol)] = np.nan
    
    # Statistics
    n_with_qol = (~qol_summary.isna()).sum()
    n_without_qol = qol_summary.isna().sum()
    
    print(f"  Patients with QoL data: {n_with_qol} ({n_with_qol/len(df)*100:.1f}%)")
    print(f"  Patients without QoL data: {n_without_qol} ({n_without_qol/len(df)*100:.1f}%)")
    
    if n_with_qol > 0:
        print(f"  QoL Summary (sum): mean={qol_summary.mean():.2f}, std={qol_summary.std():.2f}")
        print(f"  QoL Summary (mean): mean={qol_mean.mean():.2f}, std={qol_mean.std():.2f}")
        print(f"  QoL Summary range: [{qol_summary.min():.2f}, {qol_summary.max():.2f}]")
    
    return qol_summary, qol_mean, available_qol

# Calculate QoL summaries
qol_summary_pacap, qol_mean_pacap, available_qol_pacap = calculate_qol_summary(
    df_pacap, qol_features, "PACAP"
)

qol_summary_ncr, qol_mean_ncr, available_qol_ncr = calculate_qol_summary(
    df_ncr, qol_features, "NCR"
)

# =============================================================================
# Prepare Survival Data
# =============================================================================
print("\n" + "=" * 60)
print("PREPARING SURVIVAL DATA")
print("=" * 60)
print()

# PACAP survival
if 'vit_stat' in df_pacap.columns and 'vit_stat_int' in df_pacap.columns:
    y_pacap = Surv.from_arrays(
        event=df_pacap['vit_stat'].astype(bool),
        time=df_pacap['vit_stat_int'].astype(float)
    )
    print(f"PACAP: {len(y_pacap)} patients")
    print(f"  Events: {y_pacap['event'].sum()} ({y_pacap['event'].sum()/len(y_pacap)*100:.1f}%)")
    print(f"  Censored: {(~y_pacap['event']).sum()} ({(~y_pacap['event']).sum()/len(y_pacap)*100:.1f}%)")
    print(f"  Median survival time: {np.median(y_pacap['time']):.1f} months")
else:
    print("Warning: PACAP survival columns not found")
    y_pacap = None

# NCR survival
if 'vit_stat' in df_ncr.columns and 'vit_stat_int' in df_ncr.columns:
    y_ncr = Surv.from_arrays(
        event=df_ncr['vit_stat'].astype(bool),
        time=df_ncr['vit_stat_int'].astype(float)
    )
    print(f"\nNCR: {len(y_ncr)} patients")
    print(f"  Events: {y_ncr['event'].sum()} ({y_ncr['event'].sum()/len(y_ncr)*100:.1f}%)")
    print(f"  Censored: {(~y_ncr['event']).sum()} ({(~y_ncr['event']).sum()/len(y_ncr)*100:.1f}%)")
    print(f"  Median survival time: {np.median(y_ncr['time']):.1f} months")
else:
    print("Warning: NCR survival columns not found")
    y_ncr = None

# =============================================================================
# Identify Subpopulations
# =============================================================================
print("\n" + "=" * 60)
print("IDENTIFYING SUBPOPULATIONS")
print("=" * 60)
print()

def identify_subpopulations(df, dataset_name):
    """Identify subpopulations based on resectability status."""
    print(f"\n{dataset_name}:")
    
    # Check for resectability status column
    if 'resectability_status' in df.columns:
        print(f"  Found 'resectability_status' column")
        print(f"  Unique values: {df['resectability_status'].value_counts().to_dict()}")
        
        # Define subpopulations
        subpopulations = {
            'metastatic': df['resectability_status'].str.lower().str.contains('metastatic|metastases', case=False, na=False),
            'lapc': df['resectability_status'].str.lower().str.contains('lapc|locally advanced', case=False, na=False),
            'borderline': df['resectability_status'].str.lower().str.contains('borderline', case=False, na=False),
            'resectable': df['resectability_status'].str.lower().str.contains('resectable|resectability', case=False, na=False),
        }
        
        # Print counts
        for name, mask in subpopulations.items():
            print(f"  {name.capitalize()}: {mask.sum()} patients")
        
        return subpopulations
    else:
        print(f"  Warning: 'resectability_status' column not found")
        print(f"  Available columns with 'resect' or 'stage' or 'meta':")
        relevant_cols = [col for col in df.columns if any(term in col.lower() for term in ['resect', 'stage', 'meta', 'stadium'])]
        for col in relevant_cols[:10]:
            print(f"    - {col}")
        
        # Try alternative column names
        alternative_cols = ['stadium', 'cstadium', 'stage', 'resectability']
        for col in alternative_cols:
            if col in df.columns:
                print(f"  Found alternative column: {col}")
                print(f"  Unique values: {df[col].value_counts().head().to_dict()}")
        
        return None

# Identify subpopulations
subpop_pacap = identify_subpopulations(df_pacap, "PACAP")
subpop_ncr = identify_subpopulations(df_ncr, "NCR")

# =============================================================================
# Create QoL Groups (High vs Low)
# =============================================================================
print("\n" + "=" * 60)
print("CREATING QoL GROUPS")
print("=" * 60)
print()

def create_qol_groups(qol_summary, dataset_name, method='median'):
    """Create high/low QoL groups based on summary."""
    if qol_summary is None or qol_summary.isna().all():
        print(f"{dataset_name}: No QoL data available")
        return None, None
    
    qol_valid = qol_summary.dropna()
    
    if len(qol_valid) == 0:
        print(f"{dataset_name}: No valid QoL data")
        return None, None
    
    if method == 'median':
        threshold = qol_valid.median()
        print(f"{dataset_name}:")
        print(f"  Median QoL threshold: {threshold:.2f}")
    elif method == 'tertile':
        threshold = qol_valid.quantile(0.33)
        print(f"{dataset_name}:")
        print(f"  33rd percentile threshold: {threshold:.2f}")
    else:
        threshold = qol_valid.mean()
        print(f"{dataset_name}:")
        print(f"  Mean QoL threshold: {threshold:.2f}")
    
    # Create groups
    high_qol = qol_summary >= threshold
    low_qol = qol_summary < threshold
    missing_qol = qol_summary.isna()
    
    print(f"  High QoL (≥{threshold:.2f}): {high_qol.sum()} patients")
    print(f"  Low QoL (<{threshold:.2f}): {low_qol.sum()} patients")
    print(f"  Missing QoL: {missing_qol.sum()} patients")
    
    return high_qol, low_qol

# Create groups for PACAP
high_qol_pacap, low_qol_pacap = create_qol_groups(qol_summary_pacap, "PACAP", method='median')

# Create groups for NCR
high_qol_ncr, low_qol_ncr = create_qol_groups(qol_summary_ncr, "NCR", method='median')

# =============================================================================
# Plot Kaplan-Meier Curves
# =============================================================================
print("\n" + "=" * 60)
print("GENERATING SURVIVAL PLOTS")
print("=" * 60)
print()

def plot_kaplan_meier(y, groups, group_names, title, ax=None, colors=None):
    """Plot Kaplan-Meier survival curves for different groups."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    if colors is None:
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    for i, (group_mask, group_name) in enumerate(zip(groups, group_names)):
        if group_mask is None or group_mask.sum() == 0:
            continue
        
        y_group = y[group_mask]
        
        if len(y_group) == 0:
            continue
        
        # Calculate Kaplan-Meier
        time, survival_prob = kaplan_meier_estimator(
            y_group['event'],
            y_group['time']
        )
        
        # Plot
        ax.step(time, survival_prob, where='post', label=group_name, 
                linewidth=2.5, color=colors[i % len(colors)])
        
        # Add number at risk
        ax.text(time[-1] if len(time) > 0 else 0, 
                survival_prob[-1] if len(survival_prob) > 0 else 0,
                f'  n={group_mask.sum()}', 
                verticalalignment='bottom',
                fontsize=10)
    
    ax.set_xlabel('Time (months)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Survival Probability', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim([0, 1.05])
    
    return ax

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Pretreatment QoL Summary vs. Survival', fontsize=16, fontweight='bold', y=0.995)

# PACAP: High vs Low QoL
if y_pacap is not None and high_qol_pacap is not None and low_qol_pacap is not None:
    ax1 = axes[0, 0]
    plot_kaplan_meier(
        y_pacap,
        [high_qol_pacap, low_qol_pacap],
        ['High QoL', 'Low QoL'],
        'PACAP: High vs Low QoL (Median Split)',
        ax=ax1,
        colors=['#2E86AB', '#A23B72']
    )
    
    # Log-rank test
    try:
        y_high = y_pacap[high_qol_pacap]
        y_low = y_pacap[low_qol_pacap]
        result = compare_survival(y_high, y_low)
        p_value = result.p_value
        ax1.text(0.05, 0.05, f'Log-rank test: p={p_value:.4f}', 
                transform=ax1.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    except:
        pass

# NCR: High vs Low QoL
if y_ncr is not None and high_qol_ncr is not None and low_qol_ncr is not None:
    ax2 = axes[0, 1]
    plot_kaplan_meier(
        y_ncr,
        [high_qol_ncr, low_qol_ncr],
        ['High QoL', 'Low QoL'],
        'NCR: High vs Low QoL (Median Split)',
        ax=ax2,
        colors=['#2E86AB', '#A23B72']
    )
    
    # Log-rank test
    try:
        y_high = y_ncr[high_qol_ncr]
        y_low = y_ncr[low_qol_ncr]
        result = compare_survival(y_high, y_low)
        p_value = result.p_value
        ax2.text(0.05, 0.05, f'Log-rank test: p={p_value:.4f}', 
                transform=ax2.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    except:
        pass

# Combined: PACAP + NCR
if (y_pacap is not None and y_ncr is not None and 
    high_qol_pacap is not None and low_qol_pacap is not None and
    high_qol_ncr is not None and low_qol_ncr is not None):
    
    # Combine datasets
    y_combined = np.concatenate([y_pacap, y_ncr])
    high_qol_combined = np.concatenate([high_qol_pacap.values, high_qol_ncr.values])
    low_qol_combined = np.concatenate([low_qol_pacap.values, low_qol_ncr.values])
    
    ax3 = axes[1, 0]
    plot_kaplan_meier(
        y_combined,
        [high_qol_combined, low_qol_combined],
        ['High QoL', 'Low QoL'],
        'Combined (PACAP + NCR): High vs Low QoL',
        ax=ax3,
        colors=['#2E86AB', '#A23B72']
    )
    
    # Log-rank test
    try:
        y_high = y_combined[high_qol_combined]
        y_low = y_combined[low_qol_combined]
        result = compare_survival(y_high, y_low)
        p_value = result.p_value
        ax3.text(0.05, 0.05, f'Log-rank test: p={p_value:.4f}', 
                transform=ax3.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    except:
        pass

# QoL Distribution
ax4 = axes[1, 1]
if qol_summary_pacap is not None and qol_summary_ncr is not None:
    qol_pacap_valid = qol_summary_pacap.dropna()
    qol_ncr_valid = qol_summary_ncr.dropna()
    
    if len(qol_pacap_valid) > 0 and len(qol_ncr_valid) > 0:
        ax4.hist(qol_pacap_valid, bins=30, alpha=0.6, label='PACAP', 
                color='#2E86AB', edgecolor='black')
        ax4.hist(qol_ncr_valid, bins=30, alpha=0.6, label='NCR', 
                color='#A23B72', edgecolor='black')
        ax4.axvline(qol_pacap_valid.median(), color='#2E86AB', linestyle='--', 
                   linewidth=2, label=f'PACAP median: {qol_pacap_valid.median():.1f}')
        ax4.axvline(qol_ncr_valid.median(), color='#A23B72', linestyle='--', 
                   linewidth=2, label=f'NCR median: {qol_ncr_valid.median():.1f}')
        ax4.set_xlabel('QoL Summary (Sum)', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax4.set_title('Distribution of QoL Summary', fontsize=14, fontweight='bold')
        ax4.legend(fontsize=11)
        ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('qol_survival_plots.png', dpi=300, bbox_inches='tight')
print("Saved plot to: qol_survival_plots.png")
plt.close()

# =============================================================================
# Additional Analysis: QoL as Continuous Variable
# =============================================================================
print("\n" + "=" * 60)
print("QoL AS CONTINUOUS VARIABLE ANALYSIS")
print("=" * 60)
print()

def analyze_continuous_qol(y, qol_summary, dataset_name):
    """Analyze QoL as a continuous variable using Cox regression."""
    if y is None or qol_summary is None:
        return
    
    # Only use patients with both survival and QoL data
    valid_mask = ~qol_summary.isna()
    y_valid = y[valid_mask]
    qol_valid = qol_summary[valid_mask]
    
    if len(y_valid) == 0:
        print(f"{dataset_name}: No valid data for analysis")
        return
    
    print(f"\n{dataset_name}:")
    print(f"  Patients with both survival and QoL data: {len(y_valid)}")
    
    # Simple correlation analysis
    # Create risk groups based on QoL quartiles
    quartiles = qol_valid.quantile([0.25, 0.5, 0.75])
    
    q1_mask = qol_valid <= quartiles[0.25]
    q2_mask = (qol_valid > quartiles[0.25]) & (qol_valid <= quartiles[0.5])
    q3_mask = (qol_valid > quartiles[0.5]) & (qol_valid <= quartiles[0.75])
    q4_mask = qol_valid > quartiles[0.75]
    
    print(f"  Q1 (≤{quartiles[0.25]:.2f}): {q1_mask.sum()} patients")
    print(f"  Q2 ({quartiles[0.25]:.2f}-{quartiles[0.5]:.2f}): {q2_mask.sum()} patients")
    print(f"  Q3 ({quartiles[0.5]:.2f}-{quartiles[0.75]:.2f}): {q3_mask.sum()} patients")
    print(f"  Q4 (>{quartiles[0.75]:.2f}): {q4_mask.sum()} patients")
    
    # Plot quartile survival curves
    fig, ax = plt.subplots(figsize=(10, 6))
    
    quartile_masks = [q1_mask, q2_mask, q3_mask, q4_mask]
    quartile_names = [f'Q1 (Lowest)', f'Q2', f'Q3', f'Q4 (Highest)']
    colors_quartiles = ['#C73E1D', '#F18F01', '#2E86AB', '#06A77D']
    
    for i, (q_mask, q_name) in enumerate(zip(quartile_masks, quartile_names)):
        y_q = y_valid[q_mask]
        if len(y_q) == 0:
            continue
        
        time, survival_prob = kaplan_meier_estimator(
            y_q['event'],
            y_q['time']
        )
        
        ax.step(time, survival_prob, where='post', label=q_name, 
                linewidth=2.5, color=colors_quartiles[i])
        
        ax.text(time[-1] if len(time) > 0 else 0, 
                survival_prob[-1] if len(survival_prob) > 0 else 0,
                f'  n={q_mask.sum()}', 
                verticalalignment='bottom',
                fontsize=10)
    
    ax.set_xlabel('Time (months)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Survival Probability', fontsize=12, fontweight='bold')
    ax.set_title(f'{dataset_name}: Survival by QoL Quartiles', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim([0, 1.05])
    
    plt.tight_layout()
    plt.savefig(f'qol_quartiles_{dataset_name.lower()}.png', dpi=300, bbox_inches='tight')
    print(f"  Saved quartile plot to: qol_quartiles_{dataset_name.lower()}.png")
    plt.close()

# Analyze continuous QoL
if y_pacap is not None:
    analyze_continuous_qol(y_pacap, qol_summary_pacap, "PACAP")

if y_ncr is not None:
    analyze_continuous_qol(y_ncr, qol_summary_ncr, "NCR")

# =============================================================================
# Subpopulation Analysis: QoL vs Survival by Resectability Status
# =============================================================================
print("\n" + "=" * 60)
print("SUBPOPULATION ANALYSIS: QoL vs SURVIVAL BY RESECTABILITY STATUS")
print("=" * 60)
print()

def plot_subpopulation_survival(y, qol_summary, subpopulations, dataset_name, 
                                high_qol_mask, low_qol_mask):
    """Plot survival curves for each subpopulation stratified by QoL."""
    if y is None or qol_summary is None or subpopulations is None:
        return
    
    if high_qol_mask is None or low_qol_mask is None:
        return
    
    # Filter to patients with QoL data
    has_qol = ~qol_summary.isna()
    y_with_qol = y[has_qol]
    high_qol_with_data = high_qol_mask[has_qol]
    low_qol_with_data = low_qol_mask[has_qol]
    
    # Create figure with subplots for each subpopulation
    subpop_names = ['metastatic', 'lapc', 'borderline', 'resectable']
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'{dataset_name}: QoL vs Survival by Subpopulation', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    axes_flat = axes.flatten()
    
    for idx, subpop_name in enumerate(subpop_names):
        if subpop_name not in subpopulations:
            axes_flat[idx].axis('off')
            continue
        
        ax = axes_flat[idx]
        subpop_mask = subpopulations[subpop_name]
        
        # Filter to subpopulation with QoL data
        subpop_with_qol = subpop_mask[has_qol]
        
        if subpop_with_qol.sum() == 0:
            ax.text(0.5, 0.5, f'No {subpop_name} patients\nwith QoL data', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(f'{subpop_name.capitalize()}', fontsize=14, fontweight='bold')
            continue
        
        # High and low QoL within this subpopulation
        high_qol_subpop = high_qol_with_data & subpop_with_qol
        low_qol_subpop = low_qol_with_data & subpop_with_qol
        
        if high_qol_subpop.sum() == 0 and low_qol_subpop.sum() == 0:
            ax.text(0.5, 0.5, f'No QoL data for\n{subpop_name} patients', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(f'{subpop_name.capitalize()}', fontsize=14, fontweight='bold')
            continue
        
        # Plot survival curves
        groups = []
        group_names = []
        
        if high_qol_subpop.sum() > 0:
            groups.append(high_qol_subpop)
            group_names.append(f'High QoL (n={high_qol_subpop.sum()})')
        
        if low_qol_subpop.sum() > 0:
            groups.append(low_qol_subpop)
            group_names.append(f'Low QoL (n={low_qol_subpop.sum()})')
        
        if len(groups) > 0:
            plot_kaplan_meier(
                y_with_qol,
                groups,
                group_names,
                f'{subpop_name.capitalize()}',
                ax=ax,
                colors=['#2E86AB', '#A23B72']
            )
            
            # Log-rank test if both groups have data
            if len(groups) == 2 and high_qol_subpop.sum() > 0 and low_qol_subpop.sum() > 0:
                try:
                    y_high = y_with_qol[high_qol_subpop]
                    y_low = y_with_qol[low_qol_subpop]
                    result = compare_survival(y_high, y_low)
                    p_value = result.p_value
                    ax.text(0.05, 0.05, f'Log-rank: p={p_value:.4f}', 
                           transform=ax.transAxes, fontsize=10,
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                except Exception as e:
                    pass
    
    plt.tight_layout()
    plt.savefig(f'qol_survival_subpopulations_{dataset_name.lower()}.png', 
                dpi=300, bbox_inches='tight')
    print(f"Saved subpopulation plots to: qol_survival_subpopulations_{dataset_name.lower()}.png")
    plt.close()

# Plot subpopulation analysis for PACAP
if y_pacap is not None and subpop_pacap is not None:
    plot_subpopulation_survival(
        y_pacap, qol_summary_pacap, subpop_pacap, "PACAP",
        high_qol_pacap, low_qol_pacap
    )

# Plot subpopulation analysis for NCR
if y_ncr is not None and subpop_ncr is not None:
    plot_subpopulation_survival(
        y_ncr, qol_summary_ncr, subpop_ncr, "NCR",
        high_qol_ncr, low_qol_ncr
    )

# Combined dataset subpopulation analysis
if (y_pacap is not None and y_ncr is not None and 
    subpop_pacap is not None and subpop_ncr is not None and
    high_qol_pacap is not None and low_qol_pacap is not None and
    high_qol_ncr is not None and low_qol_ncr is not None):
    
    # Combine subpopulations
    combined_subpop = {}
    for subpop_name in ['metastatic', 'lapc', 'borderline', 'resectable']:
        if subpop_name in subpop_pacap and subpop_name in subpop_ncr:
            combined_mask = np.concatenate([
                subpop_pacap[subpop_name].values,
                subpop_ncr[subpop_name].values
            ])
            combined_subpop[subpop_name] = combined_mask
    
    if len(combined_subpop) > 0:
        # Combine QoL and survival data
        qol_combined = pd.concat([qol_summary_pacap, qol_summary_ncr], ignore_index=True)
        y_combined = np.concatenate([y_pacap, y_ncr])
        high_qol_combined = np.concatenate([high_qol_pacap.values, high_qol_ncr.values])
        low_qol_combined = np.concatenate([low_qol_pacap.values, low_qol_ncr.values])
        
        plot_subpopulation_survival(
            y_combined, qol_combined, combined_subpop, "Combined",
            pd.Series(high_qol_combined), pd.Series(low_qol_combined)
        )

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
print()
print("Generated plots:")
print("  - qol_survival_plots.png: Main survival plots (high vs low QoL)")
print("  - qol_quartiles_pacap.png: PACAP survival by QoL quartiles")
print("  - qol_quartiles_ncr.png: NCR survival by QoL quartiles")
if subpop_pacap is not None:
    print("  - qol_survival_subpopulations_pacap.png: PACAP survival by subpopulation")
if subpop_ncr is not None:
    print("  - qol_survival_subpopulations_ncr.png: NCR survival by subpopulation")
if (subpop_pacap is not None and subpop_ncr is not None):
    print("  - qol_survival_subpopulations_combined.png: Combined survival by subpopulation")
print()

