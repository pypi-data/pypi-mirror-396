# Encapsulation + methods
# src/quality_scorer.py
"""
QualityScorer module for computing weighted data quality metrics.

This module evaluates different aspects of dataset quality using
EDA outputs, including:
- Missing value quality
- Duplicate row quality
- Outlier impact
- Balance score (placeholder)
It also computes a final weighted overall quality score.
"""

import numpy as np

class QualityScorer:
    """
    Class for computing multiple data quality scores based on EDA results.

    Attributes:
        _eda (dict): Protected dictionary of EDA results (missing, duplicates, outliers).
        _df_len (int): Number of rows in the dataset.
        _weights (dict): Custom weights for each metric (must sum to 1.0).
        scores (dict): Stores individual metric scores and final overall score.
    """

    # Default weights as class attribute
    DEFAULT_WEIGHTS = {
        'missing': 0.35,
        'duplicates': 0.15,
        'outliers': 0.25,
        'balance': 0.25
    }

    def __init__(self, eda_results, df_len, custom_weights=None):
        """
        Initialize the QualityScorer with EDA results and dataset length.

        Args:
            eda_results (dict): Output dictionary from the EDAAnalyzer modules.
            df_len (int): Total number of rows in the dataset.
            custom_weights (dict, optional): Custom weights for scoring metrics.
                Must contain keys: 'missing', 'duplicates', 'outliers', 'balance'.
                Values must sum to 1.0. Defaults to None (uses DEFAULT_WEIGHTS).

        Raises:
            ValueError: If custom_weights don't sum to 1.0 or contain invalid keys.
        """
        self._eda = eda_results
        self._df_len = df_len
        self.scores = {}
        
        # Set weights - use custom if provided, otherwise use defaults
        if custom_weights is not None:
            self._validate_weights(custom_weights)
            self._weights = custom_weights
        else:
            self._weights = self.DEFAULT_WEIGHTS.copy()

    def _validate_weights(self, weights):
        """
        Validate that custom weights are properly formatted.

        Args:
            weights (dict): Custom weights to validate.

        Raises:
            ValueError: If weights are invalid.
        """
        required_keys = {'missing', 'duplicates', 'outliers', 'balance'}
        
        # Check if all required keys are present
        if set(weights.keys()) != required_keys:
            raise ValueError(
                f"Custom weights must contain exactly these keys: {required_keys}. "
                f"Got: {set(weights.keys())}"
            )
        
        # Check if all values are numeric and positive
        for key, value in weights.items():
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(
                    f"Weight for '{key}' must be a positive number. Got: {value}"
                )
        
        # Check if weights sum to 1.0 (with small tolerance for floating point errors)
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"Weights must sum to 1.0. Current sum: {total:.4f}. "
                f"Weights: {weights}"
            )

    def get_weights(self):
        """
        Get the current weights being used for scoring.

        Returns:
            dict: Current weights for each metric.
        """
        return self._weights.copy()

    def missing_score(self):
        """
        Compute the quality score based on missing value percentages.

        Returns:
            float: Score between 0 and 100 (higher = better quality).
        """
        missing = self._eda.get('missing', {})
        pct = [v['pct'] for v in missing.values()] if missing else [0]
        self.scores['missing'] = max(0, 100 - np.mean(pct))
        return self.scores['missing']

    def duplicates_score(self):
        """
        Compute the quality score based on duplicate rows.

        Returns:
            float: Score between 0 and 100 (higher = better).
        """
        dups = self._eda.get('duplicates', 0)
        pct = (dups / max(1, self._df_len)) * 100
        self.scores['duplicates'] = max(0, 100 - pct * 2)
        return self.scores['duplicates']

    def outliers_score(self):
        """
        Compute the quality score based on number of detected outliers.

        Returns:
            float: Score between 0 and 100 (higher = better).
        """
        out = self._eda.get('outliers', {})
        total = sum(out.values()) if out else 0
        pct = (total / max(1, self._df_len)) * 100
        self.scores['outliers'] = max(0, 100 - pct * 1.5)
        return self.scores['outliers']

    def balance_score(self):
        """
        Placeholder scoring for dataset balance.

        Returns:
            float: Score representing balance (currently fixed at 90.0).
        """
        self.scores['balance'] = 90.0
        return self.scores['balance']

    def overall_score(self):
        """
        Compute a weighted overall data quality score using configured weights.

        Default weights:
            - Missing score (35%)
            - Duplicate score (15%)
            - Outlier score (25%)
            - Balance score (25%)

        Ensures all component metrics are computed before combining.

        Returns:
            float: Final weighted quality score between 0 and 100.
        """
        # Ensure all individual scores are computed
        for metric in ['missing', 'duplicates', 'outliers', 'balance']:
            if metric not in self.scores:
                getattr(self, f"{metric}_score")()

        # Compute weighted overall score
        self.scores['overall'] = sum(
            self.scores[m] * self._weights[m] 
            for m in self._weights.keys()
        )
        return self.scores['overall']
