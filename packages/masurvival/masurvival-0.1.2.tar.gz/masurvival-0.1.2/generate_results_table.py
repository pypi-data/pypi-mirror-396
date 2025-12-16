"""
Script to generate a formatted results table with PACAP and NCR C-index results
and statistical significance statements.
"""

import pandas as pd
import numpy as np

# =============================================================================
# Load Results
# =============================================================================
print("=" * 80)
print("LOADING RESULTS")
print("=" * 80)
print()

# Load detailed results
try:
    detailed_results = pd.read_csv('c_index_detailed_results.csv')
    print("Loaded: c_index_detailed_results.csv")
except FileNotFoundError:
    print("Error: c_index_detailed_results.csv not found")
    detailed_results = None

# Load comparison table
try:
    comparison_table = pd.read_csv('c_index_comparison.csv')
    print("Loaded: c_index_comparison.csv")
except FileNotFoundError:
    print("Error: c_index_comparison.csv not found")
    comparison_table = None

# Load statistical significance tests
try:
    stat_tests = pd.read_csv('statistical_significance_tests.csv')
    print("Loaded: statistical_significance_tests.csv")
except FileNotFoundError:
    print("Error: statistical_significance_tests.csv not found")
    stat_tests = None

print()

# =============================================================================
# Create Formatted Results Table
# =============================================================================
print("=" * 80)
print("RESULTS TABLE: C-INDEX (Mean ± Std)")
print("=" * 80)
print()

if detailed_results is not None:
    # Create a formatted table
    results_table = pd.DataFrame({
        'Strategy': detailed_results['Strategy'],
        'PACAP Test': detailed_results['PACAP_Formatted'],
        'NCR Test': detailed_results['NCR_Formatted'],
        'Merged Test': detailed_results.get('Merged_Formatted', 'N/A')
    })
    
    print(results_table.to_string(index=False))
    print()
    
    # Save formatted table
    results_table.to_csv('results_summary_table.csv', index=False)
    print("Saved formatted table to: results_summary_table.csv")
    print()

# =============================================================================
# Statistical Significance Analysis
# =============================================================================
print("=" * 80)
print("STATISTICAL SIGNIFICANCE ANALYSIS")
print("=" * 80)
print()

if stat_tests is not None:
    # Create significance summary
    significance_summary = []
    
    for _, row in stat_tests.iterrows():
        comparison = row['comparison']
        test_set = row['test_set']
        mean_diff = row['mean_diff']
        p_value_t = row['p_value_t']
        p_value_w = row['p_value_wilcoxon']
        
        # Determine significance level
        if p_value_t < 0.001:
            sig_level = '***'
            sig_text = 'highly significant (p < 0.001)'
        elif p_value_t < 0.01:
            sig_level = '**'
            sig_text = 'very significant (p < 0.01)'
        elif p_value_t < 0.05:
            sig_level = '*'
            sig_text = 'significant (p < 0.05)'
        else:
            sig_level = 'ns'
            sig_text = 'not significant (p >= 0.05)'
        
        significance_summary.append({
            'Comparison': comparison,
            'Test Set': test_set,
            'Mean Difference': f"{mean_diff:+.4f}",
            'p-value (t-test)': f"{p_value_t:.4f}",
            'p-value (Wilcoxon)': f"{p_value_w:.4f}",
            'Significance': sig_level,
            'Interpretation': sig_text
        })
    
    sig_df = pd.DataFrame(significance_summary)
    print(sig_df.to_string(index=False))
    print()
    
    # Save significance summary
    sig_df.to_csv('statistical_significance_summary.csv', index=False)
    print("Saved significance summary to: statistical_significance_summary.csv")
    print()

# =============================================================================
# Generate Significance Statements
# =============================================================================
print("=" * 80)
print("SIGNIFICANCE STATEMENTS")
print("=" * 80)
print()

if stat_tests is not None:
    # Group by test set
    pacap_tests = stat_tests[stat_tests['test_set'] == 'PACAP']
    ncr_tests = stat_tests[stat_tests['test_set'] == 'NCR']
    
    print("PACAP TEST SET:")
    print("-" * 80)
    for _, row in pacap_tests.iterrows():
        comparison = row['comparison']
        mean_diff = row['mean_diff']
        p_value_t = row['p_value_t']
        
        if p_value_t < 0.001:
            sig_statement = f"*** Highly significant (p < 0.001)"
        elif p_value_t < 0.01:
            sig_statement = f"** Very significant (p < 0.01)"
        elif p_value_t < 0.05:
            sig_statement = f"* Significant (p < 0.05)"
        else:
            sig_statement = "(Not significant, p >= 0.05)"
        
        direction = "better" if mean_diff > 0 else "worse"
        print(f"  {comparison}:")
        print(f"    Mean difference: {mean_diff:+.4f} ({direction})")
        print(f"    {sig_statement}")
        print()
    
    print("\nNCR TEST SET:")
    print("-" * 80)
    for _, row in ncr_tests.iterrows():
        comparison = row['comparison']
        mean_diff = row['mean_diff']
        p_value_t = row['p_value_t']
        
        if p_value_t < 0.001:
            sig_statement = f"*** Highly significant (p < 0.001)"
        elif p_value_t < 0.01:
            sig_statement = f"** Very significant (p < 0.01)"
        elif p_value_t < 0.05:
            sig_statement = f"* Significant (p < 0.05)"
        else:
            sig_statement = "(Not significant, p >= 0.05)"
        
        direction = "better" if mean_diff > 0 else "worse"
        print(f"  {comparison}:")
        print(f"    Mean difference: {mean_diff:+.4f} ({direction})")
        print(f"    {sig_statement}")
        print()

