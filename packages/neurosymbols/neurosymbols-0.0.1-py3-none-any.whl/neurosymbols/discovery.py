"""Schema discovery module for structure induction."""

import json

import dspy

from neurosymbols.schema import SchemaDefinition


class DiscoverSchema(dspy.Signature):
    """
    Analyze unstructured text examples to discover a common schema.

    Identify the data points required to evaluate the examples and output
    a schema definition that covers all variables mentioned in the text.
    Output must be valid JSON matching the SchemaDefinition structure:
    {"model_name": "ModelName", "fields": [{"name": "field_name", "type_name": "str|int|float|bool", "description": "..."}]}
    """

    examples = dspy.InputField(desc="List of raw text strings to analyze")
    case_description = dspy.InputField(
        desc="Optional business context and domain knowledge to guide schema discovery"
    )
    generated_schema = dspy.OutputField(
        desc='Valid JSON object with "model_name" (string) and "fields" (array of objects with "name", "type_name", "description"). Return only JSON, no markdown.'
    )


def discover_schema(
    examples: list[str], lm: dspy.LM, case_description: str | None = None
) -> SchemaDefinition:
    """
    Discover a Pydantic schema from unstructured text examples.

    Args:
        examples: List of raw text strings to analyze
        lm: DSPy language model instance
        case_description: Optional business context and domain knowledge to guide schema discovery

    Returns:
        SchemaDefinition containing the discovered schema
    """
    predictor = dspy.Predict(DiscoverSchema)
    result = predictor(
        examples=str(examples),
        case_description=case_description or "No specific business context provided.",
    )

    # Parse JSON output and convert to SchemaDefinition
    try:
        schema_json = json.loads(result.generated_schema)
        return SchemaDefinition(**schema_json)
    except (json.JSONDecodeError, TypeError):
        # If it's already a dict or SchemaDefinition, handle it
        if isinstance(result.generated_schema, dict):
            return SchemaDefinition(**result.generated_schema)
        # Try to extract JSON from markdown code blocks
        schema_str = str(result.generated_schema)
        if "```json" in schema_str:
            schema_str = schema_str.split("```json")[1].split("```")[0].strip()
        elif "```" in schema_str:
            schema_str = schema_str.split("```")[1].split("```")[0].strip()
        return SchemaDefinition(**json.loads(schema_str))
