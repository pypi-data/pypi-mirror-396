# Schema & Logic Enhancements

To make ODGS a true enterprise "Game Changer" and align with the "System of Record" vision, consider these enhancements:

## 1. Lifecycle Management
- **Status Field**: Add `status` (Draft, Review, Active, Deprecated) to every metric. This allows for governance workflows (e.g., "Draft" metrics don't get compiled to Power BI).
- **Versioning**: Add `version` (e.g., 1.0, 1.1) to track changes to definitions over time.
- **Timestamps**: `created_at` and `updated_at`.

## 2. Dependency Graph (Lineage)
- **Inputs Field**: Explicitly list the valid `metric_ids` or `column_ids` that input into a calculation. This allows the graph to be built *deterministically* rather than inferred.
- **Upstream/Downstream**: Allow metrics to reference other metrics (e.g., `Net Profit Link` references `Revenue` and `Cost`).

## 3. Compliance & Sensitivity
- **GDPR Tags**: `is_pii: boolean`.
- **Classification**: `sensitivity_level` (Public, Internal, Confidential, Restricted).
- **EU AI Act**: `risk_category` (Minimal, High, Unacceptable).

## 4. Testing & Validation
- **Sample Data**: Include `test_cases` in the JSON (Input A, Input B -> Expected Result) to verify the logic automatically in Python/Unit Tests.
- **Thresholds**: `alert_threshold_low` and `alert_threshold_high` for monitoring.

## 5. UI/UX Enhancements
- **Color Hex**: Allow defining a standard color for the metric (e.g., "Revenue" is always #00FF00).
- **Format String**: `display_format` (e.g., "$#,##0.00", "0%").
