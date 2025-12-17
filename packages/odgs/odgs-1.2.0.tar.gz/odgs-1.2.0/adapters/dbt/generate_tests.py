import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MACROS_DIR = os.path.join(PROJECT_ROOT, 'adapters', 'dbt', 'macros')
RULES_FILE = os.path.join(PROJECT_ROOT, 'standard_data_rules.json')

def generate_tests():
    if not os.path.exists(MACROS_DIR):
        os.makedirs(MACROS_DIR)
        
    with open(RULES_FILE, 'r') as f:
        rules = json.load(f)
        
    output_file = os.path.join(MACROS_DIR, 'odgs_tests.sql')
    
    with open(output_file, 'w') as f:
        f.write("-- Auto-generated dbt tests from ODGS Standard Data Rules\n")
        f.write("-- These tests provide a scaffold for implementing governance rules.\n\n")
        
        for rule in rules:
            rule_id = rule['rule_id']
            name = rule['name']
            logic = rule['calculation_logic']
            
            test_name = f"test_odgs_rule_{rule_id}"
            
            f.write(f"{{% test {test_name}(model, column_name) %}}\n")
            f.write(f"    -- Rule: {name}\n")
            f.write(f"    -- Logic: {logic}\n")
            f.write(f"    -- Domain: {rule['domain']}\n")
            f.write("\n")
            f.write("    -- TODO: Implement specific validation logic here.\n")
            f.write("    -- Example: select * from {{ model }} where {{ column_name }} is null\n")
            f.write("    -- For now, this test passes by returning 0 rows.\n")
            f.write("    select * from {{ model }} where 1=0\n")
            f.write("\n")
            f.write("{% endtest %}\n\n")
            
    print(f"✅ Generated {len(rules)} dbt generic tests in {output_file}")

if __name__ == "__main__":
    generate_tests()
