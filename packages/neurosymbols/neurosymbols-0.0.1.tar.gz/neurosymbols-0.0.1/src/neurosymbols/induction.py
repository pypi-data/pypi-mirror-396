"""Prolog rule induction module for logic induction."""

import json
import os
import sys
from typing import Any

import dspy

from neurosymbols.logic import PrologRuleSpec


class InduceLogic(dspy.Signature):
    """
    Induce Prolog rules from structured data examples with validity labels.

    Analyze the patterns that separate valid examples from invalid ones
    and generate a COMPLETE Prolog rule that captures this logic.

    IMPORTANT: Facts are stored as field_name(entity_id, value). For example:
    - If input has {"age": 25, "status": "active"}, facts are:
      age(e1, 25) and status(e1, 'active')
    - The rule head must be: valid(X) where X is the entity variable (e.g., e1)
    - Access fields using: field_name(X, Value) where X is the entity variable
    - Use proper Prolog syntax: valid(X) :- condition1(X), condition2(X).
    - CRITICAL: The rule must be COMPLETE - include ALL conditions needed to
      separate valid from invalid examples
    - The rule must end with a period (.) and be syntactically complete
    - For string comparisons, use member/2: member(Country, ['US', 'Canada'])
    - Avoid complex disjunctions with parentheses - use member/2 or separate conditions
    - Example: valid(X) :- age(X, A), A >= 18, status(X, 'active').
    - Example with member: valid(X) :- country(X, C), member(C, ['US', 'Canada']).

    Output must be valid JSON with 'rationale' and 'prolog_code' fields.
    """

    structured_examples = dspy.InputField(
        desc=(
            "List of dictionaries with 'input' (dict with field:value pairs) "
            "and 'valid' (bool) keys. Facts are stored as field_name(entity_id, value)."
        )
    )
    fact_structure = dspy.InputField(
        desc=(
            "Example of how facts are structured. Format: field_name(entity_id, value). "
            "The rule must use entity_id as the variable (e.g., X). "
            "The rule must check ALL relevant fields to distinguish valid from invalid examples."
        )
    )
    required_fields = dspy.InputField(
        desc=(
            "List of all field names that must be checked in the rule. "
            "The rule should reference all these fields."
        )
    )
    case_description = dspy.InputField(
        desc="Optional business context and domain knowledge to guide rule creation"
    )
    rule = dspy.OutputField(
        desc=(
            'Valid JSON object with "rationale" (string) and "prolog_code" '
            '(COMPLETE Prolog rule string using field_name(X, Value) pattern). '
            'The prolog_code must be a complete, syntactically valid rule '
            'ending with a period. Use member/2 for list membership checks, '
            'avoid complex disjunctions with parentheses. Return only JSON, no markdown. '
            'Example: {"rationale": "...", "prolog_code": "valid(X) :- age(X, A), '
            "A >= 18, status(X, 'active').\"} "
            'Example with member: {"rationale": "...", "prolog_code": "valid(X) :- '
            "country(X, C), member(C, ['US', 'Canada']).\"}"
        )
    )


def _clean_prolog_rule(prolog_code: str) -> str:
    """
    Clean and normalize Prolog rule code.

    Args:
        prolog_code: Raw Prolog rule code

    Returns:
        Cleaned Prolog rule code
    """
    # Remove leading/trailing whitespace
    cleaned = prolog_code.strip()

    # Remove markdown code blocks if present
    if "```prolog" in cleaned:
        cleaned = cleaned.split("```prolog")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    # Remove any JSON escaping
    cleaned = cleaned.replace('\\"', '"').replace("\\'", "'")

    # Check if rule looks incomplete (missing closing parenthesis)
    # Count opening and closing parentheses
    open_parens = cleaned.count("(")
    close_parens = cleaned.count(")")

    # If unbalanced, try to fix common issues
    if open_parens > close_parens:
        # Rule might be incomplete - check if it ends properly
        if not cleaned.rstrip().endswith("."):
            # Add missing closing parentheses and period
            missing = open_parens - close_parens
            cleaned = cleaned.rstrip(";").rstrip(",") + ")" * missing + "."

    # Ensure rule ends with a period
    if not cleaned.endswith("."):
        cleaned = cleaned.rstrip(";").rstrip(",") + "."

    return cleaned


