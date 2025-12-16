"""
Kateryna State - Ternary Logic for LLM Responses
=================================================

Balanced ternary epistemic states:
    +1 = CONFIDENT (grounded in evidence)
     0 = UNCERTAIN (abstain)
    -1 = OVERCONFIDENT (potential hallucination)

Named after Kateryna Yushchenko (1919-2001), Ukrainian computer scientist
who invented indirect addressing in 1955.

References:
    Brusentsov, N.P. (1960). An Electronic Calculating Machine Based on
        Ternary Code. Doklady Akademii Nauk SSSR.
    Lukasiewicz, J. (1920). On Three-Valued Logic. Ruch Filozoficzny.
    Kleene, S.C. (1938). On Notation for Ordinal Numbers. Journal of
        Symbolic Logic.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TernaryState(Enum):
    """
    Balanced ternary states from Setun architecture.

    The key insight: -1 (OVERCONFIDENT) catches the exact failure mode
    that kills people - confident bullshit without evidence.
    """
    CONFIDENT = 1       # +1: Grounded confidence - return response
    UNCERTAIN = 0       #  0: Appropriate uncertainty - abstain
    OVERCONFIDENT = -1  # -1: Ungrounded confidence - DANGER FLAG


@dataclass
class EpistemicState:
    """
    Result of epistemic analysis.

    Implements Setun-inspired balanced ternary logic for LLM confidence:
    - state=CONFIDENT (+1): Model is confident AND grounded in evidence
    - state=UNCERTAIN (0): Model is uncertain, should abstain
    - state=OVERCONFIDENT (-1): Model is confident WITHOUT evidence (hallucination risk)

    Attributes:
        state: Ternary state (CONFIDENT, UNCERTAIN, OVERCONFIDENT)
        confidence: Combined confidence score 0.0 to 1.0
        should_abstain: Whether the response should be replaced with abstention
        reason: Human-readable explanation
        markers_found: Linguistic markers that influenced the decision
        retrieval_confidence: RAG retrieval confidence (0.0-1.0) if provided
        chunks_found: Number of relevant chunks retrieved
        grounded: True if response is backed by RAG context
    """
    state: TernaryState
    confidence: float
    should_abstain: bool
    reason: str
    markers_found: List[str]
    retrieval_confidence: Optional[float] = None
    chunks_found: Optional[int] = None
    grounded: bool = False

    def __str__(self) -> str:
        grounding = "grounded" if self.grounded else "ungrounded"
        return (
            f"EpistemicState({self.state.name}, "
            f"{self.confidence:.0%}, {grounding})"
        )

    @property
    def is_confident(self) -> bool:
        """True if state is CONFIDENT (+1) - grounded confidence."""
        return self.state == TernaryState.CONFIDENT

    @property
    def is_uncertain(self) -> bool:
        """True if state is UNCERTAIN (0) - should abstain."""
        return self.state == TernaryState.UNCERTAIN

    @property
    def is_overconfident(self) -> bool:
        """True if state is OVERCONFIDENT (-1) - hallucination risk."""
        return self.state == TernaryState.OVERCONFIDENT

    @property
    def is_danger_zone(self) -> bool:
        """
        Confident language + weak grounding = hallucination risk.

        This is the breakthrough insight. The -1 state catches
        the exact failure mode that kills people: confident bullshit.
        """
        return self.state == TernaryState.OVERCONFIDENT


@dataclass
class EpistemicResponse:
    """
    LLM response with epistemic analysis.

    Attributes:
        content: The final response content (may be abstention message)
        epistemic_state: Full epistemic analysis
        original_response: The raw LLM response before modification
        was_modified: True if response was replaced with abstention
    """
    content: str
    epistemic_state: EpistemicState
    original_response: str
    was_modified: bool

    def __str__(self) -> str:
        status = "abstained" if self.was_modified else "passed"
        return f"EpistemicResponse({status}, {self.epistemic_state})"
