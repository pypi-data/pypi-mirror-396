"""Data extraction module for converting text to structured data."""

import json
from typing import Any

import dspy
from pydantic import BaseModel

from neurosymbols.schema import SchemaDefinition
from neurosymbols.utils import pydantic_model_to_schema_definition


class ExtractData(dspy.Signature):
    """
    Extract structured information from text based on provided field definitions.

    Return a JSON dictionary matching the schema with correct types.
    """

    text_input = dspy.InputField(desc="Raw text input to extract data from")
    fields_to_extract = dspy.InputField(
        desc="List of fields and types to find in the text"
    )
    extracted_data = dspy.OutputField(
        desc='Valid JSON object mapping field names to extracted values. Return only JSON, no markdown. Example: {"field_name": "value", "number_field": 123}'
    )


def extract_data(
    text: str,
    schema_def: SchemaDefinition | type[BaseModel],
    lm: dspy.LM,
) -> dict[str, Any]:
    """
    Extract structured data from text using the discovered schema or Pydantic model.

    Args:
        text: Raw text input
        schema_def: Schema definition or Pydantic model class to use for extraction
        lm: DSPy language model instance

    Returns:
        Dictionary mapping field names to extracted values
    """
    # Convert Pydantic model to SchemaDefinition if needed
    if isinstance(schema_def, type) and issubclass(schema_def, BaseModel):
        schema_def = pydantic_model_to_schema_definition(schema_def)

    predictor = dspy.Predict(ExtractData)
    field_desc = str([f"{f.name} ({f.type_name})" for f in schema_def.fields])
    result = predictor(text_input=text, fields_to_extract=field_desc)

    # Parse JSON output
    try:
        return json.loads(result.extracted_data)
    except (json.JSONDecodeError, TypeError):
        # If it's already a dict, return it
        if isinstance(result.extracted_data, dict):
            return result.extracted_data
        # Try to extract JSON from markdown code blocks
        data_str = str(result.extracted_data)
        if "```json" in data_str:
            data_str = data_str.split("```json")[1].split("```")[0].strip()
        elif "```" in data_str:
            data_str = data_str.split("```")[1].split("```")[0].strip()
        return json.loads(data_str)
