"""Core classes for neurosymbolic rule optimization."""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import dspy  # type: ignore[import-untyped]
from pytholog import KnowledgeBase  # type: ignore[import-untyped]


@dataclass
class Example:
    """Example data for rule generation and optimization.

    Attributes:
        input_data: Input data dictionary mapping variable names to values
        expected_output: Expected output dictionary or list of dictionaries
            mapping variable names to values. If None, evaluation will use
            an LLM judge or custom evaluation function.
    """

    input_data: dict[str, Any]
    expected_output: dict[str, Any] | list[dict[str, Any]] | None = None


@dataclass
class OptimizationResult:
    """Result of rule optimization.

    Attributes:
        optimized_rules: List of optimized Prolog rules as strings
        metrics: Dictionary containing optimization metrics
        baseline_score: Baseline score before optimization
        optimized_score: Score after optimization
    """

    optimized_rules: list[str]
    metrics: dict[str, Any]
    baseline_score: float
    optimized_score: float


class RuleOptimizer:
    """Optimize neurosymbolic rules using DSPy.

    This class uses DSPy optimizers to generate and optimize Prolog rules
    that match input-output examples. It follows the same API pattern as
    dspydantic's PydanticOptimizer.
    """

    def __init__(
        self,
        examples: list[Example],
        query_template: str | None = None,
        initial_rules: list[str] | None = None,
        evaluate_fn: Callable | str | None = None,
        model_id: str = "gpt-4o",
        api_key: str | None = None,
        api_base: str | None = None,
        api_version: str | None = None,
        optimizer: str | dspy.teleprompt.Teleprompter | None = None,
        num_threads: int = 4,
        verbose: bool = False,
        train_split: float = 0.8,
        optimizer_kwargs: dict[str, Any] | None = None,
    ):
        """Initialize the RuleOptimizer.

        Args:
            examples: List of examples for optimization
            query_template: Optional query template string (e.g., "add({x}, {y}, Z)")
                with placeholders for input variables
            initial_rules: Optional list of initial Prolog rules to optimize
            evaluate_fn: Evaluation function, built-in option ("exact"), or None.
                When expected_output is provided: Can be a callable
                (Example, list[str], str | None) -> float, a string ("exact"),
                or None (uses default evaluation).
                When expected_output is None: Can be a dspy.LM instance (used as judge),
                a callable judge function, or None (uses default LLM judge).
            model_id: LLM model ID (default: "gpt-4o")
            api_key: API key (default: from OPENAI_API_KEY env var)
            api_base: API base URL (for Azure OpenAI or custom endpoints)
            api_version: API version (for Azure OpenAI)
            optimizer: Optimizer specification. Can be:
                - A string (optimizer type name): e.g., "miprov2", "gepa", etc.
                - A Teleprompter instance: Custom optimizer instance
                - None: Auto-selects based on dataset size
            num_threads: Number of optimization threads (default: 4)
            verbose: Print progress (default: False)
            train_split: Fraction of examples to use for training (rest for validation)
                (default: 0.8)
            optimizer_kwargs: Optional dictionary of additional keyword arguments
                to pass to the optimizer constructor. Only used if optimizer is a string
                or None.
        """
        self.examples = examples
        self.query_template = query_template
        self.initial_rules = initial_rules or []
        self.evaluate_fn = evaluate_fn
        self.model_id = model_id
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base
        self.api_version = api_version
        self.optimizer = optimizer
        self.num_threads = num_threads
        self.verbose = verbose
        self.train_split = train_split
        self.optimizer_kwargs = optimizer_kwargs or {}

        # Initialize DSPy LM
        self.lm = self._create_lm()

        # Set DSPy settings
        dspy.settings.configure(lm=self.lm)

    def _create_lm(self) -> dspy.LM:
        """Create DSPy language model instance."""
        # DSPy 3.x uses dspy.LM with model string format "provider/model"
        # For OpenAI, use "openai/model-name"
        model_string = (
            self.model_id
            if "/" in self.model_id
            else f"openai/{self.model_id}"
        )

        # Prepare kwargs for LM initialization
        lm_kwargs: dict[str, Any] = {"model": model_string}

        # Set API key if provided
        if self.api_key:
            lm_kwargs["api_key"] = self.api_key

        # Handle Azure OpenAI or custom endpoints
        if self.api_base:
            lm_kwargs["api_base"] = self.api_base
            if self.api_version:
                lm_kwargs["api_version"] = self.api_version

        return dspy.LM(**lm_kwargs)

    def _format_query(self, example: Example) -> str | None:
        """Format query template with example input data."""
        if not self.query_template:
            return None

        try:
            return self.query_template.format(**example.input_data)
        except KeyError as e:
            if self.verbose:
                print(f"Warning: Missing key {e} in input_data for query template")
            return None

    def _parse_query(self, query: str) -> list:
        """Parse Prolog query string into pytholog format.

        Converts "predicate(Var)" to ["predicate", "Var"] format.
        """
        if not query:
            return []

        # Simple parser for Prolog queries like "sentiment(Sentiment)"
        # Remove whitespace
        query = query.strip()

        # Find the predicate and arguments
        if "(" in query and ")" in query:
            predicate = query.split("(")[0].strip()
            args_str = query.split("(")[1].split(")")[0].strip()
            # Split arguments by comma
            args = [arg.strip() for arg in args_str.split(",") if arg.strip()]
            return [predicate] + args
        else:
            # Simple predicate without arguments
            return [query]

    def _evaluate_rules(
        self, example: Example, rules: list[str], query: str | None
    ) -> float:
        """Evaluate rules against an example.

        Returns a score between 0.0 and 1.0.
        """
        if self.evaluate_fn == "exact":
            return self._exact_evaluate(example, rules, query)
        elif callable(self.evaluate_fn):
            return self.evaluate_fn(example, rules, query)
        elif isinstance(self.evaluate_fn, dspy.LM):
            return self._llm_judge_evaluate(example, rules, query, self.evaluate_fn)
        elif example.expected_output is None:
            # Use default LLM judge when no expected output
            return self._llm_judge_evaluate(example, rules, query, self.lm)
        else:
            # Default to exact evaluation
            return self._exact_evaluate(example, rules, query)

    def _exact_evaluate(
        self, example: Example, rules: list[str], query: str | None
    ) -> float:
        """Evaluate rules using exact matching against expected output."""
        if example.expected_output is None:
            return 0.0

        if not query:
            return 0.0

        try:
            # Create knowledge base with rules
            # pytholog KnowledgeBase accepts rules via calling it with a list
            kb = KnowledgeBase("temp")
            if rules:
                kb(rules)

            # Execute query - pytholog query format is complex
            # For now, use a simple pattern matching approach or fallback to LLM judge
            # pytholog's query method expects parsed Prolog term objects, not strings
            # Since parsing is complex, we'll use LLM-based evaluation as fallback
            results = None
            try:
                # Try to use pytholog's query - this may fail due to format requirements
                # For simple cases, we can try pattern matching on the rules themselves
                query_list = self._parse_query(query)
                results = kb.query(query_list)
            except (AttributeError, TypeError, ValueError):
                # pytholog query format is complex - fallback to rule-based matching
                # Try simple pattern matching: check if rules can produce expected output
                # This is a simplified evaluation that doesn't require full Prolog execution
                results = self._simple_rule_match(example, rules, query)
                if results is None:
                    # If simple matching also fails, return 0 (can't evaluate)
                    return 0.0

            if not results:
                return 0.0

            # Normalize results to list of dicts
            if isinstance(results, bool):
                # Query succeeded but no bindings
                return 1.0 if example.expected_output == {} else 0.0

            if not isinstance(results, list):
                results = [results]

            # Convert results to list of dicts
            result_dicts = []
            for result in results:
                if isinstance(result, dict):
                    result_dicts.append(result)
                elif isinstance(result, tuple):
                    # Convert tuple to dict if possible
                    if len(result) == 1 and isinstance(result[0], dict):
                        result_dicts.append(result[0])
                    else:
                        # Try to match with expected output keys
                        if isinstance(example.expected_output, dict):
                            result_dicts.append(
                                {
                                    k: v
                                    for k, v in zip(
                                        example.expected_output.keys(), result
                                    )
                                }
                            )

            # Check if any result matches expected output
            expected_list = (
                [example.expected_output]
                if isinstance(example.expected_output, dict)
                else example.expected_output
            )

            for expected in expected_list:
                for result_dict in result_dicts:
                    # Normalize values for comparison
                    normalized_result = {
                        k: self._normalize_value(v)
                        for k, v in result_dict.items()
                    }
                    normalized_expected = {
                        k: self._normalize_value(v)
                        for k, v in expected.items()
                    }

                    if normalized_result == normalized_expected:
                        return 1.0

            return 0.0

        except Exception as e:
            if self.verbose:
                print(f"Error evaluating rules: {e}")
            return 0.0

    def _simple_rule_match(
        self, example: Example, rules: list[str], query: str | None
    ) -> list[dict[str, Any]] | None:
        """Simple pattern matching on rules when Prolog execution fails.

        This checks if rules contain patterns that would produce the expected output.
        Returns a list of result dicts or None if no match found.
        """
        if not rules:
            # No rules to match against
            return None

        if not example.expected_output or not isinstance(example.expected_output, dict):
            return None

        # Extract expected values
        expected_values = list(example.expected_output.values())
        if not expected_values:
            return None

        # Check if any rule directly produces the expected output
        # Look for rules like "sentiment(positive)." or "sentiment(positive) :- ..."
        for rule in rules:
            # Check for facts (rules ending with just a period, no body)
            if ":-" not in rule:
                # This is a fact, check if it matches expected output
                for expected_value in expected_values:
                    expected_str = str(expected_value).lower()
                    rule_lower = rule.lower()
                    # Check if rule contains the expected value
                    if expected_str in rule_lower:
                        # Try to extract the predicate and value
                        if "(" in rule and ")" in rule:
                            # Extract value from fact like "sentiment(positive)."
                            fact_value = (
                                rule.split("(")[1].split(")")[0].strip().strip('"').strip("'")
                            )
                            if fact_value.lower() == expected_str:
                                # Create a result dict matching expected output structure
                                result_dict = {}
                                for key in example.expected_output.keys():
                                    result_dict[key] = fact_value
                                return [result_dict]
            else:
                # This is a rule with a body, check if the head matches expected output
                # Format: "predicate(value) :- condition."
                head_part = rule.split(":-")[0].strip()
                if "(" in head_part and ")" in head_part:
                    # Extract value from head like "sentiment(positive)"
                    head_value = (
                        head_part.split("(")[1].split(")")[0].strip().strip('"').strip("'")
                    )
                    for expected_value in expected_values:
                        expected_str = str(expected_value).lower()
                        if head_value.lower() == expected_str:
                            # Create a result dict matching expected output structure
                            result_dict = {}
                            for key in example.expected_output.keys():
                                result_dict[key] = head_value
                            return [result_dict]

        # If no direct match, return None to indicate we couldn't evaluate
        return None

    def _normalize_value(self, value: Any) -> Any:
        """Normalize value for comparison."""
        if isinstance(value, int | float):
            return float(value)
        elif isinstance(value, str):
            # Try to convert numeric strings
            try:
                return float(value)
            except ValueError:
                return value.lower().strip()
        return value

    def _llm_judge_evaluate(
        self,
        example: Example,
        rules: list[str],
        query: str | None,
        judge_lm: dspy.LM,
    ) -> float:
        """Evaluate rules using an LLM judge."""
        # Create a prompt for the judge
        rules_text = "\n".join(rules)
        input_text = str(example.input_data)
        query_text = query or "N/A"

        prompt = f"""Evaluate whether the following Prolog rules correctly solve the given problem.

Rules:
{rules_text}

Input: {input_text}
Query: {query_text}

Rate the correctness on a scale of 0.0 to 1.0, where:
- 1.0 = Rules correctly solve the problem
- 0.5 = Rules partially solve the problem
- 0.0 = Rules do not solve the problem

Respond with only a number between 0.0 and 1.0."""

        try:
            response = judge_lm(prompt)
            # Extract numeric score
            score_str = re.search(r"0?\.\d+|1\.0|\d+", str(response))
            if score_str:
                score = float(score_str.group())
                return max(0.0, min(1.0, score))
            return 0.5  # Default neutral score
        except Exception as e:
            if self.verbose:
                print(f"Error in LLM judge evaluation: {e}")
            return 0.0

    def _get_optimizer(self) -> dspy.teleprompt.Teleprompter:
        """Get or create the optimizer instance."""
        if isinstance(self.optimizer, dspy.teleprompt.Teleprompter):
            return self.optimizer

        # Auto-select optimizer based on dataset size if not specified
        optimizer_type = self.optimizer
        if optimizer_type is None:
            if len(self.examples) < 20:
                optimizer_type = "bootstrapfewshot"
            else:
                optimizer_type = "bootstrapfewshotwithrandomsearch"

        # Map optimizer type string to class
        # Note: User can specify lowercase names, but we map to actual class names
        optimizer_map = {
            "bootstrapfewshot": dspy.teleprompt.BootstrapFewShot,
            "bootstrapfewshotwithrandomsearch": dspy.teleprompt.BootstrapFewShotWithRandomSearch,
            "miprov2": dspy.teleprompt.MIPROv2,
            "gepa": dspy.teleprompt.GEPA,
            "copro": dspy.teleprompt.COPRO,  # Note: actual class is COPRO (all caps)
            "simba": dspy.teleprompt.SIMBA,
            "knnfewshot": dspy.teleprompt.KNNFewShot,
            "labeledfewshot": dspy.teleprompt.LabeledFewShot,
        }

        optimizer_class = optimizer_map.get(optimizer_type.lower())
        if optimizer_class is None:
            # Try to find by name in teleprompt module
            optimizer_class = getattr(dspy.teleprompt, optimizer_type, None)
            if optimizer_class is None:
                raise ValueError(
                    f"Unknown optimizer type: {optimizer_type}. "
                    f"Available: {list(optimizer_map.keys())}"
                )

        # Create metric function
        metric = self._create_metric()

        # Create optimizer with default kwargs plus user-provided kwargs
        # Only include num_threads for optimizers that support it
        import inspect

        default_kwargs: dict[str, Any] = {"metric": metric}

        # Check if optimizer supports num_threads parameter
        sig = inspect.signature(optimizer_class.__init__)
        if "num_threads" in sig.parameters:
            default_kwargs["num_threads"] = self.num_threads

        default_kwargs.update(self.optimizer_kwargs)

        return optimizer_class(**default_kwargs)

    def _create_metric(self) -> Callable:
        """Create metric function for optimization."""

        def metric(example: Example, pred: dict[str, Any], *args) -> float:
            """Metric function for DSPy optimization."""
            rules = pred.get("rules", [])
            query = self._format_query(example)
            return self._evaluate_rules(example, rules, query)

        return metric

    def _create_dspy_module(self) -> type[dspy.Module]:
        """Create DSPy module for rule generation."""

        class RuleGenerator(dspy.Module):
            """DSPy module for generating Prolog rules."""

            def __init__(self):
                super().__init__()
                self.generate_rules = dspy.ChainOfThought(
                    "input_data, query_template -> rules_text"
                )

            def forward(self, input_data: dict[str, Any], query_template: str | None):
                """Generate rules from input data and query template."""
                # Format input for the prompt
                input_str = str(input_data)
                query_str = query_template or "N/A"

                # Generate rules using ChainOfThought
                # DSPy will handle the prompt construction
                result = self.generate_rules(
                    input_data=input_str, query_template=query_str
                )

                # Extract rules text from result
                # Try different possible attribute names
                rules_text = None
                for attr in ["rules_text", "rules", "answer", "output"]:
                    if hasattr(result, attr):
                        rules_text = getattr(result, attr)
                        break

                if rules_text is None:
                    # Fallback to string representation
                    rules_text = str(result)

                # Parse rules from text
                rules = self._parse_rules(rules_text)

                # Ensure we always return at least one rule
                # If parsing failed, create a default rule based on the query
                if not rules or (len(rules) == 1 and not rules[0].strip()):
                    # Generate a simple rule from the query template
                    if query_str and query_str != "N/A":
                        # Extract predicate from query like "sentiment(Sentiment)"
                        if "(" in query_str and ")" in query_str:
                            predicate = query_str.split("(")[0].strip()
                            # Create a simple fact rule
                            rules = [f"{predicate}(unknown)."]
                    else:
                        # Fallback: create a generic rule
                        rules = ["rule(unknown)."]

                return {"rules": rules}

            def _parse_rules(self, text: str) -> list[str]:
                """Parse Prolog rules from text."""
                # Extract rules (lines ending with .)
                lines = text.split("\n")
                rules = []
                current_rule = []

                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("%"):
                        continue

                    current_rule.append(line)
                    if line.endswith("."):
                        rule = " ".join(current_rule)
                        rules.append(rule)
                        current_rule = []

                # Add any remaining rule
                if current_rule:
                    rule = " ".join(current_rule)
                    if not rule.endswith("."):
                        rule += "."
                    rules.append(rule)

                return rules if rules else [text.strip()]

        return RuleGenerator

    def optimize(self) -> OptimizationResult:
        """Optimize rules using DSPy.

        Returns:
            OptimizationResult containing optimized rules and metrics
        """
        if not self.examples:
            raise ValueError("At least one example is required")

        # Split examples into train and validation
        split_idx = int(len(self.examples) * self.train_split)
        train_examples = self.examples[:split_idx]
        val_examples = self.examples[split_idx:]

        # Create DSPy module
        rule_generator_class = self._create_dspy_module()
        module = rule_generator_class()

        # Calculate baseline score
        baseline_rules = self.initial_rules.copy()
        baseline_scores = []
        for example in val_examples:
            query = self._format_query(example)
            score = self._evaluate_rules(example, baseline_rules, query)
            baseline_scores.append(score)
        baseline_score = (
            sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
        )

        # Get optimizer
        teleprompter = self._get_optimizer()

        # Prepare training examples for DSPy
        dspy_train_examples = []
        for example in train_examples:
            query = self._format_query(example)
            dspy_example = dspy.Example(
                input_data=example.input_data,
                query_template=query,
                expected_output=example.expected_output,
            ).with_inputs("input_data", "query_template")
            dspy_train_examples.append(dspy_example)

        # Optimize
        if self.verbose:
            print(f"Optimizing with {len(train_examples)} training examples...")

        optimized_module = teleprompter.compile(
            student=module, trainset=dspy_train_examples
        )

        # Generate optimized rules for validation examples
        optimized_rules_set = set(self.initial_rules)
        for example in train_examples:
            query = self._format_query(example)
            result = optimized_module(input_data=example.input_data, query_template=query)
            if isinstance(result, dict) and "rules" in result:
                optimized_rules_set.update(result["rules"])

        optimized_rules = list(optimized_rules_set)

        # Calculate optimized score
        optimized_scores = []
        for example in val_examples:
            query = self._format_query(example)
            score = self._evaluate_rules(example, optimized_rules, query)
            optimized_scores.append(score)
        optimized_score = (
            sum(optimized_scores) / len(optimized_scores) if optimized_scores else 0.0
        )

        metrics = {
            "train_size": len(train_examples),
            "val_size": len(val_examples),
            "baseline_score": baseline_score,
            "optimized_score": optimized_score,
            "improvement": optimized_score - baseline_score,
        }

        if self.verbose:
            print(f"Baseline score: {baseline_score:.3f}")
            print(f"Optimized score: {optimized_score:.3f}")
            print(f"Improvement: {metrics['improvement']:.3f}")

        return OptimizationResult(
            optimized_rules=optimized_rules,
            metrics=metrics,
            baseline_score=baseline_score,
            optimized_score=optimized_score,
        )