def _validate_prolog_syntax(prolog_code: str) -> tuple[bool, str | None]:
    """
    Validate Prolog syntax by attempting to parse it.

    Args:
        prolog_code: Prolog rule code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    from pyswip import Prolog

    # Clean the rule first
    cleaned_rule = _clean_prolog_rule(prolog_code)

    # Redirect stdin to /dev/null to prevent interactive prompts
    devnull = open(os.devnull)
    original_stdin = sys.stdin
    sys.stdin = devnull

    try:
        prolog = Prolog()
        # Initialize to avoid prompts
        try:
            list(prolog.query("true"))
        except Exception:
            pass

        # Try to assert the rule - if it fails, syntax is invalid
        # Remove the period - assertz expects a term, not a clause with period
        rule_term = cleaned_rule.rstrip(".").strip()

        try:
            # First try: use assertz method directly (handles quotes better)
            prolog.assertz(rule_term)
        except Exception:
            try:
                # Second try: use query with assertz wrapped in parentheses
                assert_query = f"assertz(({rule_term}))"
                list(prolog.query(assert_query))
            except Exception:
                try:
                    # Third try: use query without extra parentheses
                    assert_query = f"assertz({rule_term})"
                    list(prolog.query(assert_query))
                except Exception:
                    # Last resort: use pyrun if available
                    try:
                        prolog.pyrun(f"assertz(({rule_term})).")
                    except AttributeError:
                        # pyrun not available, raise the last exception
                        raise
        prolog.retractall("valid(_)")
        return True, None
    except Exception as e:
        error_msg = str(e)
        # Extract more specific error if available
        if "syntax_error" in error_msg:
            # Try to extract the specific error location
            if "** here **" in error_msg:
                lines = error_msg.split("\n")
                for i, line in enumerate(lines):
                    if "** here **" in line and i > 0:
                        error_msg = f"{lines[i-1]}\n{line}"
                        break
        return False, f"{error_msg}. Rule: {cleaned_rule}"
    finally:
        # Restore stdin
        sys.stdin = original_stdin
        devnull.close()


def induce_prolog_rule(
    structured_examples: list[dict[str, Any]],
    lm: dspy.LM,
    max_retries: int = 3,
    case_description: str | None = None,
) -> PrologRuleSpec:
    """
    Induce a Prolog rule from structured data examples.

    Args:
        structured_examples: List of dicts with 'input' (structured data) and 'valid' (bool) keys
        lm: DSPy language model instance
        max_retries: Maximum number of retries if generated rule is invalid
        case_description: Optional business context and domain knowledge to guide rule creation

    Returns:
        PrologRuleSpec containing the generated rule

    Raises:
        ValueError: If unable to generate valid Prolog rule after retries
    """
    # Generate example fact structure from first example
    if structured_examples:
        first_example = structured_examples[0]["input"]
        fact_examples = []
        required_fields = list(first_example.keys())
        for field_name, value in first_example.items():
            if isinstance(value, str):
                fact_examples.append(f"{field_name}(e1, '{value}')")
            else:
                fact_examples.append(f"{field_name}(e1, {value})")
        fact_structure = ", ".join(fact_examples)
    else:
        fact_structure = "field_name(e1, value)"
        required_fields = []

    predictor = dspy.Predict(InduceLogic)
    current_fact_structure = fact_structure

    for attempt in range(max_retries):
        result = predictor(
            structured_examples=str(structured_examples),
            fact_structure=current_fact_structure,
            required_fields=str(required_fields),
            case_description=case_description or "No specific business context provided.",
        )

        # Parse JSON output and convert to PrologRuleSpec
        try:
            rule_json = json.loads(result.rule)
            rule_spec = PrologRuleSpec(**rule_json)
        except (json.JSONDecodeError, TypeError):
            # If it's already a dict or PrologRuleSpec, handle it
            if isinstance(result.rule, dict):
                rule_spec = PrologRuleSpec(**result.rule)
            else:
                # Try to extract JSON from markdown code blocks
                rule_str = str(result.rule)
                if "```json" in rule_str:
                    rule_str = rule_str.split("```json")[1].split("```")[0].strip()
                elif "```" in rule_str:
                    rule_str = rule_str.split("```")[1].split("```")[0].strip()
                rule_json = json.loads(rule_str)
                rule_spec = PrologRuleSpec(**rule_json)

        # Clean and validate Prolog syntax
        rule_spec.prolog_code = _clean_prolog_rule(rule_spec.prolog_code)
        is_valid, error_msg = _validate_prolog_syntax(rule_spec.prolog_code)
        if is_valid:
            return rule_spec

        # If invalid and not last attempt, retry with error feedback
        if attempt < max_retries - 1:
            # Add error feedback to the prompt for next attempt
            error_feedback = (
                f"Previous attempt failed with Prolog syntax error: {error_msg}. "
                f"Please fix the syntax. The rule must be COMPLETE and use "
                f"field_name(X, Value) pattern. For string comparisons, use "
                f"member/2 predicate: member(Value, [list]). Avoid complex "
                f"disjunctions with parentheses. The rule must check all fields: "
                f"{required_fields}. Example: valid(X) :- amount(X, A), A =< 5000, "
                f"destination_country(X, Country), member(Country, ['US', 'Canada'])."
            )
            current_fact_structure = f"{fact_structure}. {error_feedback}"
        else:
            raise ValueError(
                f"Unable to generate valid Prolog rule after {max_retries} attempts. "
                f"Last error: {error_msg}. Generated rule: {rule_spec.prolog_code}"
            )

    raise ValueError("Failed to generate valid Prolog rule")
