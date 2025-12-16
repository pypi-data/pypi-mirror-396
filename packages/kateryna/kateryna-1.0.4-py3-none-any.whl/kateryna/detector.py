"""
Kateryna Detector - Epistemic Uncertainty Detection for LLMs
=============================================================

Detects uncertainty in LLM responses and cross-references with RAG
retrieval confidence to identify hallucination risk.

Key insight: confident language + weak retrieval = danger zone.

References:
    Brusentsov, N.P. (1960). An Electronic Calculating Machine Based on
        Ternary Code. Doklady Akademii Nauk SSSR.
    Lukasiewicz, J. (1920). On Three-Valued Logic. Ruch Filozoficzny.
"""

import re
from typing import Dict, Any, List, Optional, Tuple

from .state import EpistemicState, TernaryState
from .languages import get_markers, available_languages


def calculate_retrieval_confidence(chunks: List[Dict[str, Any]]) -> Tuple[float, int]:
    """
    Calculate aggregate confidence from RAG retrieval results.

    Uses rank-weighted mean of top chunks' relevance scores.
    Inspired by Setun: we need evidence to justify confidence.

    Args:
        chunks: List of retrieved chunks with 'distance', 'relevance', or 'score' keys

    Returns:
        (confidence_score, chunks_count) where confidence is 0.0-1.0

    Example:
        >>> chunks = [{'distance': 0.1}, {'distance': 0.2}]
        >>> confidence, count = calculate_retrieval_confidence(chunks)
        >>> print(f"{confidence:.0%} from {count} chunks")
        85% from 2 chunks
    """
    if not chunks:
        return 0.0, 0

    # Take top 5 chunks for confidence calculation
    top_chunks = chunks[:5]

    relevance_scores = []
    for chunk in top_chunks:
        # Handle various scoring formats from different vector DBs
        if 'relevance' in chunk and chunk['relevance'] is not None:
            relevance_scores.append(float(chunk['relevance']))
        elif 'distance' in chunk and chunk['distance'] is not None:
            # Convert distance to relevance (lower distance = higher relevance)
            relevance = max(0.0, min(1.0, 1.0 - float(chunk['distance'])))
            relevance_scores.append(relevance)
        elif 'score' in chunk and chunk['score'] is not None:
            # Normalize score if it's not in 0-1 range
            score = float(chunk['score'])
            if score > 1.0:
                score = min(1.0, score / 10.0)
            relevance_scores.append(score)
        elif 'similarity' in chunk and chunk['similarity'] is not None:
            relevance_scores.append(float(chunk['similarity']))

    if not relevance_scores:
        return 0.0, len(chunks)

    # Rank-weighted mean: first result counts more
    weights = [1.0 - (i * 0.15) for i in range(len(relevance_scores))]
    weighted_sum = sum(s * w for s, w in zip(relevance_scores, weights))
    total_weight = sum(weights)

    confidence = weighted_sum / total_weight if total_weight > 0 else 0.0

    return min(1.0, max(0.0, confidence)), len(chunks)


