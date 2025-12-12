"""Example demonstrating schema adaptation for different domains."""

from neurosymbols import NeurosymbolicPipeline


def main():
    """
    Demonstrate how the pipeline automatically adapts to different domains.

    This example shows banking transaction validation - the pipeline will
    automatically discover that it needs 'amount' and 'country' fields instead
    of 'age' and 'status', without any code changes.
    """

    # INPUT: Banking transaction data
    # The pipeline will discover it needs 'amount' and 'country' fields
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

    # Train - will discover banking-specific schema and rules
    pipeline.train(raw_training_data)

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
