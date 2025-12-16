# Composition + dunder method
# src/orchestrator.py
from loader import DataLoader
from preprocessor import Preprocessor
from eda_analyzer import NumericAnalyzer, CategoricalAnalyzer
from quality_scorer import QualityScorer
from narrator import Narrator
from report_builder import ReportBuilder

class DatasetPipeline:
    """
    Main orchestrator class for the automated EDA pipeline.

    This class coordinates the entire process: data loading, preprocessing,
    numeric and categorical analysis, quality scoring, narrative generation, 
    and Markdown report building.

    Attributes:
        loader (DataLoader): Handles loading CSV files.
        preprocessor (Preprocessor): Preprocesses the DataFrame (trimming strings, parsing dates).
        analyzer (EDAAnalyzer): Performs numeric and categorical analysis.
        eda_results (dict): Stores combined results of EDA analyses.
        scores (dict): Stores calculated quality scores.
        narrative (list): Stores generated narrative insights.
        report (str): Final Markdown report string.
        custom_weights (dict): Custom weights for quality scoring (optional).
    """

    def __init__(self, path, custom_weights=None):
        """
        Initialize DatasetPipeline with path to CSV data.

        Args:
            path (str): Path to the CSV file to analyze.
            custom_weights (dict, optional): Custom weights for quality scoring.
                Must contain keys: 'missing', 'duplicates', 'outliers', 'balance'.
                Values must sum to 1.0. Defaults to None (uses default weights).
        """
        self.loader = DataLoader(path)
        self.preprocessor = None
        self.analyzer = None
        self.eda_results = None
        self.scores = None
        self.narrative = None
        self.report = None
        self.custom_weights = custom_weights

    def run(self):
        """
        Execute the full data pipeline: load, preprocess, analyze, score, narrate, and build report.

        Returns:
            str: The final Markdown report generated from the analysis.
        """
        # Load data
        df = self.loader.load()

        # Preprocess
        self.preprocessor = Preprocessor(df).trim_strings(
            df.select_dtypes(include='object').columns.tolist()
        )
        df_clean = self.preprocessor.get_df()

        # Numeric and categorical analysis
        num_analyzer = NumericAnalyzer(df_clean)
        cat_analyzer = CategoricalAnalyzer(df_clean)
        
        # Get results from both analyzers
        num_results = num_analyzer.run_all()
        cat_results = cat_analyzer.run_all()
        
        # Merge results properly - combine missing values from both
        self.eda_results = {
            'summary': {**num_results.get('summary', {}), **cat_results.get('summary', {})},
            'missing': {**num_results.get('missing', {}), **cat_results.get('missing', {})},
            'outliers': num_results.get('outliers', {}),
            'duplicates': num_results.get('duplicates', 0)
        }

        # Data quality scoring with custom weights if provided
        scorer = QualityScorer(
            self.eda_results, 
            df_len=len(df_clean),
            custom_weights=self.custom_weights
        )
        scorer.overall_score()
        self.scores = scorer.scores

        # Generate narrative
        narrator = Narrator(self.eda_results, self.scores)
        self.narrative = narrator.generate()

        # Build Markdown report (pass weights info)
        builder = ReportBuilder(
            self.narrative, 
            self.scores, 
            self.eda_results,
            weights=scorer.get_weights()
        )
        self.report = builder.to_markdown()
        return self.report

    def __repr__(self):
        """
        String representation of the DatasetPipeline object.

        Returns:
            str: Representation including the loader information.
        """
        return f"<DatasetPipeline loader={repr(self.loader)}>"
