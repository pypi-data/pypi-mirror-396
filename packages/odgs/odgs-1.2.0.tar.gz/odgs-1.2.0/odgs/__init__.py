import json
import os

# Helper to load JSON files from the package
def _load_json(filename):
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filename)
    with open(file_path, 'r') as f:
        return json.load(f)

# Load schemas
standard_metrics = _load_json("standard_metrics.json")
standard_dq_dimensions = _load_json("standard_dq_dimensions.json")
standard_data_rules = _load_json("standard_data_rules.json")
root_cause_factors = _load_json("root_cause_factors.json")
business_process_maps = _load_json("business_process_maps.json")
