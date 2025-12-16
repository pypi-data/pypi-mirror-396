# Dunder methods + encapsulation
# src/loader.py
"""
DataLoader module for loading CSV files into pandas DataFrames.

This module defines the DataLoader class, which handles:
- Reading CSV files into a pandas DataFrame.
- Accessing the loaded DataFrame.
- Comparing DataLoader instances.
- Getting basic metadata about the DataFrame.
"""

import pandas as pd

class DataLoader:
    """
    Class to load CSV files into a pandas DataFrame and provide metadata.

    Attributes:
        _path (str): Path to the CSV file.
        _df (pd.DataFrame): Loaded DataFrame (protected).

    """

    def __init__(self, path):
        """Initialize the DataLoader with a CSV file path."""
        self._path = path
        self._df = None

    def load(self, nrows=None):
        """
        Load a CSV file into a pandas DataFrame.

        Args:
            nrows (int, optional): Limit the number of rows to read. Defaults to None (read all).

        Returns:
            pd.DataFrame: Loaded DataFrame.
        """
        self._df = pd.read_csv(self._path, nrows=nrows)
        return self._df

    def get_df(self):
        """Return the loaded DataFrame."""
        return self._df

    # Dunder Methods
    def __repr__(self):
        """
        String representation of the DataLoader object.

        Returns:
            str: Information about the DataLoader, including file path and row count.
        """
        rows = len(self._df) if self._df is not None else 0
        return f"<DataLoader path='{self._path}' rows={rows}>"

    def __eq__(self, other):
        """
        Compare DataLoader instances by the shape of their DataFrames.

        Args:
            other (DataLoader): Another DataLoader instance.

        Returns:
            bool: True if both DataFrames have the same shape, otherwise False.
        """
        if isinstance(other, DataLoader):
            return self._df.shape == other._df.shape
        return False

    def __len__(self):
        """
        Return the number of columns in the loaded DataFrame.

        Returns:
            int: Number of columns, or 0 if the DataFrame is not loaded.
        """
        return len(self._df.columns) if self._df is not None else 0
