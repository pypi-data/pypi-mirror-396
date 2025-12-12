"""Schema discovery and definition models for structure induction."""

from typing import Literal

from pydantic import BaseModel, Field


class FieldDefinition(BaseModel):
    """Definition of a single field in the discovered schema."""

    name: str = Field(..., description="Snake_case field name, e.g., 'user_age'")
    type_name: Literal["int", "float", "str", "bool"] = Field(
        ..., description="Python type name for the field"
    )
    description: str = Field(..., description="Human-readable description of the field")


class SchemaDefinition(BaseModel):
    """Complete schema definition discovered from unstructured text."""

    model_name: str = Field(..., description="Name for the Pydantic model (PascalCase)")
    fields: list[FieldDefinition] = Field(
        ..., description="List of fields to extract from text"
    )
