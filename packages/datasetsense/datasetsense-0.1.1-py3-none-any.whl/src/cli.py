# simple command line entry
"""
Command-line interface (CLI) for running the Automated EDA Narrator pipeline.

This script allows users to execute the DatasetPipeline on a CSV file from the terminal.
It generates a Markdown report containing:
- Narrative insights from the dataset
- Data quality scores
- Summary statistics

Usage:
    python src/cli.py <csv_path> [--out <output_file>] [--weights <json_string>]

Example:
    python src/cli.py data/sample.csv --out reports/sample_report.md
    python src/cli.py data/sample.csv --weights '{"missing":0.5,"duplicates":0.1,"outliers":0.2,"balance":0.2}'
"""

import argparse
import json
from orchestrator import DatasetPipeline

def main():
    """
    Parse command-line arguments and execute the DatasetPipeline.

    Steps:
    1. Parses the required 'csv' argument and optional arguments.
    2. Optionally parses custom weights from JSON string.
    3. Runs the DatasetPipeline on the given CSV file.
    4. Outputs the Markdown report to a file if '--out' is specified, 
       otherwise prints the report to the terminal.

    Command-line Arguments:
        csv (str): Path to the CSV file to analyze.
        --out (str, optional): Output Markdown file path. Defaults to None.
        --weights (str, optional): JSON string of custom weights. Defaults to None.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(
        description="Run Automated EDA Narrator with optional custom weights"
    )
    parser.add_argument("csv", help="Path to CSV file")
    parser.add_argument("--out", help="Output markdown path", default=None)
    parser.add_argument(
        "--weights", 
        help='Custom weights as JSON string (e.g., \'{"missing":0.5,"duplicates":0.1,"outliers":0.2,"balance":0.2}\')',
        default=None
    )
    args = parser.parse_args()

    # Parse custom weights if provided
    custom_weights = None
    if args.weights:
        try:
            custom_weights = json.loads(args.weights)
            print(f"Using custom weights: {custom_weights}")
        except json.JSONDecodeError as e:
            print(f"Error parsing weights JSON: {e}")
            print("Using default weights instead.")
            custom_weights = None

    # Run pipeline
    try:
        pipeline = DatasetPipeline(args.csv, custom_weights=custom_weights)
        md = pipeline.run()

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"Wrote report to {args.out}")
        else:
            print(md)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
