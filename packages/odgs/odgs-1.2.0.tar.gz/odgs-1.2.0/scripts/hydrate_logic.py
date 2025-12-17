import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_FILE = os.path.join(PROJECT_ROOT, 'standard_metrics.json')

def to_snake_case(text):
    return text.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")

def to_title_case(text):
    # Simple title case, keeping existing casing for acronyms if possible or just capitalizing words
    return text.title()

def hydrate_logic():
    with open(METRICS_FILE, 'r') as f:
        metrics = json.load(f)

    hydrated_count = 0
    
    for m in metrics:
        logic = m.get('calculation_logic', {})
        if not isinstance(logic, dict):
            continue
            
        abstract = logic.get('abstract', '')
        if not abstract:
            continue

        # Heuristics for SQL and DAX generation
        # This is a basic parser/replacer. Real-world would need a full parser.
        
        # Tokenize by operators
        tokens = re.split(r'(\s*[\+\-\*\/]\s*|\s*[\(\)]\s*)', abstract)
        
        sql_parts = []
        dax_parts = []
        
        for token in tokens:
            stripped = token.strip()
            if not stripped:
                continue
                
            if stripped in ['+', '-', '*', '/', '(', ')']:
                sql_parts.append(stripped)
                dax_parts.append(stripped)
            elif re.match(r'^\d+(\.\d+)?$', stripped): # Number
                sql_parts.append(stripped)
                dax_parts.append(stripped)
            else: # Variable/Measure
                # SQL: SUM(snake_case)
                sql_parts.append(f"SUM({to_snake_case(stripped)})")
                # DAX: [Title Case]
                dax_parts.append(f"[{stripped}]")
        
        sql_expr = "".join(sql_parts)
        dax_expr = "".join(dax_parts)
        
        # Handle Division (Ratio) specifically for safety
        if '/' in abstract:
            # Very naive division handling, assuming A / B structure
            # For robust handling, we'd need an AST. 
            # For now, let's stick to the simple replacement but wrap the denominator in NULLIF for SQL
            # and use DIVIDE for DAX if it looks like a simple ratio.
            pass 

        # Update if still TODO
        if 'TODO' in logic.get('sql_standard', ''):
            m['calculation_logic']['sql_standard'] = sql_expr
        
        if 'TODO' in logic.get('dax_pattern', ''):
            # Use DIVIDE for DAX if / is present
            if '/' in abstract:
                 # Try to split on the main division operator if possible. 
                 # This is hard with regex without recursion for nested parens.
                 # Fallback to standard operator for now, but user requested DIVIDE.
                 # Let's do a simple check: if it's "A / B", make it DIVIDE(A, B)
                 parts = abstract.split('/')
                 if len(parts) == 2:
                     num = parts[0].strip().strip('()')
                     den = parts[1].strip().strip('()')
                     dax_expr = f"DIVIDE([{num}], [{den}])"
            
            m['calculation_logic']['dax_pattern'] = dax_expr

        hydrated_count += 1

    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Hydrated logic for {hydrated_count} metrics.")

if __name__ == "__main__":
    hydrate_logic()
