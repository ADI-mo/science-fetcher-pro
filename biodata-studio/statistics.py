"""
מודול סטטיסטיקה - ניתוחים סטטיסטיים מתקדמים
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multitest import multipletests


class StatisticalAnalyzer:
    """מבצע ניתוחים סטטיסטיים על תוצאות"""
    
    def __init__(self, results_df):
        """
        Args:
            results_df: DataFrame של תוצאות מ-GrowthCurveAnalyzer
        """
        self.results = results_df
    
    def compare_groups(self, groups_dict, parameter='Growth_Rate (1/h)'):
        """
        משווה בין קבוצות של דגימות
        
        Args:
            groups_dict: מילון של {group_name: [sample_names]}
            parameter: הפרמטר להשוואה
            
        Returns:
            dict עם תוצאות ANOVA ו-post-hoc
        """
        # ארגון הנתונים לפי קבוצות
        group_data = []
        group_labels = []
        
        for group_name, samples in groups_dict.items():
            group_values = self.results[self.results['Sample'].isin(samples)][parameter].values
            group_data.append(group_values)
            group_labels.extend([group_name] * len(group_values))
        
        # ANOVA
        f_stat, p_value = stats.f_oneway(*group_data)
        
        # Post-hoc Tukey HSD (אם יש יותר מ-2 קבוצות)
        posthoc_results = None
        if len(groups_dict) > 2:
            all_values = np.concatenate(group_data)
            tukey_result = pairwise_tukeyhsd(all_values, group_labels, alpha=0.05)
            posthoc_results = pd.DataFrame(data=tukey_result.summary().data[1:],
                                          columns=tukey_result.summary().data[0])
        
        return {
            'anova_f_statistic': f_stat,
            'anova_p_value': p_value,
            'significant': p_value < 0.05,
            'posthoc': posthoc_results
        }
    
    def pairwise_comparisons(self, parameter='Growth_Rate (1/h)', correction='bonferroni'):
        """
        השוואות pairwise בין כל הדגימות
        
        Args:
            parameter: הפרמטר להשוואה
            correction: שיטת תיקון multiple testing
            
        Returns:
            DataFrame עם תוצאות t-tests
        """
        samples = self.results['Sample'].unique()
        comparisons = []
        
        for i, sample1 in enumerate(samples):
            for sample2 in samples[i+1:]:
                val1 = self.results[self.results['Sample'] == sample1][parameter].values
                val2 = self.results[self.results['Sample'] == sample2][parameter].values
                
                # t-test
                t_stat, p_val = stats.ttest_ind(val1, val2)
                
                # effect size (Cohen's d)
                pooled_std = np.sqrt((np.std(val1)**2 + np.std(val2)**2) / 2)
                cohen_d = (np.mean(val1) - np.mean(val2)) / pooled_std if pooled_std > 0 else 0
                
                comparisons.append({
                    'Sample_1': sample1,
                    'Sample_2': sample2,
                    'Mean_1': np.mean(val1),
                    'Mean_2': np.mean(val2),
                    'Difference': np.mean(val1) - np.mean(val2),
                    't_statistic': t_stat,
                    'p_value': p_val,
                    'cohens_d': cohen_d
                })
        
        results_df = pd.DataFrame(comparisons)
        
        # Multiple testing correction
        if len(results_df) > 0:
            reject, pvals_corrected, _, _ = multipletests(
                results_df['p_value'], 
                alpha=0.05, 
                method=correction
            )
            results_df['p_value_corrected'] = pvals_corrected
            results_df['significant'] = reject
        
        return results_df.round(4)
    
    def correlation_analysis(self):
        """
        ניתוח קורלציות בין פרמטרים שונים
        
        Returns:
            מטריצת קורלציה + p-values
        """
        numeric_cols = self.results.select_dtypes(include=[np.number]).columns
        data = self.results[numeric_cols]
        
        # Pearson correlation
        corr_matrix = data.corr()
        
        # P-values
        p_values = pd.DataFrame(np.zeros_like(corr_matrix), 
                               columns=corr_matrix.columns, 
                               index=corr_matrix.index)
        
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i != j:
                    _, p_val = stats.pearsonr(data[col1].dropna(), data[col2].dropna())
                    p_values.iloc[i, j] = p_val
        
        return {
            'correlation_matrix': corr_matrix.round(3),
            'p_values': p_values.round(4)
        }
    
    def outlier_detection(self, parameter='Growth_Rate (1/h)', method='iqr'):
        """
        זיהוי outliers
        
        Args:
            parameter: הפרמטר לבדיקה
            method: 'iqr' או 'zscore'
            
        Returns:
            DataFrame עם דגימות שהן outliers
        """
        values = self.results[parameter].values
        
        if method == 'iqr':
            Q1 = np.percentile(values, 25)
            Q3 = np.percentile(values, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = (values < lower_bound) | (values > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(values))
            outliers = z_scores > 3
        
        else:
            raise ValueError("method חייב להיות 'iqr' או 'zscore'")
        
        outlier_df = self.results[outliers].copy()
        outlier_df['outlier_score'] = values[outliers]
        
        return outlier_df
    
    def generate_summary_table(self):
        """
        יוצר טבלת סיכום סטטיסטית מלאה
        
        Returns:
            DataFrame עם סטטיסטיקה מתוארת
        """
        numeric_cols = self.results.select_dtypes(include=[np.number]).columns
        
        summary = pd.DataFrame({
            'Mean': self.results[numeric_cols].mean(),
            'Median': self.results[numeric_cols].median(),
            'Std': self.results[numeric_cols].std(),
            'Min': self.results[numeric_cols].min(),
            'Max': self.results[numeric_cols].max(),
            'CV (%)': (self.results[numeric_cols].std() / self.results[numeric_cols].mean() * 100)
        })
        
        return summary.round(3)
