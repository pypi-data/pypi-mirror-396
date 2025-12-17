# System Architecture

## Overview
The ODGS architecture is designed to be "Headless," meaning the governance logic exists independently of the consumption layer.

## High-Level Design

```mermaid
graph TD
    subgraph "The Protocol (Source of Truth)"
        A[standard_metrics.json] 
        B[standard_data_rules.json]
        C[business_process_maps.json]
        D[root_cause_factors.json]
        E[ontology_graph.json]
        F[physical_data_map.json]
    end

    subgraph "The Compiler (CLI & SDK)"
        G[odgs CLI / Python SDK]
        H[NPM Package]
    end

    subgraph "The Consumption Layer (Downstream)"
        I[Data Warehouse (Snowflake/BigQuery)]
        J[BI Tools (Power BI / Tableau)]
        K[AI Agents (LLM Context)]
        L[Data Catalog]
    end

    A & B & C & D & E & F --> G
    A & B & C & D & E & F --> H

    G -->|Compiles to SQL| I
    G -->|Compiles to TMSL/TDS| J
    G -->|Compiles to Context| K
    G -->|Compiles to Metadata| L
```

## Component Interaction

1.  **JSON Source**: The engineer or data steward defines the logic in the JSON files.
2.  **CLI / SDK**: The `odgs` tool reads these files, validates them against the schema, and builds the necessary artifacts.
3.  **Deploy**: The artifacts (SQL views, TMSL files, etc.) are deployed to their respective platforms via CI/CD.
