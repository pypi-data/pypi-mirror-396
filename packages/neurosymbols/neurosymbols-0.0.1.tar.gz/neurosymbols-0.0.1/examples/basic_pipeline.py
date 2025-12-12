"""Basic example demonstrating the neuro-symbolic double induction pipeline."""

from neurosymbols import NeurosymbolicPipeline


def main():
    """Run a complete example of the pipeline."""

    # INPUT: Completely unstructured text
    # The system doesn't know about "age" or "status" yet - it will discover them!
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

    # Run the "Double Induction" training
    # Phase 1: Structure Induction - discovers schema (age, status)
    # Phase 2: Logic Induction - discovers Prolog rules (age >= 18 AND status == 'active')
    pipeline.train(raw_training_data)

    # Test on NEW unstructured text
    print("\n--- TEST PHASE ---")
    test_cases = [
        ("Mark is 50 years old and active.", True),  # Should be True
        ("Jenny is 12 years old and active.", False),  # Should be False
        ("Tom is 25 years old but suspended.", False),  # Should be False
    ]

    for text, expected in test_cases:
        result = pipeline.predict(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: '{text}' -> Valid? {result} (expected {expected})")


if __name__ == "__main__":
    main()
