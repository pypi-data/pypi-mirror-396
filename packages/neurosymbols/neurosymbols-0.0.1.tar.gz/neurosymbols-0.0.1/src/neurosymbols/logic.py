"""Prolog rule induction models for logic induction."""

from pydantic import BaseModel, Field


class PrologRuleSpec(BaseModel):
    """Specification for a Prolog rule generated from structured data."""

    rationale: str = Field(..., description="Explanation of why this rule separates valid from invalid examples")
    prolog_code: str = Field(
        ...,
        description="Prolog rule code. Rule head: valid(X). Variables start with uppercase, atoms with lowercase.",
    )
