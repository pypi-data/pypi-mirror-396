"""
Kateryna - Epistemic Uncertainty Layer for LLMs
===============================================

Stop your LLMs from hallucinating. Let them say "I don't know."

Named after Kateryna Yushchenko (1919-2001), Ukrainian computer scientist
who invented indirect addressing (pointers) in 1955, systematically erased
from Western computing history.

Inspired by Brusentsov's Setun balanced ternary computer (1958):
- +1 = CONFIDENT (grounded in evidence)
-  0 = UNCERTAIN (abstain)
- -1 = OVERCONFIDENT (potential hallucination - DANGER)

The -1 state is the breakthrough. It catches confident bullshit.

DOI: 10.5281/zenodo.17875182

Quick Start:
    # Standalone detector (works with any LLM output)
    from kateryna import EpistemicDetector, TernaryState

    detector = EpistemicDetector()
    state = detector.analyze(
        "The capital of Freedonia is definitely Fredville.",
        retrieval_confidence=0.05  # No RAG grounding
    )

    if state.is_danger_zone:
        print("DANGER: Confident response without grounding!")
        # state.state == TernaryState.OVERCONFIDENT (-1)

    # With OpenAI
    from kateryna.adapters.openai import OpenAISyncEpistemicAdapter
    from openai import OpenAI

    client = OpenAISyncEpistemicAdapter(OpenAI(), model="gpt-4")
    response = client.generate_with_rag("Explain this code", rag_chunks=chunks)

    # With local Ollama
    from kateryna.adapters.ollama import OllamaSyncEpistemicAdapter

    client = OllamaSyncEpistemicAdapter(model="llama3.2")
    response = client.generate("What is quantum computing?")
"""

__version__ = "1.0.4"
__author__ = "Zane Hambly"

from .state import EpistemicState, EpistemicResponse, TernaryState
from .detector import EpistemicDetector, calculate_retrieval_confidence
from .languages import available_languages, get_markers

__all__ = [
    # Core
    'EpistemicDetector',
    'calculate_retrieval_confidence',
    # State
    'EpistemicState',
    'EpistemicResponse',
    'TernaryState',
    # Languages
    'available_languages',
    'get_markers',
    # Version
    '__version__',
]