# =============================================================================
# Create Publication-Ready Table
# =============================================================================
print("=" * 80)
print("PUBLICATION-READY TABLE")
print("=" * 80)
print()

if detailed_results is not None and stat_tests is not None:
    # Create a comprehensive table with significance markers
    pub_table_data = []
    
    for _, row in detailed_results.iterrows():
        strategy = row['Strategy']
        
        # Get PACAP results
        pacap_mean = row['PACAP_Mean']
        pacap_std = row['PACAP_Std']
        pacap_formatted = row['PACAP_Formatted']
        
        # Get NCR results
        ncr_mean = row['NCR_Mean']
        ncr_std = row['NCR_Std']
        ncr_formatted = row['NCR_Formatted']
        
        # Get merged results if available
        merged_formatted = row.get('Merged_Formatted', 'N/A')
        
        pub_table_data.append({
            'Strategy': strategy,
            'PACAP C-index': pacap_formatted,
            'NCR C-index': ncr_formatted,
            'Merged C-index': merged_formatted
        })
    
    pub_table = pd.DataFrame(pub_table_data)
    
    # Add significance notes
    print(pub_table.to_string(index=False))
    print()
    print("Significance levels:")
    print("  *** p < 0.001")
    print("  **  p < 0.01")
    print("  *   p < 0.05")
    print("  ns  not significant (p >= 0.05)")
    print()
    
    # Create detailed significance table
    print("=" * 80)
    print("DETAILED SIGNIFICANCE COMPARISONS")
    print("=" * 80)
    print()
    
    sig_comparison_table = []
    
    for _, row in stat_tests.iterrows():
        comparison = row['comparison']
        test_set = row['test_set']
        mean_diff = row['mean_diff']
        p_value_t = row['p_value_t']
        p_value_w = row['p_value_wilcoxon']
        
        # Format p-value
        if p_value_t < 0.001:
            p_formatted = "<0.001"
            sig_marker = "***"
        elif p_value_t < 0.01:
            p_formatted = f"{p_value_t:.3f}"
            sig_marker = "**"
        elif p_value_t < 0.05:
            p_formatted = f"{p_value_t:.3f}"
            sig_marker = "*"
        else:
            p_formatted = f"{p_value_t:.3f}"
            sig_marker = "ns"
        
        sig_comparison_table.append({
            'Comparison': comparison,
            'Test Set': test_set,
            'Difference': f"{mean_diff:+.4f}",
            'p-value': p_formatted,
            'Significance': sig_marker
        })
    
    sig_comparison_df = pd.DataFrame(sig_comparison_table)
    print(sig_comparison_df.to_string(index=False))
    print()
    
    # Save publication-ready tables
    pub_table.to_csv('publication_table.csv', index=False)
    sig_comparison_df.to_csv('significance_comparisons.csv', index=False)
    print("Saved publication tables:")
    print("  - publication_table.csv")
    print("  - significance_comparisons.csv")
    print()

# =============================================================================
# Summary of Significant Results
# =============================================================================
print("=" * 80)
print("SUMMARY: SIGNIFICANT RESULTS")
print("=" * 80)
print()

if stat_tests is not None:
    significant_results = stat_tests[stat_tests['p_value_t'] < 0.05]
    
    if len(significant_results) > 0:
        print(f"Found {len(significant_results)} statistically significant comparisons (p < 0.05):")
        print()
        
        for _, row in significant_results.iterrows():
            comparison = row['comparison']
            test_set = row['test_set']
            mean_diff = row['mean_diff']
            p_value = row['p_value_t']
            
            strategy1, strategy2 = comparison.split(' vs ')
            
            if mean_diff > 0:
                conclusion = f"{strategy1} significantly outperforms {strategy2}"
            else:
                conclusion = f"{strategy2} significantly outperforms {strategy1}"
            
            print(f"  {test_set}: {comparison}")
            print(f"    {conclusion} (difference: {mean_diff:+.4f}, p={p_value:.4f})")
            print()
    else:
        print("No statistically significant differences found (p < 0.05)")
        print()
    
    # Non-significant results
    non_significant = stat_tests[stat_tests['p_value_t'] >= 0.05]
    if len(non_significant) > 0:
        print(f"Non-significant comparisons (p >= 0.05): {len(non_significant)}")
        for _, row in non_significant.iterrows():
            print(f"  {row['test_set']}: {row['comparison']} (p={row['p_value_t']:.4f})")
        print()

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print()
print("Generated files:")
print("  - results_summary_table.csv: Formatted results table")
print("  - statistical_significance_summary.csv: Detailed significance analysis")
print("  - publication_table.csv: Publication-ready table")
print("  - significance_comparisons.csv: Significance comparison table")
print()

