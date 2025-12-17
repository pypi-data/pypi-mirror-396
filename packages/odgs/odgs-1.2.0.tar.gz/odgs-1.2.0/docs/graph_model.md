# The ODGS Graph Model

## interconnected Nodes
While ODGS is stored as flat JSON files, it logically represents a **Knowledge Graph**. Each file represents a type of node, and the references between them (e.g., `metric_id` linking to `rule_id`) form the edges.

This structure allows for powerful queries like: *"Show me all metrics affected by a failure in the 'Order-to-Cash' process."*

## The Schema Graph

```mermaid
erDiagram
    METRIC ||--o{ DATA_RULE : "validated_by"
    METRIC }|--|| BUSINESS_PROCESS : "belongs_to"
    METRIC }|--|| PHYSICAL_COLUMN : "maps_to"
    DATA_RULE }|--|| DQ_DIMENSION : "classified_as"
    DATA_RULE }|--o{ ROOT_CAUSE : "diagnosed_by"
    BUSINESS_PROCESS ||--o| BUSINESS_PROCESS : "child_of"
    ONTOLOGY_NODE ||--o{ ONTOLOGY_EDGE : "relates_to"
    ONTOLOGY_NODE ||--|| METRIC : "is_defined_by"

    METRIC {
        string metric_id PK
        string name
        string calculation_logic
    }

    DATA_RULE {
        string rule_id PK
        string regex_pattern
        string threshold
    }

    BUSINESS_PROCESS {
        string process_id PK
        string process_name
    }

    ROOT_CAUSE {
        string factor_id PK
        string description
    }
```

## Why a Graph?
By treating governance as a graph, we enable:

1.  **Impact Analysis**: If `Order_ID` changes format, we traverse the graph to find every dependent Metric and Dashboard.
2.  **Root Cause Analysis**: If `Gross_Margin` drops, we traverse the graph to see which underlying Data Rules failed and which Business Process is responsible.
3.  **AI Context**: We can feed the LLM a subgraph relevant to the user's question, rather than the entire database schema.
