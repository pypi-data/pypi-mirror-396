# Base class + inheritance + polymorphism
# src/eda_analyzer.py
"""
EDAAnalyzer module for performing exploratory data analysis (EDA) on datasets.

Provides base and specialized analyzers for numeric and categorical columns
of a pandas DataFrame, generating summary statistics for each type of data.
"""

import pandas as pd
import numpy as np

class EDAAnalyzer:
    """
    Base class for exploratory data analysis (EDA).

    Attributes:
        _df (pd.DataFrame): Protected DataFrame to analyze.
        results (dict): Dictionary to store analysis results.
    """

    def __init__(self, df):
        """
        Initialize the EDAAnalyzer with a DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame for analysis.
        """
        self._df = df
        self.results = {}

    def run_all(self):
        """
        Base method for EDA analysis (to be overridden in child classes).

        Returns:
            dict: Dictionary containing summary statistics of the DataFrame.
        """
        return {"summary": self._df.describe().to_dict()}


class NumericAnalyzer(EDAAnalyzer):
    """
    Performs EDA specifically on numeric columns of a DataFrame.
    """

    def run_all(self):
        """
        Generate summary statistics for numeric columns including:
        - Summary statistics (mean, std, min, max, etc.)
        - Missing value counts and percentages
        - Outlier detection using IQR method
        - Duplicate row count

        Returns:
            dict: Dictionary containing comprehensive numeric analysis.
        """
        num = self._df.select_dtypes(include=[np.number])
        
        # Summary statistics
        self.results['summary'] = num.describe().to_dict()
        
        # Missing values analysis
        self.results['missing'] = {}
        for col in num.columns:
            missing_count = num[col].isna().sum()
            self.results['missing'][col] = {
                'missing': int(missing_count),
                'pct': round((missing_count / len(self._df)) * 100, 2)
            }
        
        # Outlier detection using IQR method
        self.results['outliers'] = {}
        for col in num.columns:
            Q1 = num[col].quantile(0.25)
            Q3 = num[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = ((num[col] < lower_bound) | (num[col] > upper_bound)).sum()
            self.results['outliers'][col] = int(outliers)
        
        # Duplicate rows count
        self.results['duplicates'] = int(self._df.duplicated().sum())
        
        return self.results


class CategoricalAnalyzer(EDAAnalyzer):
    """
    Performs EDA specifically on categorical columns of a DataFrame.
    """

    def run_all(self):
        """
        Generate summary statistics for categorical columns including:
        - Summary statistics (count, unique, top, freq)
        - Missing value counts and percentages

        Returns:
            dict: Dictionary containing comprehensive categorical analysis.
        """
        cat = self._df.select_dtypes(include=['object'])
        
        # Summary statistics for categorical columns
        if not cat.empty:
            self.results['summary'] = cat.describe(include='all').to_dict()
            
            # Missing values analysis for categorical columns
            self.results['missing'] = {}
            for col in cat.columns:
                missing_count = cat[col].isna().sum()
                self.results['missing'][col] = {
                    'missing': int(missing_count),
                    'pct': round((missing_count / len(self._df)) * 100, 2)
                }
        else:
            self.results['summary'] = {}
            self.results['missing'] = {}
        
        return self.results
