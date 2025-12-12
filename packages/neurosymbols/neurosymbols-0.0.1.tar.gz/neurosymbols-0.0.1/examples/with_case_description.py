"""Example demonstrating pipeline with case description for business context."""

from neurosymbols import NeurosymbolicPipeline


def main():
    """
    Demonstrate using case_description to provide business context.

    The case_description helps guide schema discovery and rule creation
    by providing domain knowledge that may not be evident from examples alone.
    """

    # Case description provides business context and domain knowledge
    case_description = """
    Banking Transaction Validation Rules:
    - Transactions to certain countries (Russia, North Korea, Iran) are restricted
    - High-value transactions (>$50,000) to restricted countries are always invalid
    - Transactions to approved countries (United States, US, Canada) are generally valid
    - Small transactions (<$5,000) are typically valid regardless of destination
    - Medium transactions ($5,000-$50,000) require destination country validation
    """

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

    # Train with case description - provides business context for better schema and rules
    pipeline.train(raw_training_data, case_description=case_description)

    # Test on new transactions
    print("\n--- TEST PHASE ---")
    test_cases = [
        ("Transfer $200 to United States", True),
        ("Payment of $60,000 to Russia", False),  # High amount to restricted country
        ("Small $50 transfer to Canada", True),
        ("Transaction of $10,000 to Iran", False),  # Medium amount to restricted country
    ]

    for text, expected in test_cases:
        result = pipeline.predict(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: '{text}' -> Valid? {result} (expected {expected})")


if __name__ == "__main__":
    main()
