# ODGS Technical Documentation

Welcome to the technical documentation for the Open Data Governance Schema (ODGS).

## Overview
ODGS is a vendor-neutral protocol for defining business logic, data quality rules, and metric definitions in a machine-readable format (JSON). It decouples the "what" (definition) from the "how" (execution), allowing for a single source of truth that can be compiled into various downstream tools (SQL, LookML, DAX, etc.).

## Core Components
The protocol consists of several interconnected JSON schemas:

- **Metrics**: Standardized definitions of KPIs.
- **Data Rules**: technical validation rules for data quality.
- **DQ Dimensions**: The qualitative dimensions of data quality.
- **Root Cause Factors**: A taxonomy for diagnosing data issues.
- **Business Process Maps**: Mapping data to business workflows.
- **Physical Data Map**: linking abstract metrics to physical tables.
- **Ontology Graph**: Defining relationships between business entities.

## Navigation
- [Architecture](./architecture.md): High-level system design.
- [Graph Model](./graph_model.md): Understanding the interconnected nodes.
- [Domain Suggestions](./domain_suggestions.md): Potential domain names for the project.
