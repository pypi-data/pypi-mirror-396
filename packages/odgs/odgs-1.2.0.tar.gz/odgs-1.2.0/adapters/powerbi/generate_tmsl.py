import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METRICS_FILE = os.path.join(PROJECT_ROOT, 'standard_metrics.json')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'adapters', 'powerbi', 'measures.tmsl.json')

REFERENCE_FILES = [
    {"path": "standard_dq_dimensions.json", "name": "DQ_Dimensions"},
    {"path": "root_cause_factors.json", "name": "Root_Cause_Factors"},
    {"path": "business_process_maps.json", "name": "Business_Processes"}
]

def generate_powerbi_tmsl():
    # 1. Generate Measures from Metrics
    with open(METRICS_FILE, 'r') as f:
        metrics = json.load(f)

    tmsl_measures = []
    
    for m in metrics:
        measure_def = {
            "name": m['name'],
            "expression": m['calculation_logic'].get('dax_pattern', '/* TODO_DAX */'),
            "description": m.get('definition', ''),
            "formatString": "#,0.00", # Default format
            "annotations": [
                {
                    "name": "ODGS_ID",
                    "value": m['metric_id']
                },
                {
                    "name": "Owner",
                    "value": m['owner']
                }
            ]
        }
        tmsl_measures.append(measure_def)

    # 2. Generate Reference Tables
    tables = []
    
    # Main Metrics Table (Virtual table to hold measures)
    tables.append({
        "name": "ODGS_Metrics",
        "columns": [{"name": "Dummy", "dataType": "string"}],
        "partitions": [{
            "name": "ODGS_Metrics_Partition",
            "mode": "import",
            "source": {
                "type": "m",
                "expression": "let\n    Source = #table(type table [Dummy = text], {{ \"Metrics Container\" }})\nin\n    Source"
            }
        }],
        "measures": tmsl_measures
    })

    # Reference Data Tables
    for ref in REFERENCE_FILES:
        file_path = os.path.join(PROJECT_ROOT, ref["path"])
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Create M expression to embed data
            # We'll take the first row keys as columns
            if data:
                columns = list(data[0].keys())
                # Filter out complex objects for simplicity in this adapter
                simple_columns = [c for c in columns if isinstance(data[0][c], (str, int, float, bool, type(None)))]
                
                m_columns = ", ".join([f'"{c}"' for c in simple_columns])
                m_rows = []
                for row in data:
                    vals = []
                    for c in simple_columns:
                        val = row.get(c)
                        if isinstance(val, str):
                            escaped_val = val.replace('"', '""')
                            vals.append(f'"{escaped_val}"')
                        elif val is None:
                            vals.append("null")
                        else:
                            vals.append(str(val))
                    m_rows.append(f"{{{', '.join(vals)}}}")
                
                m_expression = f"""let
    Source = #table(
        type table [{', '.join([f'{c} = any' for c in simple_columns])}],
        {{
            {', '.join(m_rows)}
        }}
    )
in
    Source"""

                tables.append({
                    "name": ref["name"],
                    "columns": [{"name": c, "dataType": "string"} for c in simple_columns], # defaulting to string for simplicity
                    "partitions": [{
                        "name": f"{ref['name']}_Partition",
                        "mode": "import",
                        "source": {
                            "type": "m",
                            "expression": m_expression
                        }
                    }]
                })

    tmsl_model = {
        "createOrReplace": {
            "object": {
                "database": "ODGS_Governance_Layer",
                "compatibilityLevel": 1500
            },
            "database": {
                "name": "ODGS_Governance_Layer",
                "model": {
                    "culture": "en-US",
                    "tables": tables
                }
            }
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(tmsl_model, f, indent=2)
        
    print(f"✅ Generated Power BI TMSL configuration for {len(tmsl_measures)} measures and {len(tables)-1} reference tables at {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_powerbi_tmsl()
