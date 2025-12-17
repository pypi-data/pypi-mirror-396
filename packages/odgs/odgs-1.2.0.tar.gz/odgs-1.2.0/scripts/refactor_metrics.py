import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_FILE = os.path.join(PROJECT_ROOT, 'standard_metrics.json')

def refactor_metrics():
    with open(METRICS_FILE, 'r') as f:
        metrics = json.load(f)

    for metric in metrics:
        current_logic = metric.get('calculation_logic')
        
        # Check if already refactored (is a dict)
        if isinstance(current_logic, dict):
            continue
            
        # Create structured logic
        structured_logic = {
            "abstract": current_logic,
            "sql_standard": f"/* TODO: Implement SQL for {metric['name']} */",
            "dax_pattern": f"/* TODO: Implement DAX for {metric['name']} */"
        }
        
        metric['calculation_logic'] = structured_logic

    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Refactored {len(metrics)} metrics to structured calculation_logic.")

if __name__ == "__main__":
    refactor_metrics()
