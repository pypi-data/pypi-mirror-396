# Composition + narrative
class Narrator:
    """
    Generates natural-language explanations and summaries of EDA results
    and computed data-quality scores.

    This class converts numerical metrics into readable text paragraphs
    that describe the dataset's statistical properties, missing values,
    outliers, and overall quality verdict.

    Parameters
    ----------
    eda_results : dict
        Dictionary containing EDA outputs such as summary statistics,
        missing value counts, and outlier detections.
    scores : dict
        Dictionary of computed quality scores, including the overall score.
    """

    def __init__(self, eda_results, scores):
        self._eda = eda_results
        self._scores = scores

    def generate(self):
        """
        Generate a list of narrative statements describing the dataset.

        Returns
        -------
        list of str
            A list of human-readable sentences summarising:
            - basic statistics (mean, std)
            - missing value counts and percentages
            - outlier counts
            - overall data-quality rating based on final score
        """
        text = []

        # Summary statistics
        for col, metrics in self._eda.get('summary', {}).items():
            if isinstance(metrics, dict) and 'mean' in metrics and 'std' in metrics:
                text.append(
                    f"Column '{col}' has mean {metrics['mean']:.2f} "
                    f"and standard deviation {metrics['std']:.2f}."
                )

        # Missing values
        for col, info in self._eda.get('missing', {}).items():
            if info['missing'] > 0:
                text.append(
                    f"Column '{col}' has {info['missing']} missing values "
                    f"({info['pct']}%)."
                )

        # Outliers
        for col, n in self._eda.get('outliers', {}).items():
            if n > 0:
                text.append(f"Column '{col}' contains {n} detected outliers.")

        # Overall score + verbal rating
        overall = self._scores.get('overall', 0)
        verdict = (
            "Excellent" if overall >= 90
            else "Good" if overall >= 75
            else "Fair" if overall >= 50
            else "Poor"
        )

        text.append(
            f"Overall data quality: {overall:.2f}/100 - {verdict}."
        )

        return text
