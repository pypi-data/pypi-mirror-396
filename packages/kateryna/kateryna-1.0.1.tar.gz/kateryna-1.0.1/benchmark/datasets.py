# -*- coding: utf-8 -*-
"""
Kateryna Benchmark Datasets
===========================

Test cases for validating hallucination detection.
Each case has:
- input: The LLM response to analyze
- question: The original question (optional)
- rag_confidence: Simulated RAG score (0.0-1.0)
- chunks_found: Number of RAG chunks
- expected_state: CONFIDENT (+1), UNCERTAIN (0), or OVERCONFIDENT (-1)
- expected_abstain: Whether the detector should recommend abstention
- category: Test category for reporting
- description: Human-readable description

DOI: 10.5281/zenodo.17875182
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class TestCategory(str, Enum):
    """Categories for benchmark organization."""
    HALLUCINATION_FICTIONAL = "hallucination_fictional"
    HALLUCINATION_CITATION = "hallucination_citation"
    HALLUCINATION_NUMERIC = "hallucination_numeric"
    HALLUCINATION_API = "hallucination_api"
    GROUNDED_STRONG = "grounded_strong"
    GROUNDED_HEDGED = "grounded_hedged"
    APPROPRIATE_ABSTENTION = "appropriate_abstention"
    EDGE_PARTIAL = "edge_partial"
    EDGE_UNGROUNDED_CORRECT = "edge_ungrounded_correct"
    UNANSWERABLE = "unanswerable"


@dataclass
class BenchmarkCase:
    """A single benchmark test case."""
    id: str
    input: str
    expected_state: int  # +1, 0, -1
    expected_abstain: bool
    category: TestCategory
    description: str
    question: str = ""
    rag_confidence: Optional[float] = None
    chunks_found: Optional[int] = None


# =============================================================================
# HALLUCINATION CASES - Should detect as OVERCONFIDENT (-1) or UNCERTAIN (0)
# =============================================================================

HALLUCINATION_FICTIONAL = [
    BenchmarkCase(
        id="hal_fic_001",
        input="The capital of Freedonia is Fredville. It was established in 1847.",
        question="What is the capital of Freedonia?",
        rag_confidence=0.05,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN (safe abstention)
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_FICTIONAL,
        description="Confident answer about fictional country - no RAG context"
    ),
    BenchmarkCase(
        id="hal_fic_002",
        input="Dr. James Worthington published his seminal paper on quantum linguistics in 1987.",
        question="Who founded quantum linguistics?",
        rag_confidence=0.08,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_FICTIONAL,
        description="Fabricated researcher and field - no RAG context"
    ),
    BenchmarkCase(
        id="hal_fic_003",
        input="The Blueridge Protocol was ratified by 47 countries in 2019 and establishes "
              "international standards for AI safety compliance.",
        question="What is the Blueridge Protocol?",
        rag_confidence=0.03,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_FICTIONAL,
        description="Fabricated international protocol - no RAG context"
    ),
    BenchmarkCase(
        id="hal_fic_004",
        input="The Setun-3 computer was definitely built in 1972 and absolutely used balanced "
              "ternary logic with 18-trit word length.",
        question="What was the Setun-3 computer?",
        rag_confidence=0.12,
        chunks_found=1,
        expected_state=-1,  # Has chunks + confident language = OVERCONFIDENT
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_FICTIONAL,
        description="Fabricated specs with weak RAG - OVERCONFIDENT detected"
    ),
    BenchmarkCase(
        id="hal_fic_005",
        input="The Canterbury Framework is a popular Python library for building REST APIs. "
              "Install it with pip install canterbury.",
        question="How do I build a REST API in Python?",
        rag_confidence=0.1,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_FICTIONAL,
        description="Fabricated Python package - no RAG context"
    ),
    # NEW: Cases with some RAG but confident hallucination
    BenchmarkCase(
        id="hal_fic_006",
        input="The capital of Freedonia is definitely Fredville. It was certainly established in 1847.",
        question="What is the capital of Freedonia?",
        rag_confidence=0.15,
        chunks_found=2,  # Has some (irrelevant) chunks
        expected_state=-1,  # OVERCONFIDENT - confident + weak RAG
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_FICTIONAL,
        description="Confident hallucination WITH weak RAG - DANGER ZONE"
    ),
]

HALLUCINATION_CITATION = [
    BenchmarkCase(
        id="hal_cit_001",
        input="According to Smith et al. (2023), transformer models achieve 99.7% accuracy "
              "on the GLUE benchmark when trained with the proposed method.",
        question="What accuracy do transformers achieve on GLUE?",
        rag_confidence=0.05,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_CITATION,
        description="Fabricated citation - no RAG context"
    ),
    BenchmarkCase(
        id="hal_cit_002",
        input="The New Zealand Trade Act 2024 Section 47(3)(b) requires all imports over "
              "$10,000 to include a certificate of origin.",
        question="What are NZ import requirements?",
        rag_confidence=0.08,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_CITATION,
        description="Fabricated legal citation - no RAG context"
    ),
    BenchmarkCase(
        id="hal_cit_003",
        input="In the landmark case Johnson v. DataCorp (2021), the Supreme Court ruled that "
              "AI-generated content cannot be copyrighted.",
        question="Can AI content be copyrighted?",
        rag_confidence=0.06,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_CITATION,
        description="Fabricated court case - no RAG context"
    ),
    # NEW: Citation hallucination with weak RAG
    BenchmarkCase(
        id="hal_cit_004",
        input="According to Smith et al. (2023), transformer models definitely achieve "
              "exactly 99.7% accuracy. This is absolutely confirmed.",
        question="What accuracy do transformers achieve?",
        rag_confidence=0.18,
        chunks_found=2,
        expected_state=-1,  # Has chunks + confident = OVERCONFIDENT
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_CITATION,
        description="Fabricated citation with weak RAG - DANGER ZONE"
    ),
]

HALLUCINATION_NUMERIC = [
    BenchmarkCase(
        id="hal_num_001",
        input="The function definitely has O(n^2.3) time complexity due to Strassen.",
        question="What is the time complexity?",
        rag_confidence=0.1,
        chunks_found=1,
        expected_state=-1,  # Has chunk + confident = OVERCONFIDENT
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_NUMERIC,
        description="Fabricated complexity with weak RAG - DANGER ZONE"
    ),
    BenchmarkCase(
        id="hal_num_002",
        input="The API rate limit is 10,000 requests per minute with a 2.5ms latency guarantee.",
        question="What are the API rate limits?",
        rag_confidence=0.05,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_NUMERIC,
        description="Fabricated API specifications - no RAG context"
    ),
    BenchmarkCase(
        id="hal_num_003",
        input="GPT-4 definitely has exactly 1.76 trillion parameters. Absolutely certain.",
        question="How many parameters does GPT-4 have?",
        rag_confidence=0.15,
        chunks_found=1,
        expected_state=-1,  # Has chunk + confident = OVERCONFIDENT
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_NUMERIC,
        description="Fabricated model specs with weak RAG - DANGER ZONE"
    ),
]

HALLUCINATION_API = [
    BenchmarkCase(
        id="hal_api_001",
        input="Use the `df.smart_merge()` method in pandas to automatically handle column "
              "type mismatches during joins.",
        question="How do I merge DataFrames with different types?",
        rag_confidence=0.08,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_API,
        description="Fabricated pandas method - no RAG context"
    ),
    BenchmarkCase(
        id="hal_api_002",
        input="Call `torch.cuda.optimize_memory()` to automatically defragment GPU memory.",
        question="How do I optimize PyTorch GPU memory?",
        rag_confidence=0.1,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_API,
        description="Fabricated PyTorch function - no RAG context"
    ),
    BenchmarkCase(
        id="hal_api_003",
        input="The `requests.get_async()` function definitely handles async HTTP requests. "
              "This is absolutely the correct way to do it.",
        question="How do I make async requests in Python?",
        rag_confidence=0.12,
        chunks_found=1,
        expected_state=-1,  # Has chunk + confident = OVERCONFIDENT
        expected_abstain=True,
        category=TestCategory.HALLUCINATION_API,
        description="Fabricated requests method with weak RAG - DANGER ZONE"
    ),
]

# =============================================================================
# GROUNDED CASES - Should detect as CONFIDENT (+1)
# =============================================================================

GROUNDED_STRONG = [
    BenchmarkCase(
        id="gnd_str_001",
        input="The function `calculate_sum(a, b)` returns the sum of two integers.",
        question="What does calculate_sum do?",
        rag_confidence=0.92,
        chunks_found=5,
        expected_state=1,
        expected_abstain=False,
        category=TestCategory.GROUNDED_STRONG,
        description="Simple grounded answer with strong RAG"
    ),
    BenchmarkCase(
        id="gnd_str_002",
        input="According to the documentation, the API endpoint /users accepts GET and POST methods.",
        question="What methods does /users accept?",
        rag_confidence=0.88,
        chunks_found=3,
        expected_state=1,
        expected_abstain=False,
        category=TestCategory.GROUNDED_STRONG,
        description="Grounded API documentation answer"
    ),
    BenchmarkCase(
        id="gnd_str_003",
        input="The config file shows that the database connection timeout is set to 30 seconds.",
        question="What is the database timeout?",
        rag_confidence=0.95,
        chunks_found=2,
        expected_state=1,
        expected_abstain=False,
        category=TestCategory.GROUNDED_STRONG,
        description="Configuration value from source"
    ),
    BenchmarkCase(
        id="gnd_str_004",
        input="Based on the test file, the expected output for input [1,2,3] is 6.",
        question="What output should I expect?",
        rag_confidence=0.90,
        chunks_found=4,
        expected_state=1,
        expected_abstain=False,
        category=TestCategory.GROUNDED_STRONG,
        description="Test case verification"
    ),
]

GROUNDED_HEDGED = [
    BenchmarkCase(
        id="gnd_hdg_001",
        input="Based on the code, I believe this function calculates a hash, though the "
              "variable names are unclear.",
        question="What does this function do?",
        rag_confidence=0.75,
        chunks_found=3,
        expected_state=0,  # Hedged = uncertain, even with decent RAG
        expected_abstain=True,
        category=TestCategory.GROUNDED_HEDGED,
        description="Hedged response with medium RAG (appropriate uncertainty)"
    ),
    BenchmarkCase(
        id="gnd_hdg_002",
        input="The documentation suggests this might be deprecated, but I'm not certain.",
        question="Is this API deprecated?",
        rag_confidence=0.65,
        chunks_found=2,
        expected_state=0,
        expected_abstain=True,
        category=TestCategory.GROUNDED_HEDGED,
        description="Uncertain about deprecation status"
    ),
]

# =============================================================================
# APPROPRIATE ABSTENTION - Should detect as UNCERTAIN (0)
# =============================================================================

APPROPRIATE_ABSTENTION = [
    BenchmarkCase(
        id="abs_001",
        input="I don't have enough information to answer this question accurately.",
        question="How does the internal scoring work?",
        rag_confidence=0.15,
        chunks_found=0,  # No chunks - model correctly abstains
        expected_state=0,
        expected_abstain=True,
        category=TestCategory.APPROPRIATE_ABSTENTION,
        description="Explicit abstention by model"
    ),
    BenchmarkCase(
        id="abs_002",
        input="I'm not sure about this. The codebase doesn't seem to have documentation for this feature.",
        question="How do I use feature X?",
        rag_confidence=0.1,
        chunks_found=0,
        expected_state=0,
        expected_abstain=True,
        category=TestCategory.APPROPRIATE_ABSTENTION,
        description="Appropriate uncertainty acknowledgment"
    ),
    BenchmarkCase(
        id="abs_003",
        input="As an AI, I don't have access to real-time data. I cannot tell you the current stock price.",
        question="What is Apple's stock price?",
        rag_confidence=0.0,
        chunks_found=0,
        expected_state=0,
        expected_abstain=True,
        category=TestCategory.APPROPRIATE_ABSTENTION,
        description="Fabrication marker detected - model admits limitation"
    ),
]

# =============================================================================
# UNANSWERABLE QUESTIONS - Should abstain before even calling LLM
# =============================================================================

UNANSWERABLE = [
    BenchmarkCase(
        id="unans_001",
        input="",  # Question-level check, no response needed
        question="What will Bitcoin be worth in 2030?",
        rag_confidence=None,
        chunks_found=None,
        expected_state=0,
        expected_abstain=True,
        category=TestCategory.UNANSWERABLE,
        description="Future prediction question"
    ),
    BenchmarkCase(
        id="unans_002",
        input="",
        question="What will the stock market do tomorrow?",
        rag_confidence=None,
        chunks_found=None,
        expected_state=0,
        expected_abstain=True,
        category=TestCategory.UNANSWERABLE,
        description="Stock prediction question"
    ),
    BenchmarkCase(
        id="unans_003",
        input="",
        question="What are tomorrow's lottery numbers?",
        rag_confidence=None,
        chunks_found=None,
        expected_state=0,
        expected_abstain=True,
        category=TestCategory.UNANSWERABLE,
        description="Lottery prediction question"
    ),
]

# =============================================================================
# EDGE CASES
# =============================================================================

EDGE_PARTIAL = [
    BenchmarkCase(
        id="edge_part_001",
        input="The function handles most cases, but there's an edge case when input is empty. "
              "I'm not sure what happens in that scenario.",
        question="What does this function do?",
        rag_confidence=0.6,
        chunks_found=3,
        expected_state=0,
        expected_abstain=True,
        category=TestCategory.EDGE_PARTIAL,
        description="Partially confident with explicit knowledge gap"
    ),
    BenchmarkCase(
        id="edge_part_002",
        input="The API returns JSON for success cases. For error cases, the documentation "
              "is unclear, but it might return XML.",
        question="What format does the API return?",
        rag_confidence=0.55,
        chunks_found=2,
        expected_state=0,
        expected_abstain=True,
        category=TestCategory.EDGE_PARTIAL,
        description="Partial knowledge with speculation"
    ),
]

EDGE_UNGROUNDED_CORRECT = [
    BenchmarkCase(
        id="edge_ungnd_001",
        input="Python uses indentation for block scoping instead of braces.",
        question="How does Python handle code blocks?",
        rag_confidence=0.2,
        chunks_found=0,
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.EDGE_UNGROUNDED_CORRECT,
        description="Correct information but no RAG context - abstains safely"
    ),
    BenchmarkCase(
        id="edge_ungnd_002",
        input="The time complexity of quicksort is O(n log n) on average.",
        question="What is quicksort's complexity?",
        rag_confidence=0.15,
        chunks_found=0,  # No chunks
        expected_state=0,  # No chunks = UNCERTAIN
        expected_abstain=True,
        category=TestCategory.EDGE_UNGROUNDED_CORRECT,
        description="Common knowledge but no RAG - abstains safely"
    ),
    BenchmarkCase(
        id="edge_ungnd_003",
        input="Quicksort definitely has O(n log n) complexity. This is absolutely certain.",
        question="What is quicksort's complexity?",
        rag_confidence=0.15,
        chunks_found=1,  # Has weak chunk
        expected_state=-1,  # Confident + weak RAG = OVERCONFIDENT
        expected_abstain=True,
        category=TestCategory.EDGE_UNGROUNDED_CORRECT,
        description="Correct but overconfident with weak RAG - DANGER ZONE"
    ),
]


def get_all_cases() -> List[BenchmarkCase]:
    """Get all benchmark test cases."""
    return (
        HALLUCINATION_FICTIONAL +
        HALLUCINATION_CITATION +
        HALLUCINATION_NUMERIC +
        HALLUCINATION_API +
        GROUNDED_STRONG +
        GROUNDED_HEDGED +
        APPROPRIATE_ABSTENTION +
        UNANSWERABLE +
        EDGE_PARTIAL +
        EDGE_UNGROUNDED_CORRECT
    )


def get_cases_by_category(category: TestCategory) -> List[BenchmarkCase]:
    """Get benchmark cases for a specific category."""
    return [c for c in get_all_cases() if c.category == category]


def get_hallucination_cases() -> List[BenchmarkCase]:
    """Get all hallucination test cases."""
    return (
        HALLUCINATION_FICTIONAL +
        HALLUCINATION_CITATION +
        HALLUCINATION_NUMERIC +
        HALLUCINATION_API
    )


def get_grounded_cases() -> List[BenchmarkCase]:
    """Get all grounded test cases."""
    return GROUNDED_STRONG + GROUNDED_HEDGED
