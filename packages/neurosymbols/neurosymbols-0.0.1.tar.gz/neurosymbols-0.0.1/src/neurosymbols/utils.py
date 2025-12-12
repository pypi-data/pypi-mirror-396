"""Utility functions for schema conversion and model handling."""

from pydantic import BaseModel

from neurosymbols.schema import FieldDefinition, SchemaDefinition


def pydantic_model_to_schema_definition(model: type[BaseModel]) -> SchemaDefinition:
    """
    Convert a Pydantic model to a SchemaDefinition.

    Args:
        model: Pydantic model class

    Returns:
        SchemaDefinition representing the Pydantic model
    """
    fields = []
    schema = model.model_json_schema()

    for field_name, field_info in schema.get("properties", {}).items():
        # Get Python type from JSON schema type
        json_type = field_info.get("type", "string")
        type_map = {
            "integer": "int",
            "number": "float",
            "string": "str",
            "boolean": "bool",
        }
        type_name = type_map.get(json_type, "str")

        # Get description from field info
        description = field_info.get("description", f"{field_name} field")

        fields.append(
            FieldDefinition(
                name=field_name,
                type_name=type_name,  # type: ignore[arg-type]
                description=description,
            )
        )

    return SchemaDefinition(
        model_name=model.__name__,
        fields=fields,
    )
