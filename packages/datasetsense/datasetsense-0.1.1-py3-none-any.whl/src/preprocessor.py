# Encapsulation + getters
# src/preprocessor.py
"""
Preprocessor module for cleaning and transforming pandas DataFrames.

This module provides utilities for:
- Trimming whitespace from string columns
- Parsing date columns safely
- Returning the cleaned DataFrame for further analysis
"""

from dateutil import parser

class Preprocessor:
    """
    A class for preprocessing a pandas DataFrame by cleaning and transforming data.

    Attributes:
        _df (pd.DataFrame): A protected copy of the DataFrame to preprocess.
    """

    def __init__(self, df):
        """
        Initialize the Preprocessor with a DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame to preprocess.
        """
        self._df = df.copy()        # protected

    def trim_strings(self, cols):
        """
        Trim leading and trailing whitespace from specified string columns.

        Args:
            cols (list): List of column names to trim.

        Returns:
            Preprocessor: Returns self to allow method chaining.
        """
        for c in cols:
            if c in self._df:
                self._df[c] = self._df[c].astype(str).str.strip()
        return self

    def parse_dates(self, cols):
        """
        Convert columns to datetime objects.

        Args:
            cols (list): List of column names to convert to datetime.

        Returns:
            Preprocessor: Returns self to allow method chaining.
        """
        for c in cols:
            if c in self._df:
                self._df[c] = self._df[c].apply(
                    lambda x: parser.parse(x) if isinstance(x, str) else x
                )
        return self

    def get_df(self):
        """
        Retrieve the processed DataFrame.

        Returns:
            pd.DataFrame: The cleaned and transformed DataFrame.
        """
        return self._df
