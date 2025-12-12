"""Main pipeline orchestrator for the neuro-symbolic double induction workflow."""

import os
import sys
from typing import Any

import dspy  # type: ignore[import-untyped]
from pydantic import BaseModel, Field, create_model
from pyswip import Prolog

from neurosymbols.discovery import discover_schema
from neurosymbols.extraction import extract_data
from neurosymbols.induction import induce_prolog_rule
from neurosymbols.schema import SchemaDefinition
from neurosymbols.utils import pydantic_model_to_schema_definition


class TrainingExample:
    """Training example with unstructured text and validity label."""

    def __init__(self, text: str, valid: bool):
        self.text = text
        self.valid = valid


class NeurosymbolicPipeline:
    """
    Neuro-Symbolic Pipeline performing Double Induction.

    Transforms unstructured text → structured data → symbolic logic through:
    1. Structure Induction: Discovers Pydantic schema from text
    2. Logic Induction: Discovers Prolog rules from structured data
    """

    def __init__(
        self,
        model_id: str = "gpt-4.1-mini",
        api_key: str | None = None,
        api_base: str | None = None,
        api_version: str | None = None,
        lm: dspy.LM | None = None,
        verbose: bool = False,
    ):
        """
        Initialize the neuro-symbolic pipeline.

        Args:
            model_id: LLM model identifier (default: "gpt-4.1-mini")
            api_key: API key for the LLM (default: from environment)
            api_base: API base URL (for Azure OpenAI or custom endpoints)
            api_version: API version (for Azure OpenAI)
            lm: Optional DSPy language model instance (overrides model_id/api_key)
            verbose: Print progress information during training and prediction
        """
        self.verbose = verbose

        # Initialize language model
        if lm is not None:
            self.lm = lm
        else:
            self.lm = dspy.LM(
                model_id, api_key=api_key, api_base=api_base, api_version=api_version
            )

        dspy.configure(lm=self.lm)

        # Initialize Prolog engine in non-interactive mode
        # Redirect stdin to /dev/null to prevent interactive prompts
        self._original_stdin = sys.stdin
        self.prolog = Prolog()
        # Suppress interactive prompts by initializing with a query
        try:
            list(self.prolog.query("true"))
        except Exception:
            pass  # Ignore initialization errors

        # Pipeline state
        self.schema_def: SchemaDefinition | None = None
        self.dynamic_model: type[BaseModel] | None = None
        self.prolog_rule: str | None = None

    def train(
        self,
        raw_examples: list[dict[str, Any]],
        schema: SchemaDefinition | type[BaseModel] | None = None,
        prolog_rule: str | None = None,
        case_description: str | None = None,
    ) -> None:
        """
        Train the pipeline on unstructured text examples.

        Performs double induction (unless schema/rule provided):
        1. Structure Induction: Discovers schema from text (if schema not provided)
        2. Logic Induction: Discovers Prolog rules from structured data (if rule not provided)

        Args:
            raw_examples: List of dicts with 'text' (str) and 'valid' (bool) keys
            schema: Optional pre-existing schema (SchemaDefinition or Pydantic model).
                   If None, schema will be discovered from examples.
            prolog_rule: Optional pre-existing Prolog rule string.
                        If None, rule will be induced from structured data.
            case_description: Optional business context and domain knowledge to guide
                            schema discovery and rule creation. Provides nuance and
                            business rules that may not be evident from examples alone.
        """
        # Step 1: Schema Discovery (if not provided)
        if schema is None:
            if self.verbose:
                print(f"--- 1. Discovering Schema from {len(raw_examples)} examples ---")

            all_texts = [ex["text"] for ex in raw_examples]
            self.schema_def = discover_schema(all_texts, self.lm, case_description)

            if self.verbose:
                field_names = [f.name for f in self.schema_def.fields]
                print(f"   > Generated Schema: {field_names}")

            # Create Dynamic Pydantic Model from discovered schema
            self.dynamic_model = self._create_dynamic_pydantic_model(self.schema_def)
        else:
            if self.verbose:
                print("--- 1. Using Provided Schema ---")

            # Handle Pydantic model or SchemaDefinition
            if isinstance(schema, type) and issubclass(schema, BaseModel):
                self.dynamic_model = schema
                self.schema_def = pydantic_model_to_schema_definition(schema)
            else:
                self.schema_def = schema
                self.dynamic_model = self._create_dynamic_pydantic_model(schema)

            if self.verbose:
                field_names = [f.name for f in self.schema_def.fields]
                print(f"   > Using Schema: {field_names}")

        # Step 2: Extract Structured Data
        if self.verbose:
            print("--- 2. Extracting Structured Data ---")

        structured_dataset = []

        for ex in raw_examples:
            try:
                # Extract data from text
                extracted_dict = extract_data(ex["text"], self.schema_def, self.lm)

                # Validate and structure with Pydantic
                clean_obj = self.dynamic_model(**extracted_dict)
                structured_dataset.append(
                    {"input": clean_obj.model_dump(), "valid": ex["valid"]}
                )
            except Exception as e:
                if self.verbose:
                    print(f"   > Extraction Failed for '{ex['text']}': {e}")
                continue

        if not structured_dataset:
            raise ValueError(
                "No valid structured examples extracted. Check your input data."
            )

        # Step 3: Logic Induction (if rule not provided)
        if prolog_rule is None:
            if self.verbose:
                print("--- 3. Inducing Prolog Logic ---")

            logic_result = induce_prolog_rule(
                structured_dataset, self.lm, case_description=case_description
            )
            # Rule is already cleaned by induce_prolog_rule
            self.prolog_rule = logic_result.prolog_code

            if self.verbose:
                print(f"   > Generated Rule: {self.prolog_rule}")
                print(f"   > Rationale: {logic_result.rationale}")
        else:
            if self.verbose:
                print("--- 3. Using Provided Prolog Rule ---")
            # Clean provided rule
            from neurosymbols.induction import _clean_prolog_rule

            self.prolog_rule = _clean_prolog_rule(prolog_rule)
            if self.verbose:
                print(f"   > Using Rule: {self.prolog_rule}")

    def train_rules_from_schema(
        self,
        model: type[BaseModel],
        raw_examples: list[dict[str, Any]],
        case_description: str | None = None,
    ) -> None:
        """
        Train Prolog rules from an existing Pydantic model.

        Uses the provided Pydantic model to extract structured data from text,
        then induces Prolog rules from the structured examples.

        Args:
            model: Pydantic model class to use for extraction
            raw_examples: List of dicts with 'text' (str) and 'valid' (bool) keys
            case_description: Optional business context and domain knowledge to guide
                            rule creation. Provides nuance and business rules that may
                            not be evident from examples alone.
        """
        if self.verbose:
            print(f"--- Training Rules from Existing Schema: {model.__name__} ---")

        # Set schema from Pydantic model
        self.dynamic_model = model
        self.schema_def = pydantic_model_to_schema_definition(model)

        if self.verbose:
            field_names = [f.name for f in self.schema_def.fields]
            print(f"   > Using Schema: {field_names}")

        # Extract structured data
        if self.verbose:
            print("--- Extracting Structured Data ---")

        structured_dataset = []

        for ex in raw_examples:
            try:
                extracted_dict = extract_data(ex["text"], self.schema_def, self.lm)
                clean_obj = self.dynamic_model(**extracted_dict)
                structured_dataset.append(
                    {"input": clean_obj.model_dump(), "valid": ex["valid"]}
                )
            except Exception as e:
                if self.verbose:
                    print(f"   > Extraction Failed for '{ex['text']}': {e}")
                continue

        if not structured_dataset:
            raise ValueError(
                "No valid structured examples extracted. Check your input data."
            )

        # Induce Prolog rules
        if self.verbose:
            print("--- Inducing Prolog Logic ---")

        logic_result = induce_prolog_rule(
            structured_dataset, self.lm, case_description=case_description
        )
        self.prolog_rule = logic_result.prolog_code

        if self.verbose:
            print(f"   > Generated Rule: {self.prolog_rule}")
            print(f"   > Rationale: {logic_result.rationale}")

    def set_schema(
        self, schema: SchemaDefinition | type[BaseModel]
    ) -> None:
        """
        Manually set the schema for the pipeline.

        Args:
            schema: SchemaDefinition or Pydantic model class
        """
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            self.dynamic_model = schema
            self.schema_def = pydantic_model_to_schema_definition(schema)
        else:
            self.schema_def = schema
            self.dynamic_model = self._create_dynamic_pydantic_model(schema)

    def set_prolog_rule(self, rule: str) -> None:
        """
        Manually set the Prolog rule for the pipeline.

        Args:
            rule: Prolog rule string
        """
        from neurosymbols.induction import _clean_prolog_rule

        self.prolog_rule = _clean_prolog_rule(rule)

    def predict(self, new_text: str) -> bool:
        """
        Predict validity of new unstructured text.

        Pipeline: Text → Pydantic → Prolog → Result

        Args:
            new_text: Raw text input to evaluate

        Returns:
            True if the text is valid according to learned rules, False otherwise

        Raises:
            ValueError: If pipeline hasn't been trained yet
        """
        if self.schema_def is None or self.dynamic_model is None or self.prolog_rule is None:
            raise ValueError(
                "Pipeline must be trained before prediction. Call train() first."
            )

        # Step 1: Extract structured data
        extracted_dict = extract_data(new_text, self.schema_def, self.lm)

        # Step 2: Structure with Pydantic
        data_obj = self.dynamic_model(**extracted_dict)
        data_dict = data_obj.model_dump()

        # Step 3: Validate with Prolog
        return self._run_prolog(data_dict)

    def _create_dynamic_pydantic_model(
        self, schema_def: SchemaDefinition
    ) -> type[BaseModel]:
        """
        Create a dynamic Pydantic model from schema definition.

        Args:
            schema_def: Schema definition to convert

        Returns:
            Pydantic model class
        """
        fields = {}
        type_map = {"int": int, "float": float, "str": str, "bool": bool}

        for field in schema_def.fields:
            py_type = type_map.get(field.type_name, str)
            fields[field.name] = (
                py_type,
                Field(..., description=field.description),
            )

        return create_model(schema_def.model_name, **fields)  # type: ignore[call-overload]

    def _run_prolog(self, data_item: dict[str, Any]) -> bool:
        """
        Execute Prolog validation on structured data.

        Args:
            data_item: Dictionary of field names to values

        Returns:
            True if valid according to Prolog rules, False otherwise
        """
        if self.prolog_rule is None:
            raise ValueError("Prolog rule not set. Pipeline must be trained first.")

        # Redirect stdin to /dev/null to prevent interactive prompts
        devnull = open(os.devnull)
        original_stdin = sys.stdin
        sys.stdin = devnull

        try:
            # Ensure rule is cleaned before use
            from neurosymbols.induction import _clean_prolog_rule

            cleaned_rule = _clean_prolog_rule(self.prolog_rule)

            # Reset Prolog state
            self.prolog.retractall("valid(_)")
            for key in data_item.keys():
                self.prolog.retractall(f"{key}(_,_)")

            entity_id = "e1"

            # Assert facts
            for key, value in data_item.items():
                if isinstance(value, str):
                    safe_val = f"'{value}'"
                else:
                    safe_val = str(value)
                self.prolog.assertz(f"{key}({entity_id}, {safe_val})")

            # Assert rule - remove period first (assertz expects a term)
            rule_term = cleaned_rule.rstrip(".").strip()

            try:
                # First try: use assertz method directly (handles quotes better)
                self.prolog.assertz(rule_term)
            except Exception:
                try:
                    # Second try: use query with assertz wrapped in parentheses
                    assert_query = f"assertz(({rule_term}))"
                    list(self.prolog.query(assert_query))
                except Exception:
                    try:
                        # Third try: use query without extra parentheses
                        assert_query = f"assertz({rule_term})"
                        list(self.prolog.query(assert_query))
                    except Exception:
                        # Last resort: use pyrun if available
                        try:
                            self.prolog.pyrun(f"assertz(({rule_term})).")
                        except AttributeError:
                            # pyrun not available, raise the last exception
                            raise

            # Query - using list() to consume all results
            results = list(self.prolog.query(f"valid({entity_id})"))
            return len(results) > 0
        except Exception as e:
            if self.verbose:
                print(f"Prolog Error: {e}")
                print(f"Invalid rule: {self.prolog_rule}")
            return False
        finally:
            # Restore stdin
            sys.stdin = original_stdin
            devnull.close()
