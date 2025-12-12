"""Example demonstrating manual setup of schema and rules."""

from pydantic import BaseModel, Field

from neurosymbols import NeurosymbolicPipeline


class User(BaseModel):
    """User model with age and status fields."""

    age: int = Field(..., description="User age in years")
    status: str = Field(..., description="Account status: 'active' or 'suspended'")


def main():
    """
    Demonstrate manually setting schema and rules without training.

    Useful when you want full control over the pipeline components.
    """

    # Initialize Pipeline
    pipeline = NeurosymbolicPipeline(
        model_id="gpt-4.1-mini",
        verbose=True,
    )

    # Manually set schema
    print("--- Setting Schema Manually ---")
    pipeline.set_schema(User)
    print(f"   > Schema: {[f.name for f in pipeline.schema_def.fields]}")

    # Manually set Prolog rule
    print("\n--- Setting Prolog Rule Manually ---")
    rule = "valid(X) :- age(X, A), A >= 18, status(X, 'active')."
    pipeline.set_prolog_rule(rule)
    print(f"   > Rule: {pipeline.prolog_rule}")

    # Now we can use the pipeline for prediction
    print("\n--- PREDICTION PHASE ---")
    test_cases = [
        ("Mark is 50 years old and active.", True),
        ("Jenny is 12 years old and active.", False),
        ("Tom is 25 years old but suspended.", False),
    ]

    for text, expected in test_cases:
        result = pipeline.predict(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: '{text}' -> Valid? {result} (expected {expected})")


if __name__ == "__main__":
    main()
