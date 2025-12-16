"""
Kateryna Basic Usage Example
============================

Shows how to use the epistemic detector standalone (without any LLM adapter).
Works with output from ANY LLM.
"""

from kateryna import EpistemicDetector, TernaryState, calculate_retrieval_confidence


def main():
    # Initialize detector
    detector = EpistemicDetector()

    print("=" * 60)
    print("KATERYNA - Epistemic Uncertainty Detection")
    print("=" * 60)
    print()

    # Example 1: Confident response WITH grounding
    print("Example 1: Confident + Strong RAG = TRUST")
    print("-" * 40)

    state = detector.analyze(
        text="The function calculates the sum of two numbers by adding them together.",
        question="What does this function do?",
        retrieval_confidence=0.85,
        chunks_found=5
    )

    print(f"State: {state.state.name} ({state.state.value})")
    print(f"Grounded: {state.grounded}")
    print(f"Should abstain: {state.should_abstain}")
    print(f"Reason: {state.reason}")
    print()

    # Example 2: Confident response WITHOUT grounding = DANGER!
    print("Example 2: Confident + Weak RAG = DANGER ZONE")
    print("-" * 40)

    state = detector.analyze(
        text="The capital of Freedonia is definitely Fredville, a bustling city.",
        question="What is the capital of Freedonia?",
        retrieval_confidence=0.05,  # Very low - no relevant chunks
        chunks_found=1
    )

    print(f"State: {state.state.name} ({state.state.value})")
    print(f"is_danger_zone: {state.is_danger_zone}")
    print(f"Should abstain: {state.should_abstain}")
    print(f"Reason: {state.reason}")
    print()

    # Example 3: Uncertain response (honest model)
    print("Example 3: Uncertain Response = Appropriate Abstention")
    print("-" * 40)

    state = detector.analyze(
        text="I'm not sure about this. It might be related to sorting, but I'm uncertain.",
        question="What does this algorithm do?",
        retrieval_confidence=0.4,
        chunks_found=3
    )

    print(f"State: {state.state.name} ({state.state.value})")
    print(f"Should abstain: {state.should_abstain}")
    print(f"Markers found: {state.markers_found}")
    print()

    # Example 4: Pre-question filtering (save tokens!)
    print("Example 4: Pre-Question Filtering")
    print("-" * 40)

    questions = [
        "What will Bitcoin be worth in 2030?",
        "How does this sorting algorithm work?",
        "Who will win the next election?",
    ]

    for q in questions:
        should_abstain, reason = detector.should_abstain_on_question(q)
        status = "ABSTAIN" if should_abstain else "PROCEED"
        print(f"[{status}] {q}")

    print()

    # Example 5: RAG confidence calculation
    print("Example 5: RAG Confidence Calculation")
    print("-" * 40)

    # Simulate chunks from different vector DBs
    pinecone_chunks = [
        {"content": "...", "distance": 0.1},
        {"content": "...", "distance": 0.2},
    ]

    chroma_chunks = [
        {"document": "...", "distance": 0.8},
        {"document": "...", "distance": 0.9},
    ]

    weaviate_chunks = [
        {"text": "...", "score": 0.75},
    ]

    for name, chunks in [("Pinecone", pinecone_chunks), ("Chroma (bad)", chroma_chunks), ("Weaviate", weaviate_chunks)]:
        conf, count = calculate_retrieval_confidence(chunks)
        print(f"{name}: {conf:.0%} confidence from {count} chunks")

    print()
    print("=" * 60)
    print("Key insight: State -1 (OVERCONFIDENT) catches hallucinations")
    print("that look confident but have no grounding.")
    print("=" * 60)


if __name__ == "__main__":
    main()
