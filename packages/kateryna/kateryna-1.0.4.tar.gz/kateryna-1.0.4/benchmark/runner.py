# -*- coding: utf-8 -*-
"""
Kateryna Benchmark Runner
=========================

Runs the benchmark suite against the EpistemicDetector and produces
metrics for validating hallucination detection accuracy.

Usage:
    python -m benchmark.runner
    python -m benchmark.runner --verbose
    python -m benchmark.runner --category hallucination_fictional

DOI: 10.5281/zenodo.17875182
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from kateryna import EpistemicDetector, TernaryState

from .datasets import (
    BenchmarkCase,
    TestCategory,
    get_all_cases,
    get_cases_by_category,
)


@dataclass
class TestResult:
    """Result of a single benchmark test."""
    case_id: str
    passed: bool
    expected_state: int
    actual_state: int
    expected_abstain: bool
    actual_abstain: bool
    state_correct: bool
    abstain_correct: bool
    confidence: float
    reason: str
    category: TestCategory
    description: str


@dataclass
class CategoryMetrics:
    """Metrics for a test category."""
    total: int = 0
    passed: int = 0
    state_correct: int = 0
    abstain_correct: int = 0

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0

    @property
    def state_accuracy(self) -> float:
        return self.state_correct / self.total if self.total > 0 else 0.0

    @property
    def abstain_accuracy(self) -> float:
        return self.abstain_correct / self.total if self.total > 0 else 0.0


@dataclass
class BenchmarkReport:
    """Full benchmark report."""
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    pass_rate: float

    # Precision/Recall for -1 (OVERCONFIDENT) detection
    overconfident_precision: float
    overconfident_recall: float
    overconfident_f1: float

    # Precision/Recall for abstention
    abstention_precision: float
    abstention_recall: float
    abstention_f1: float

    # Per-category metrics
    category_metrics: Dict[str, CategoryMetrics] = field(default_factory=dict)

    # Individual results
    results: List[TestResult] = field(default_factory=list)
    failed_cases: List[TestResult] = field(default_factory=list)


class BenchmarkRunner:
    """
    Runs benchmark tests against EpistemicDetector.

    Produces metrics including:
    - Overall pass rate
    - Precision/Recall for -1 (OVERCONFIDENT) state detection
    - Per-category breakdown
    """

    def __init__(self, detector: Optional[EpistemicDetector] = None, verbose: bool = False):
        self.detector = detector or EpistemicDetector()
        self.verbose = verbose

    def run_case(self, case: BenchmarkCase) -> TestResult:
        """Run a single benchmark case."""

        # Handle unanswerable question pre-check
        if case.category == TestCategory.UNANSWERABLE:
            should_abstain, reason = self.detector.should_abstain_on_question(case.question)
            return TestResult(
                case_id=case.id,
                passed=should_abstain == case.expected_abstain,
                expected_state=case.expected_state,
                actual_state=0 if should_abstain else 1,
                expected_abstain=case.expected_abstain,
                actual_abstain=should_abstain,
                state_correct=should_abstain == (case.expected_state == 0),
                abstain_correct=should_abstain == case.expected_abstain,
                confidence=0.0 if should_abstain else 1.0,
                reason=reason or "Question passed pre-check",
                category=case.category,
                description=case.description,
            )

        # Run normal analysis
        state = self.detector.analyze(
            text=case.input,
            question=case.question,
            retrieval_confidence=case.rag_confidence,
            chunks_found=case.chunks_found,
        )

        actual_state_value = state.state.value
        state_correct = actual_state_value == case.expected_state
        abstain_correct = state.should_abstain == case.expected_abstain

        # A test passes if BOTH state and abstain are correct
        passed = state_correct and abstain_correct

        return TestResult(
            case_id=case.id,
            passed=passed,
            expected_state=case.expected_state,
            actual_state=actual_state_value,
            expected_abstain=case.expected_abstain,
            actual_abstain=state.should_abstain,
            state_correct=state_correct,
            abstain_correct=abstain_correct,
            confidence=state.confidence,
            reason=state.reason,
            category=case.category,
            description=case.description,
        )

    def run_all(self, cases: Optional[List[BenchmarkCase]] = None) -> BenchmarkReport:
        """Run all benchmark cases and produce report."""

        if cases is None:
            cases = get_all_cases()

        results: List[TestResult] = []
        failed_cases: List[TestResult] = []
        category_metrics: Dict[str, CategoryMetrics] = {}

        # Confusion matrix for OVERCONFIDENT (-1)
        overconf_tp = 0  # Expected -1, got -1
        overconf_fp = 0  # Expected not -1, got -1
        overconf_fn = 0  # Expected -1, got not -1

        # Confusion matrix for abstention
        abstain_tp = 0
        abstain_fp = 0
        abstain_fn = 0

        for case in cases:
            result = self.run_case(case)
            results.append(result)

            if not result.passed:
                failed_cases.append(result)

            # Update category metrics
            cat_key = case.category.value
            if cat_key not in category_metrics:
                category_metrics[cat_key] = CategoryMetrics()

            category_metrics[cat_key].total += 1
            if result.passed:
                category_metrics[cat_key].passed += 1
            if result.state_correct:
                category_metrics[cat_key].state_correct += 1
            if result.abstain_correct:
                category_metrics[cat_key].abstain_correct += 1

            # Update OVERCONFIDENT confusion matrix
            if case.expected_state == -1:
                if result.actual_state == -1:
                    overconf_tp += 1
                else:
                    overconf_fn += 1
            else:
                if result.actual_state == -1:
                    overconf_fp += 1

            # Update abstention confusion matrix
            if case.expected_abstain:
                if result.actual_abstain:
                    abstain_tp += 1
                else:
                    abstain_fn += 1
            else:
                if result.actual_abstain:
                    abstain_fp += 1

            if self.verbose:
                status = "PASS" if result.passed else "FAIL"
                print(f"[{status}] {case.id}: {case.description}")
                if not result.passed:
                    print(f"       Expected: state={case.expected_state}, abstain={case.expected_abstain}")
                    print(f"       Got:      state={result.actual_state}, abstain={result.actual_abstain}")
                    print(f"       Reason:   {result.reason}")

        # Calculate metrics
        total = len(results)
        passed = sum(1 for r in results if r.passed)

        overconf_precision = overconf_tp / (overconf_tp + overconf_fp) if (overconf_tp + overconf_fp) > 0 else 0.0
        overconf_recall = overconf_tp / (overconf_tp + overconf_fn) if (overconf_tp + overconf_fn) > 0 else 0.0
        overconf_f1 = 2 * overconf_precision * overconf_recall / (overconf_precision + overconf_recall) if (overconf_precision + overconf_recall) > 0 else 0.0

        abstain_precision = abstain_tp / (abstain_tp + abstain_fp) if (abstain_tp + abstain_fp) > 0 else 0.0
        abstain_recall = abstain_tp / (abstain_tp + abstain_fn) if (abstain_tp + abstain_fn) > 0 else 0.0
        abstain_f1 = 2 * abstain_precision * abstain_recall / (abstain_precision + abstain_recall) if (abstain_precision + abstain_recall) > 0 else 0.0

        return BenchmarkReport(
            timestamp=datetime.now().isoformat(),
            total_tests=total,
            passed=passed,
            failed=total - passed,
            pass_rate=passed / total if total > 0 else 0.0,
            overconfident_precision=overconf_precision,
            overconfident_recall=overconf_recall,
            overconfident_f1=overconf_f1,
            abstention_precision=abstain_precision,
            abstention_recall=abstain_recall,
            abstention_f1=abstain_f1,
            category_metrics=category_metrics,
            results=results,
            failed_cases=failed_cases,
        )

    def run_category(self, category: TestCategory) -> BenchmarkReport:
        """Run benchmark for a specific category."""
        cases = get_cases_by_category(category)
        return self.run_all(cases)


def print_report(report: BenchmarkReport, show_failures: bool = True):
    """Print a formatted benchmark report."""

    print("\n" + "=" * 70)
    print("                    KATERYNA BENCHMARK REPORT")
    print("=" * 70)
    print(f"Timestamp: {report.timestamp}")
    print()

    # Overall metrics
    print("OVERALL RESULTS")
    print("-" * 40)
    print(f"  Total Tests:    {report.total_tests}")
    print(f"  Passed:         {report.passed}")
    print(f"  Failed:         {report.failed}")
    print(f"  Pass Rate:      {report.pass_rate:.1%}")
    print()

    # OVERCONFIDENT (-1) detection metrics
    print("OVERCONFIDENT (-1) DETECTION (Hallucination Catching)")
    print("-" * 40)
    print(f"  Precision:      {report.overconfident_precision:.1%}")
    print(f"  Recall:         {report.overconfident_recall:.1%}")
    print(f"  F1 Score:       {report.overconfident_f1:.1%}")
    print()

    # Abstention metrics
    print("ABSTENTION ACCURACY")
    print("-" * 40)
    print(f"  Precision:      {report.abstention_precision:.1%}")
    print(f"  Recall:         {report.abstention_recall:.1%}")
    print(f"  F1 Score:       {report.abstention_f1:.1%}")
    print()

    # Per-category breakdown
    print("PER-CATEGORY BREAKDOWN")
    print("-" * 40)
    for cat_name, metrics in report.category_metrics.items():
        print(f"  {cat_name}:")
        print(f"    Pass Rate:     {metrics.pass_rate:.1%} ({metrics.passed}/{metrics.total})")
        print(f"    State Acc:     {metrics.state_accuracy:.1%}")
        print(f"    Abstain Acc:   {metrics.abstain_accuracy:.1%}")
    print()

    # Failed cases
    if show_failures and report.failed_cases:
        print("FAILED CASES")
        print("-" * 40)
        for result in report.failed_cases:
            print(f"  [{result.case_id}] {result.description}")
            print(f"    Expected: state={result.expected_state}, abstain={result.expected_abstain}")
            print(f"    Got:      state={result.actual_state}, abstain={result.actual_abstain}")
            print(f"    Reason:   {result.reason}")
            print()

    print("=" * 70)


def export_report(report: BenchmarkReport, path: Path):
    """Export report to JSON."""
    data = {
        "timestamp": report.timestamp,
        "total_tests": report.total_tests,
        "passed": report.passed,
        "failed": report.failed,
        "pass_rate": report.pass_rate,
        "overconfident_detection": {
            "precision": report.overconfident_precision,
            "recall": report.overconfident_recall,
            "f1": report.overconfident_f1,
        },
        "abstention": {
            "precision": report.abstention_precision,
            "recall": report.abstention_recall,
            "f1": report.abstention_f1,
        },
        "category_metrics": {
            name: {
                "total": m.total,
                "passed": m.passed,
                "pass_rate": m.pass_rate,
                "state_accuracy": m.state_accuracy,
                "abstain_accuracy": m.abstain_accuracy,
            }
            for name, m in report.category_metrics.items()
        },
        "failed_cases": [
            {
                "id": r.case_id,
                "description": r.description,
                "expected_state": r.expected_state,
                "actual_state": r.actual_state,
                "expected_abstain": r.expected_abstain,
                "actual_abstain": r.actual_abstain,
                "reason": r.reason,
            }
            for r in report.failed_cases
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Report exported to: {path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run Kateryna benchmark suite")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--category", type=str, help="Run specific category only")
    parser.add_argument("-o", "--output", type=str, help="Export JSON report to file")
    parser.add_argument("--no-failures", action="store_true", help="Don't show failed cases")

    args = parser.parse_args()

    runner = BenchmarkRunner(verbose=args.verbose)

    if args.category:
        try:
            category = TestCategory(args.category)
            report = runner.run_category(category)
        except ValueError:
            print(f"Unknown category: {args.category}")
            print(f"Valid categories: {[c.value for c in TestCategory]}")
            sys.exit(1)
    else:
        report = runner.run_all()

    print_report(report, show_failures=not args.no_failures)

    if args.output:
        export_report(report, Path(args.output))

    # Exit with error code if tests failed
    sys.exit(0 if report.failed == 0 else 1)


if __name__ == "__main__":
    main()
