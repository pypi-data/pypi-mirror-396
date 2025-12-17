import json
import os
import csv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEEDS_DIR = os.path.join(PROJECT_ROOT, 'adapters', 'dbt', 'seeds')

FILES_TO_PROCESS = [
    {
        "filename": "standard_dq_dimensions.json",
        "output_name": "odgs_dq_dimensions.csv",
        "headers": ["id", "name", "category", "definition", "unitOfMeasure"]
    },
    {
        "filename": "root_cause_factors.json",
        "output_name": "odgs_root_cause_factors.csv",
        "headers": ["factorId", "factorName", "description"]
    },
    {
        "filename": "business_process_maps.json",
        "output_name": "odgs_business_processes.csv",
        "headers": ["lifecycleId", "lifecycleName", "description"]
    }
]

def generate_seeds():
    if not os.path.exists(SEEDS_DIR):
        os.makedirs(SEEDS_DIR)

    for item in FILES_TO_PROCESS:
        input_path = os.path.join(PROJECT_ROOT, item["filename"])
        output_path = os.path.join(SEEDS_DIR, item["output_name"])
        
        with open(input_path, 'r') as f:
            data = json.load(f)
            
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=item["headers"], extrasaction='ignore')
            writer.writeheader()
            
            # Flatten data if necessary or just write rows
            # For business processes, we might want to flatten stages, but for now let's keep it simple: top level
            # Actually, for business processes, let's just write the top level lifecycles
            
            for row in data:
                writer.writerow(row)
                
        print(f"✅ Generated seed {item['output_name']} with {len(data)} rows.")

if __name__ == "__main__":
    generate_seeds()
