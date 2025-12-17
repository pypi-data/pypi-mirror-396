import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METRICS_FILE = os.path.join(PROJECT_ROOT, 'standard_metrics.json')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'adapters', 'dbt', 'semantic_models.yml')

def generate_dbt_semantic_models():
    with open(METRICS_FILE, 'r') as f:
        metrics = json.load(f)

    with open(OUTPUT_FILE, 'w') as f:
        f.write("version: 2\n")
        f.write("metrics:\n")
        
        for m in metrics:
            name = m['name'].lower().replace(" ", "_").replace("(", "").replace(")", "")
            description = m.get('definition', '').replace('"', '\\"')
            sql_expr = m['calculation_logic'].get('sql_standard', 'TODO_SQL')
            
            f.write(f"  - name: {name}\n")
            f.write(f"    description: \"{description}\"\n")
            f.write("    type: simple\n")
            f.write("    type_params:\n")
            f.write("      measure:\n")
            f.write(f"        name: {name}_measure\n")
            f.write(f"        expr: \"{sql_expr}\"\n")
            f.write("    meta:\n")
            f.write(f"      odgs_id: \"{m['metric_id']}\"\n")
            f.write(f"      owner: \"{m['owner']}\"\n")
            f.write(f"      domain: \"{m['domain']}\"\n")
            f.write("\n")
        
    print(f"✅ Generated dbt MetricFlow configuration for {len(metrics)} metrics at {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_dbt_semantic_models()
