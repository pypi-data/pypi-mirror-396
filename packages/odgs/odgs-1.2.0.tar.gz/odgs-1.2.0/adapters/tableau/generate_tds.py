import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METRICS_FILE = os.path.join(PROJECT_ROOT, 'standard_metrics.json')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'adapters', 'tableau', 'metrics.tds')

REFERENCE_FILES = [
    {"path": "standard_dq_dimensions.json", "name": "DQ_Dimensions"},
    {"path": "root_cause_factors.json", "name": "Root_Cause_Factors"},
    {"path": "business_process_maps.json", "name": "Business_Processes"}
]

def generate_tableau_tds():
    with open(METRICS_FILE, 'r') as f:
        metrics = json.load(f)

    root = ET.Element("datasource", formatted_name='federated.odgs', inline='true')
    
    # Connection (Dummy for now)
    connection = ET.SubElement(root, "connection", class_='federated')
    named_connections = ET.SubElement(connection, "named-connections")
    named_connection = ET.SubElement(named_connections, "named-connection", caption='ODGS_Source', name='federated.odgs')
    ET.SubElement(named_connection, "connection", class_='textscan') # Simulating text/CSV source

    # Metadata Records (Simulating columns from a source)
    # 1. Metrics Table (Virtual)
    for m in metrics:
        # In Tableau, metrics are often calculated fields.
        # We'll create them as calculated-members later.
        pass

    # 2. Reference Tables Metadata
    # We'll add metadata records to simulate these tables existing in the source
    for ref in REFERENCE_FILES:
        file_path = os.path.join(PROJECT_ROOT, ref["path"])
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if data:
                columns = list(data[0].keys())
                simple_columns = [c for c in columns if isinstance(data[0][c], (str, int, float, bool, type(None)))]
                
                # In a real TDS, these would be under <metadata-records> mapping to the physical source
                # For this "headless" adapter, we'll just ensure the XML structure allows for it.
                # But the most important part for Tableau is the Calculated Fields (Metrics).
                pass

    # Calculated Fields (The Core Metrics)
    for m in metrics:
        calc_field = ET.SubElement(root, "column", 
                                   caption=m['name'], 
                                   datatype='real', 
                                   name=f"[{m['name']}]", 
                                   role='measure', 
                                   type='quantitative')
        
        # Formula
        formula = ET.SubElement(calc_field, "calculation", class_='tableau', formula=m['calculation_logic'].get('sql_standard', '1'))

        # Description
        desc = ET.SubElement(calc_field, "desc")
        formatted_text = ET.SubElement(desc, "formatted-text")
        run = ET.SubElement(formatted_text, "run")
        run.text = m.get('definition', '')

    # Add Reference Data as "Folders" or logical groupings if possible, 
    # but without physical data connection, Tableau won't show "tables".
    # So we will create Folders to organize the Metrics, and maybe placeholder columns for Dimensions.
    
    # Create Folders for Domains
    domains = set(m['domain'] for m in metrics)
    folders_element = ET.SubElement(root, "folders-common")
    
    for domain in domains:
        folder = ET.SubElement(folders_element, "folder", name=domain)
        # Add metrics to this folder
        for m in metrics:
            if m['domain'] == domain:
                ET.SubElement(folder, "folder-item", name=f"[{m['name']}]", type='field')

    # Save
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(OUTPUT_FILE, "w") as f:
        f.write(xmlstr)

    print(f"✅ Generated Tableau TDS configuration for {len(metrics)} metrics at {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_tableau_tds()
