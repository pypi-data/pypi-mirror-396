"""
Kateryna with RAG Integration Example
=====================================

Shows how to integrate Kateryna with a RAG pipeline.
This example simulates RAG retrieval - replace with your actual vector DB.
"""

from kateryna import EpistemicDetector, TernaryState


def simulate_rag_search(query: str) -> tuple[list, float]:
    """
    Simulate RAG retrieval. Replace with your actual vector DB.

    Returns: (chunks, confidence)
    """
    # Simulate different retrieval scenarios
    knowledge_base = {
        "python": [
            {"content": "Python is a high-level programming language.", "distance": 0.1},
            {"content": "Python uses indentation for code blocks.", "distance": 0.15},
            {"content": "Python was created by Guido van Rossum.", "distance": 0.2},
        ],
        "cobol": [
            {"content": "COBOL uses PERFORM for loops.", "distance": 0.2},
            {"content": "COBOL divisions: IDENTIFICATION, ENVIRONMENT, DATA, PROCEDURE.", "distance": 0.25},
        ],
        "freedonia": [],  # No knowledge about fictional country
    }

    query_lower = query.lower()

    if "python" in query_lower:
        return knowledge_base["python"], 0.85
    elif "cobol" in query_lower:
        return knowledge_base["cobol"], 0.65
    else:
        return [], 0.0


def simulate_llm_response(query: str, chunks: list) -> str:
    """
    Simulate LLM response. Replace with your actual LLM.
    """
    if chunks:
        # Model has context, gives grounded answer
        return f"Based on the documentation, {chunks[0]['content']}"
    else:
        # Model has no context, but still answers confidently (hallucination!)
        return "The capital of Freedonia is definitely Fredville, a major economic hub."


def main():
    detector = EpistemicDetector()

    queries = [
        "What is Python?",
        "Explain COBOL divisions",
        "What is the capital of Freedonia?",  # Fictional - should trigger danger
    ]

    print("=" * 60)
    print("KATERYNA RAG INTEGRATION DEMO")
    print("=" * 60)
    print()

    for query in queries:
        print(f"Query: {query}")
        print("-" * 40)

        # Step 1: RAG retrieval
        chunks, rag_confidence = simulate_rag_search(query)
        print(f"RAG: {len(chunks)} chunks, {rag_confidence:.0%} confidence")

        # Step 2: LLM generation
        response = simulate_llm_response(query, chunks)
        print(f"LLM: {response[:60]}...")

        # Step 3: Epistemic analysis
        state = detector.analyze(
            text=response,
            question=query,
            retrieval_confidence=rag_confidence,
            chunks_found=len(chunks)
        )

        # Step 4: Decision
        print(f"State: {state.state.name}")
        print(f"Grounded: {state.grounded}")

        if state.is_danger_zone:
            print(">>> DANGER: Confident hallucination detected!")
            print(">>> Action: Replace with abstention message")
            final_response = (
                "I don't have reliable information about this topic. "
                "I'd rather say I don't know than risk giving incorrect information."
            )
        elif state.should_abstain:
            print(">>> Action: Abstain (uncertainty detected)")
            final_response = f"I'm not confident about this. {state.reason}"
        else:
            print(">>> Action: Return response (grounded)")
            final_response = response

        print(f"Final: {final_response[:60]}...")
        print()

    print("=" * 60)
    print("The Freedonia query shows the -1 state in action:")
    print("Confident response + no grounding = DANGER ZONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
