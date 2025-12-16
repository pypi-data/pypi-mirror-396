# -*- coding: utf-8 -*-
"""
Kateryna Comprehensive Accuracy Tests
======================================

Extended test suite for validating detector accuracy across:
1. Threshold boundaries
2. Linguistic marker coverage
3. Response length stress tests
4. Real-world hallucination patterns
5. Confusion matrix analysis
"""

from kateryna import EpistemicDetector, TernaryState


def run_comprehensive_tests():
    detector = EpistemicDetector()
    all_results = []

    # =========================================================================
    # 1. THRESHOLD BOUNDARY TESTS
    # =========================================================================
    print("=" * 70)
    print("1. THRESHOLD BOUNDARY TESTS")
    print("=" * 70)

    boundary_tests = [
        # Around uncertain threshold (0.3)
        {"text": "The answer is X.", "rag": 0.29, "chunks": 3, "expect": 0, "name": "Just below uncertain threshold"},
        {"text": "The answer is X.", "rag": 0.30, "chunks": 3, "expect": 1, "name": "At uncertain threshold"},
        {"text": "The answer is X.", "rag": 0.31, "chunks": 3, "expect": 1, "name": "Just above uncertain threshold"},
        # Around confident threshold (0.7)
        {"text": "The answer is X.", "rag": 0.69, "chunks": 3, "expect": 1, "name": "Just below confident threshold"},
        {"text": "The answer is X.", "rag": 0.70, "chunks": 3, "expect": 1, "name": "At confident threshold"},
        {"text": "The answer is X.", "rag": 0.71, "chunks": 3, "expect": 1, "name": "Just above confident threshold"},
        # Extremes
        {"text": "The answer is X.", "rag": 0.0, "chunks": 3, "expect": 0, "name": "Zero RAG confidence"},
        {"text": "The answer is X.", "rag": 1.0, "chunks": 3, "expect": 1, "name": "Perfect RAG confidence"},
        {"text": "The answer is definitely X.", "rag": 0.01, "chunks": 1, "expect": -1, "name": "Near-zero RAG + confident"},
    ]

    for t in boundary_tests:
        state = detector.analyze(t["text"], "", t["rag"], t["chunks"])
        passed = state.state.value == t["expect"]
        all_results.append(passed)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {t['name']}: RAG={t['rag']}, expect={t['expect']}, got={state.state.value}")

    # =========================================================================
    # 2. LINGUISTIC MARKER COVERAGE
    # =========================================================================
    print()
    print("=" * 70)
    print("2. LINGUISTIC MARKER COVERAGE")
    print("=" * 70)

    # Test each uncertainty marker
    uncertainty_phrases = [
        "I'm not sure about this.",
        "I don't know the answer.",
        "I think it might be X.",
        "Maybe it's X.",
        "Perhaps the answer is X.",
        "It might be X.",
        "It could be X.",
        "It's possibly X.",
        "I'm uncertain about this.",
        "I'm not certain.",
        "I believe it's X.",
        "It seems to be X.",
        "It's probably X.",
        "It's likely X.",
        "It's unlikely to be Y.",
        "It's unclear.",
        "If I recall correctly, it's X.",
        "It appears to be X.",
    ]

    unc_pass = 0
    unc_fail = []
    for phrase in uncertainty_phrases:
        state = detector.analyze(phrase, "", 0.5, 3)
        passed = state.state == TernaryState.UNCERTAIN
        unc_pass += 1 if passed else 0
        all_results.append(passed)
        if not passed:
            unc_fail.append(f'  "{phrase[:40]}..." -> {state.state.name}')

    print(f"Uncertainty markers: {unc_pass}/{len(uncertainty_phrases)} detected")
    for fail in unc_fail:
        print(f"[FAIL] {fail}")

    # Test each overconfidence marker
    overconfidence_phrases = [
        "It's definitely X.",
        "It's certainly X.",
        "With certainty, it's X.",
        "I'm certain it's X.",
        "It's absolutely X.",
        "It's always X.",
        "It's never Y.",
        "It's undoubtedly X.",
        "It's clearly X.",
        "It's obviously X.",
        "Without a doubt, it's X.",
        "It's guaranteed to be X.",
        "It's 100% X.",
        "It must be X.",
        "No question, it's X.",
        "It's exactly X.",
        "It's precisely X.",
    ]

    over_pass = 0
    over_fail = []
    for phrase in overconfidence_phrases:
        state = detector.analyze(phrase, "", 0.1, 1)  # Weak RAG
        passed = state.state == TernaryState.OVERCONFIDENT
        over_pass += 1 if passed else 0
        all_results.append(passed)
        if not passed:
            over_fail.append(f'  "{phrase[:40]}..." -> {state.state.name}')

    print(f"Overconfidence markers (weak RAG): {over_pass}/{len(overconfidence_phrases)} detected")
    for fail in over_fail:
        print(f"[FAIL] {fail}")

    # =========================================================================
    # 3. RESPONSE LENGTH STRESS TESTS
    # =========================================================================
    print()
    print("=" * 70)
    print("3. RESPONSE LENGTH STRESS TESTS")
    print("=" * 70)

    length_tests = [
        {"text": "X", "rag": 0.8, "chunks": 5, "expect": 0, "name": "Single character"},
        {"text": "OK", "rag": 0.8, "chunks": 5, "expect": 0, "name": "Two characters"},
        {"text": "Yes", "rag": 0.8, "chunks": 5, "expect": 0, "name": "Three characters (trivial)"},
        {"text": "The answer is X.", "rag": 0.8, "chunks": 5, "expect": 1, "name": "Short response"},
        {"text": "The answer is X. " * 100, "rag": 0.8, "chunks": 5, "expect": 1, "name": "Long repetitive (1700 chars)"},
        {"text": "I think " * 50 + "maybe it is X.", "rag": 0.8, "chunks": 5, "expect": 0, "name": "Extreme hedging (50x)"},
        {"text": "Definitely " * 20 + "the answer is X.", "rag": 0.1, "chunks": 1, "expect": -1, "name": "Extreme overconfidence (weak RAG)"},
    ]

    for t in length_tests:
        state = detector.analyze(t["text"], "", t["rag"], t["chunks"])
        passed = state.state.value == t["expect"]
        all_results.append(passed)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {t['name']}: expect={t['expect']}, got={state.state.value}")

    # =========================================================================
    # 4. REAL-WORLD HALLUCINATION PATTERNS
    # =========================================================================
    print()
    print("=" * 70)
    print("4. REAL-WORLD HALLUCINATION PATTERNS")
    print("=" * 70)

    hallucination_patterns = [
        # Fake APIs
        {"text": "Use pandas.smart_merge() to combine dataframes efficiently.", "rag": 0.05, "chunks": 1, "expect": 0, "name": "Fake pandas API"},
        {"text": "The torch.quantum_compute() function handles this.", "rag": 0.08, "chunks": 1, "expect": 0, "name": "Fake PyTorch API"},
        # Fake citations with confidence markers
        {"text": "According to Smith et al. (2023), this approach is definitely optimal.", "rag": 0.1, "chunks": 1, "expect": -1, "name": "Fake citation + definitely"},
        {"text": "The seminal work by Johnson (2022) proves this conclusively.", "rag": 0.05, "chunks": 0, "expect": 0, "name": "Fake citation, no chunks"},
        # Fake statistics
        {"text": "Studies show that exactly 73.2% of developers prefer this approach.", "rag": 0.12, "chunks": 1, "expect": -1, "name": "Fake precise statistic"},
        {"text": "Research indicates approximately 70% use this method.", "rag": 0.4, "chunks": 2, "expect": 1, "name": "Hedged statistic + medium RAG"},
        # Fictional entities
        {"text": "The Blueridge Protocol ensures quantum-safe encryption.", "rag": 0.02, "chunks": 0, "expect": 0, "name": "Fictional protocol, no chunks"},
        {"text": "Microsoft definitely announced the Azure Quantum Bridge.", "rag": 0.08, "chunks": 1, "expect": -1, "name": "Fictional service + definitely"},
        # Date/version hallucinations
        {"text": "Python 4.0 was released on March 15, 2024.", "rag": 0.0, "chunks": 0, "expect": 0, "name": "Fake release date"},
        {"text": "GPT-5 definitely has exactly 500 trillion parameters.", "rag": 0.05, "chunks": 1, "expect": -1, "name": "Fake model specs + definitely"},
        # Code hallucinations
        {"text": "The function uses the deprecated __future_async__ decorator.", "rag": 0.03, "chunks": 1, "expect": 0, "name": "Fake decorator"},
        {"text": "This definitely implements the O(1) quantum sorting algorithm.", "rag": 0.02, "chunks": 1, "expect": -1, "name": "Fake algorithm + definitely"},
    ]

    for t in hallucination_patterns:
        state = detector.analyze(t["text"], "", t["rag"], t["chunks"])
        passed = state.state.value == t["expect"]
        all_results.append(passed)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {t['name']}: expect={t['expect']}, got={state.state.value}")

    # =========================================================================
    # 5. GROUNDED RESPONSE TESTS (should NOT trigger false positives)
    # =========================================================================
    print()
    print("=" * 70)
    print("5. GROUNDED RESPONSES (false positive check)")
    print("=" * 70)

    grounded_tests = [
        {"text": "The function adds two numbers and returns the sum.", "rag": 0.92, "chunks": 5, "expect": 1, "name": "Simple grounded answer"},
        {"text": "According to the documentation on line 45, this handles errors.", "rag": 0.88, "chunks": 4, "expect": 1, "name": "Doc reference + strong RAG"},
        {"text": "The API returns a JSON object with status and data fields.", "rag": 0.85, "chunks": 6, "expect": 1, "name": "Technical answer + strong RAG"},
        {"text": "This is definitely correct based on the source code.", "rag": 0.95, "chunks": 8, "expect": 1, "name": "Confident + very strong RAG"},
        {"text": "The test passes with 100% coverage.", "rag": 0.90, "chunks": 5, "expect": 1, "name": "100% in grounded context"},
        {"text": "It always returns true for valid inputs.", "rag": 0.88, "chunks": 4, "expect": 1, "name": "'always' in grounded context"},
    ]

    for t in grounded_tests:
        state = detector.analyze(t["text"], "", t["rag"], t["chunks"])
        passed = state.state.value == t["expect"]
        all_results.append(passed)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {t['name']}: expect={t['expect']}, got={state.state.value}")

    # =========================================================================
    # 6. CONFUSION MATRIX
    # =========================================================================
    print()
    print("=" * 70)
    print("6. CONFUSION MATRIX (3x3)")
    print("=" * 70)

    confusion_cases = []

    # True CONFIDENT cases
    for i in range(10):
        confusion_cases.append({"text": f"The function returns the sum of inputs (case {i}).", "rag": 0.85, "chunks": 5, "true": 1})

    # True UNCERTAIN cases
    for i in range(10):
        confusion_cases.append({"text": f"I think it might be related to sorting (case {i}), but I am not sure.", "rag": 0.5, "chunks": 3, "true": 0})

    # True OVERCONFIDENT cases
    for i in range(10):
        confusion_cases.append({"text": f"This is definitely the correct implementation (case {i}) with 100% accuracy.", "rag": 0.1, "chunks": 1, "true": -1})

    matrix = {1: {1: 0, 0: 0, -1: 0}, 0: {1: 0, 0: 0, -1: 0}, -1: {1: 0, 0: 0, -1: 0}}

    for c in confusion_cases:
        state = detector.analyze(c["text"], "", c["rag"], c["chunks"])
        pred = state.state.value
        true = c["true"]
        matrix[true][pred] += 1
        all_results.append(pred == true)

    print()
    print("                    Predicted")
    print("                 +1     0    -1")
    print(f"True +1 (CONF)   {matrix[1][1]:3d}   {matrix[1][0]:3d}   {matrix[1][-1]:3d}")
    print(f"True  0 (UNCR)   {matrix[0][1]:3d}   {matrix[0][0]:3d}   {matrix[0][-1]:3d}")
    print(f"True -1 (OVER)   {matrix[-1][1]:3d}   {matrix[-1][0]:3d}   {matrix[-1][-1]:3d}")

    # Calculate per-class metrics
    print()
    for label, name in [(1, "CONFIDENT"), (0, "UNCERTAIN"), (-1, "OVERCONFIDENT")]:
        tp = matrix[label][label]
        fp = sum(matrix[other][label] for other in [1, 0, -1] if other != label)
        fn = sum(matrix[label][other] for other in [1, 0, -1] if other != label)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        print(f"{name:13s} - Precision: {precision:.0%}, Recall: {recall:.0%}, F1: {f1:.0%}")

    # =========================================================================
    # 7. EDGE CASES
    # =========================================================================
    print()
    print("=" * 70)
    print("7. EDGE CASES")
    print("=" * 70)

    edge_cases = [
        {"text": "", "rag": 0.9, "chunks": 5, "expect": 0, "name": "Empty string"},
        {"text": "   ", "rag": 0.9, "chunks": 5, "expect": 0, "name": "Whitespace only"},
        {"text": "\n\n\n", "rag": 0.9, "chunks": 5, "expect": 0, "name": "Newlines only"},
        {"text": "..." , "rag": 0.9, "chunks": 5, "expect": 0, "name": "Ellipsis only"},
        {"text": "The answer.", "rag": None, "chunks": None, "expect": 1, "name": "No RAG context at all"},
        {"text": "I think maybe.", "rag": None, "chunks": None, "expect": 0, "name": "Hedging, no RAG context"},
        {"text": "a" * 10000, "rag": 0.8, "chunks": 5, "expect": 1, "name": "10K character response"},
        {"text": "def add(a,b): return a+b", "rag": 0.9, "chunks": 5, "expect": 1, "name": "Code snippet"},
        {"text": '{"result": "success", "value": 42}', "rag": 0.9, "chunks": 5, "expect": 1, "name": "JSON response"},
    ]

    for t in edge_cases:
        state = detector.analyze(t["text"], "", t["rag"], t["chunks"])
        passed = state.state.value == t["expect"]
        all_results.append(passed)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {t['name']}: expect={t['expect']}, got={state.state.value}")

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print()
    print("=" * 70)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    total = len(all_results)
    passed = sum(all_results)
    failed = total - passed
    print(f"Total Tests:  {total}")
    print(f"Passed:       {passed}")
    print(f"Failed:       {failed}")
    print(f"Accuracy:     {passed/total:.1%}")
    print("=" * 70)

    return passed, total


if __name__ == "__main__":
    run_comprehensive_tests()
