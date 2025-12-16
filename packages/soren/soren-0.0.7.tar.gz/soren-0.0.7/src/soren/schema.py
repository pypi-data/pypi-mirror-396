# -----------------------------------------------------------------------------
# JSON Schemas (registry list; one entry per schema)
# -----------------------------------------------------------------------------

JSON_SCHEMAS = [
    {
        "id": "backtest_metrics.v1",
        "schema": {
            "type": "object",
            "properties": {
                "total": {"type": "integer"},
                "true_positives": {"type": "integer"},
                "false_positives": {"type": "integer"},
                "true_negatives": {"type": "integer"},
                "false_negatives": {"type": "integer"},
                "precision": {"type": "number"},
                "recall": {"type": "number"},
                "f1": {"type": "number"},
                "accuracy": {"type": "number"}
            },
            "required": [
                "total", "true_positives", "false_positives",
                "true_negatives", "false_negatives",
                "precision", "recall", "f1", "accuracy"
            ],
            "additionalProperties": False
        },
    },
    {
        "id": "backtest_results.v1",
        "schema": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "row_id": {"type": "string"},
                    "label": {"type": "boolean"},
                    "prediction": {"type": "boolean"},
                    "reasoning": {"type": "string"},
                    "correct": {"type": "boolean"},
                },
                "required": ["row_id", "label", "prediction", "reasoning", "correct"],
                "additionalProperties": False
            }
        },
    },
    {
        "id": "citation_resolution_metrics.v1",
        # Accept arbitrary UUID-like keys, each with the required fields
        "schema": {
            "type": "object",
            "patternProperties": {
                "^[\\w-]+$": {
                    "type": "object",
                    "properties": {
                        "resolved": {"type": "boolean"},
                        "mimetype": {"type": "string"},
                        "quote": {"type": "string"},
                        "file_name": {"type": "string"}
                    },
                    "required": ["resolved", "mimetype", "quote", "file_name"],
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        },
    },
]


# -----------------------------------------------------------------------------
# CSV Schemas (header-based registry)
# -----------------------------------------------------------------------------

CSV_SCHEMAS = [
    {
        "id": "analyze_effectiveness_csv.v1",
        "required_headers": {"tests", "test_results", "detailed_test_results", "test_results_summary", "related_files"},
    },
    {
        "id": "generic_csv.v1",
        "required_headers": set(),
    },
]