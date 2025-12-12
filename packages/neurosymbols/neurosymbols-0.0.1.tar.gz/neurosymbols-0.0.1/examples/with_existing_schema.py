"""Example demonstrating pipeline with pre-existing Pydantic schema."""

from pydantic import BaseModel, Field

from neurosymbols import NeurosymbolicPipeline


class User(BaseModel):
    """User model with age and status fields."""

    age: int = Field(..., description="User age in years")
    status: str = Field(..., description="Account status: 'active' or 'suspended'")


def main():
    """Run pipeline with existing schema, only inducing rules."""

    # We already have a schema, so we skip schema discovery
    raw_training_data = [
        {"text": "User John is 25 years old and his account is active.", "valid": True},
        {"text": "Sarah is 40 years old, current status is active.", "valid": True},
        {"text": "Mike is 16 years old, account is active.", "valid": False},  # Too young
        {
            "text": "Emily is 30, but her account is suspended.",
            "valid": False,
        },  # Wrong status
    ]

    # Initialize Pipeline
    pipeline = NeurosymbolicPipeline(
        model_id="gpt-4.1-mini",
        verbose=True,
    )

    # Train with existing schema - only induces Prolog rules
    # Schema discovery is skipped since we provide the User model
    pipeline.train(raw_training_data, schema=User)

    # Test on NEW unstructured text
    print("\n--- TEST PHASE ---")
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
