"""Example demonstrating rule induction from existing Pydantic schema."""

from pydantic import BaseModel, Field

from neurosymbols import NeurosymbolicPipeline


class Transaction(BaseModel):
    """Banking transaction model."""

    amount: float = Field(..., description="Transaction amount in dollars")
    country: str = Field(..., description="Destination country")


def main():
    """
    Demonstrate training Prolog rules from an existing Pydantic model.

    This is useful when you already have a well-defined schema but want
    to learn validation rules from examples.
    """

    # We have a schema, but want to learn rules
    raw_training_data = [
        {
            "text": "Transfer of $500 to United States account",
            "valid": True,
        },
        {
            "text": "Payment of $1200 sent to US",
            "valid": True,
        },
        {
            "text": "Transaction of $50,000 to Russia",
            "valid": False,  # High amount to restricted country
        },
        {
            "text": "Small transfer of $100 to Canada",
            "valid": True,
        },
        {
            "text": "Wire transfer of $75,000 to North Korea",
            "valid": False,  # High amount to restricted country
        },
    ]

    # Initialize Pipeline
    pipeline = NeurosymbolicPipeline(
        model_id="gpt-4.1-mini",
        verbose=True,
    )

    # Train rules from existing schema
    # This extracts data using the Transaction model, then induces Prolog rules
    pipeline.train_rules_from_schema(Transaction, raw_training_data)

    # Test on new transactions
    print("\n--- TEST PHASE ---")
    test_cases = [
        ("Transfer $200 to United States", True),
        ("Payment of $60,000 to Russia", False),  # High amount to restricted country
        ("Small $50 transfer to Canada", True),
    ]

    for text, expected in test_cases:
        result = pipeline.predict(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: '{text}' -> Valid? {result} (expected {expected})")


if __name__ == "__main__":
    main()