class EpistemicDetector:
    """
    Detects epistemic uncertainty in LLM responses.

    Uses linguistic markers and RAG retrieval confidence to determine
    if a response should be trusted or if the model should abstain.

    Implements Setun-inspired ternary logic:
    - CONFIDENT (+1): grounded in evidence
    - UNCERTAIN (0): abstain
    - OVERCONFIDENT (-1): potential hallucination (DANGER)

    The -1 state is the breakthrough. It catches confident bullshit.

    Example:
        >>> detector = EpistemicDetector()
        >>> state = detector.analyze(
        ...     "The answer is definitely 42.",
        ...     retrieval_confidence=0.15  # Low RAG confidence
        ... )
        >>> state.is_danger_zone
        True  # Confident response + weak grounding = hallucination risk

        >>> # German language support
        >>> detector_de = EpistemicDetector(language="de")
    """

    def __init__(
        self,
        language: str = "en",
        threshold_confident: float = 0.7,
        threshold_uncertain: float = 0.3,
        min_retrieval_confidence: float = 0.3,
        custom_markers: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialize the detector.

        Args:
            language: Language code for markers ("en", "de", etc.)
            threshold_confident: RAG confidence above this = likely confident
            threshold_uncertain: RAG confidence below this = uncertain
            min_retrieval_confidence: Minimum RAG confidence to trust a response
            custom_markers: Optional custom marker dict to override defaults
        """
        self.language = language
        self.threshold_confident = threshold_confident
        self.threshold_uncertain = threshold_uncertain
        self.min_retrieval_confidence = min_retrieval_confidence

        # Load markers from language pack or custom
        if custom_markers:
            markers = custom_markers
        else:
            markers = get_markers(language)

        # Compile regex patterns for performance
        self._uncertainty_patterns = [
            re.compile(p, re.IGNORECASE) for p in markers.get("uncertainty", [])
        ]
        self._overconfidence_patterns = [
            re.compile(p, re.IGNORECASE) for p in markers.get("overconfidence", [])
        ]
        self._fabrication_patterns = [
            re.compile(p, re.IGNORECASE) for p in markers.get("fabrication", [])
        ]
        self._unanswerable_patterns = [
            re.compile(p, re.IGNORECASE) for p in markers.get("unanswerable", [])
        ]

    def should_abstain_on_question(self, question: str) -> Tuple[bool, str]:
        """
        Quick check if a question should trigger abstention before calling the LLM.

        Saves tokens by catching unanswerable questions early.

        Args:
            question: The user's question

        Returns:
            (should_abstain, reason)

        Example:
            >>> detector = EpistemicDetector()
            >>> should_abstain, reason = detector.should_abstain_on_question(
            ...     "What will Bitcoin be worth in 2030?"
            ... )
            >>> should_abstain
            True
        """
        for pattern in self._unanswerable_patterns:
            if pattern.search(question.lower()):
                return True, "This question asks for predictions or unknowable information"
        return False, ""

    def analyze(
        self,
        text: str,
        question: str = "",
        retrieval_confidence: Optional[float] = None,
        chunks_found: Optional[int] = None
    ) -> EpistemicState:
        """
        Analyze text for epistemic uncertainty with optional RAG grounding.

        Implements Setun-inspired ternary logic:
        - RAG confidence takes precedence (no evidence = no trust)
        - Linguistic analysis provides secondary signals
        - Combined scoring determines final state

        The critical insight: High linguistic confidence + Low retrieval
        confidence = OVERCONFIDENT (-1) = DANGER ZONE

        Args:
            text: The LLM response to analyze
            question: Optional original question for context
            retrieval_confidence: Optional RAG retrieval confidence (0.0-1.0)
            chunks_found: Optional number of relevant chunks retrieved

        Returns:
            EpistemicState with ternary classification and grounding info

        Example:
            >>> detector = EpistemicDetector()
            >>> # Confident language + weak RAG = DANGER
            >>> state = detector.analyze(
            ...     "The capital of Freedonia is definitely Fredville.",
            ...     retrieval_confidence=0.05,
            ...     chunks_found=0
            ... )
            >>> state.is_danger_zone
            True
        """
        text_lower = text.lower().strip()
        markers_found = []

        # === EMPTY/TRIVIAL RESPONSE CHECK ===
        if len(text_lower) <= 3:
            return EpistemicState(
                state=TernaryState.UNCERTAIN,
                confidence=0.0,
                should_abstain=True,
                reason="Response is empty or trivial",
                markers_found=["empty_response"],
                retrieval_confidence=retrieval_confidence,
                chunks_found=chunks_found,
                grounded=False
            )

        # === LINGUISTIC ANALYSIS ===

        # Count uncertainty markers (good - model is being honest)
        uncertainty_count = 0
        for pattern in self._uncertainty_patterns:
            matches = pattern.findall(text_lower)
            if matches:
                uncertainty_count += len(matches)
                markers_found.extend(matches)

        # Count overconfidence markers (potentially bad)
        overconfidence_count = 0
        for pattern in self._overconfidence_patterns:
            if pattern.search(text_lower):
                overconfidence_count += 1

        # Check for fabrication markers
        fabrication_detected = False
        for pattern in self._fabrication_patterns:
            if pattern.search(text_lower):
                fabrication_detected = True
                markers_found.append("fabrication_marker")
                break

        # Check if question is inherently unanswerable
        unanswerable_question = False
        if question:
            for pattern in self._unanswerable_patterns:
                if pattern.search(question.lower()):
                    unanswerable_question = True
                    markers_found.append("unanswerable_question")
                    break

        # Calculate linguistic confidence (high = confident language)
        text_length = len(text.split())
        normalised_uncertainty = uncertainty_count / max(text_length / 50, 1)
        linguistic_confidence = 1.0 - min(normalised_uncertainty, 1.0)

        # Boost linguistic confidence if many overconfidence markers
        if overconfidence_count > 2:
            linguistic_confidence = min(1.0, linguistic_confidence + 0.3)

        # === RAG GROUNDING ANALYSIS (Setun-inspired) ===

        has_rag_context = retrieval_confidence is not None
        rag_is_weak = has_rag_context and retrieval_confidence < self.threshold_uncertain
        rag_is_strong = has_rag_context and retrieval_confidence >= self.threshold_confident
        rag_is_medium = has_rag_context and self.threshold_uncertain <= retrieval_confidence < self.threshold_confident
        no_chunks = chunks_found is not None and chunks_found == 0

        # === STATE DETERMINATION (Setun ternary logic) ===

        # Priority 1: Unanswerable questions
        if unanswerable_question:
            state = TernaryState.UNCERTAIN
            confidence = 0.1
            reason = "Question appears to require prediction or unknowable information"
            grounded = False

        # Priority 2: No RAG chunks found at all
        elif no_chunks:
            state = TernaryState.UNCERTAIN
            confidence = 0.0
            reason = "No relevant context found in knowledge base"
            markers_found.append("no_rag_context")
            grounded = False

        # Priority 3: OVERCONFIDENCE MARKERS + WEAK RAG = DANGER ZONE (-1)
        # Even with hedging, if there are strong confidence markers + weak RAG, flag it
        # This catches "I think it might definitely be 100% correct" patterns
        elif rag_is_weak and overconfidence_count >= 1:
            state = TernaryState.OVERCONFIDENT
            confidence = retrieval_confidence
            reason = f"DANGER: Confident response without grounding (RAG: {retrieval_confidence:.0%})"
            markers_found.append("overconfident_no_grounding")
            grounded = False

        # Priority 4: Weak RAG + any response = abstain
        elif rag_is_weak:
            state = TernaryState.UNCERTAIN
            confidence = retrieval_confidence
            reason = f"Insufficient grounding (RAG confidence: {retrieval_confidence:.0%})"
            markers_found.append("weak_rag_grounding")
            grounded = False

        # Priority 5: Fabrication detected
        elif fabrication_detected:
            state = TernaryState.UNCERTAIN
            confidence = 0.2
            reason = "Response contains markers of knowledge limitations"
            grounded = False

        # Priority 6: High linguistic uncertainty
        elif normalised_uncertainty > 0.5:
            state = TernaryState.UNCERTAIN
            confidence = 1.0 - normalised_uncertainty
            reason = f"High uncertainty ({uncertainty_count} markers found)"
            grounded = rag_is_strong

        # Priority 7: Overconfidence without hedging (and no strong RAG)
        elif overconfidence_count > 2 and uncertainty_count == 0 and not rag_is_strong:
            state = TernaryState.OVERCONFIDENT
            confidence = 0.4
            reason = "Response shows signs of overconfidence without hedging"
            grounded = False

        # Priority 8: Strong RAG + confident response = GROUNDED CONFIDENCE
        elif rag_is_strong:
            state = TernaryState.CONFIDENT
            confidence = min(retrieval_confidence, linguistic_confidence)
            reason = f"Response grounded in retrieved context (RAG: {retrieval_confidence:.0%})"
            grounded = True

        # Priority 9: Medium RAG + confident response
        elif rag_is_medium:
            state = TernaryState.CONFIDENT
            confidence = retrieval_confidence * linguistic_confidence
            reason = f"Response partially grounded (RAG: {retrieval_confidence:.0%})"
            grounded = True

        # Default: No RAG context provided, linguistic analysis only
        else:
            state = TernaryState.CONFIDENT
            confidence = linguistic_confidence
            reason = "Response appears confident (no RAG context provided)"
            grounded = False

        # Calculate final abstention decision
        should_abstain = state in [TernaryState.UNCERTAIN, TernaryState.OVERCONFIDENT]

        return EpistemicState(
            state=state,
            confidence=confidence,
            should_abstain=should_abstain,
            reason=reason,
            markers_found=markers_found[:5],
            retrieval_confidence=retrieval_confidence,
            chunks_found=chunks_found,
            grounded=grounded
        )
