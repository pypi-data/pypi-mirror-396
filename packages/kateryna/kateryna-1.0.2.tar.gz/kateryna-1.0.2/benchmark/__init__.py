# Kateryna Benchmark Suite
# Hallucination detection benchmarks for epistemic ternary logic

from .datasets import (
    BenchmarkCase,
    TestCategory,
    get_all_cases,
    get_cases_by_category,
    get_hallucination_cases,
    get_grounded_cases,
)
from .runner import BenchmarkRunner, BenchmarkReport, print_report, export_report

__all__ = [
    "BenchmarkCase",
    "TestCategory",
    "get_all_cases",
    "get_cases_by_category",
    "get_hallucination_cases",
    "get_grounded_cases",
    "BenchmarkRunner",
    "BenchmarkReport",
    "print_report",
    "export_report",
]

# Premium features available in kateryna-pro:
# - live_runner: Test against real LLMs (OpenAI, Anthropic, Ollama)
# - rag_test_runner: Test with RAG context simulation
# - doc_scanner: Scan documentation to find hallucination-prone areas
