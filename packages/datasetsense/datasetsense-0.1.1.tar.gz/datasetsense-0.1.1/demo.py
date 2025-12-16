# demo.py

# Import your DatasetPipeline from src
from src.orchestrator import DatasetPipeline

# Initialize pipeline with a sample CSV
pipeline = DatasetPipeline("data/sample.csv")

# Run full analysis
report = pipeline.run()

# Print the report
print(report)

