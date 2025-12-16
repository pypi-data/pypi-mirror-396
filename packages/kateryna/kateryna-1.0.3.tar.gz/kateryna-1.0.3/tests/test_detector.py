"""
Tests for Kateryna EpistemicDetector
====================================

Comprehensive tests for the Setun-inspired ternary logic detector.
"""

import pytest
from kateryna import EpistemicDetector, calculate_retrieval_confidence, EpistemicState, TernaryState


class TestTernaryState:
    """Tests for TernaryState enum."""

    def test_confident_value(self):
        assert TernaryState.CONFIDENT.value == 1

    def test_uncertain_value(self):
        assert TernaryState.UNCERTAIN.value == 0

    def test_overconfident_value(self):
        assert TernaryState.OVERCONFIDENT.value == -1


class TestCalculateRetrievalConfidence:
    """Tests for RAG confidence calculation."""

    def test_empty_chunks_returns_zero(self):
        confidence, count = calculate_retrieval_confidence([])
        assert confidence == 0.0
        assert count == 0

    def test_low_distance_high_confidence(self):
        chunks = [
            {"distance": 0.1},
            {"distance": 0.15},
            {"distance": 0.2},
        ]
        confidence, count = calculate_retrieval_confidence(chunks)
        assert confidence > 0.7
        assert count == 3

    def test_high_distance_low_confidence(self):
        chunks = [
            {"distance": 0.9},
            {"distance": 0.85},
            {"distance": 0.95},
        ]
        confidence, count = calculate_retrieval_confidence(chunks)
        assert confidence < 0.2
        assert count == 3

    def test_relevance_score_format(self):
        chunks = [
            {"relevance": 0.9},
            {"relevance": 0.85},
        ]
        confidence, count = calculate_retrieval_confidence(chunks)
        assert confidence > 0.8
        assert count == 2

    def test_score_format(self):
        chunks = [
            {"score": 0.88},
            {"score": 0.75},
        ]
        confidence, count = calculate_retrieval_confidence(chunks)
        assert confidence > 0.7
        assert count == 2

    def test_similarity_format(self):
        chunks = [
            {"similarity": 0.92},
            {"similarity": 0.88},
        ]
        confidence, count = calculate_retrieval_confidence(chunks)
        assert confidence > 0.85
        assert count == 2


class TestEpistemicDetector:
    """Tests for the main detector class."""

    @pytest.fixture
    def detector(self):
        return EpistemicDetector()

    def test_confident_response_no_rag(self, detector):
        state = detector.analyze("The function returns the sum of two numbers.")
        assert state.state == TernaryState.CONFIDENT
        assert not state.should_abstain
        assert not state.grounded

    def test_uncertain_response(self, detector):
        state = detector.analyze(
            "I'm not sure, but I think it might be related to something. "
            "Maybe it could possibly work, though I'm uncertain."
        )
        assert state.state == TernaryState.UNCERTAIN
        assert state.should_abstain
        assert len(state.markers_found) > 0

    def test_fabrication_markers_detected(self, detector):
        state = detector.analyze(
            "As an AI language model, I don't have access to real-time data. "
            "My training data only goes up to a certain cutoff."
        )
        assert state.state == TernaryState.UNCERTAIN
        assert state.should_abstain
        assert "fabrication_marker" in state.markers_found

    def test_overconfident_without_grounding(self, detector):
        """The key Setun insight: confident + no grounding = DANGER."""
        state = detector.analyze(
            "This is definitely the answer. It's certainly correct. "
            "Absolutely guaranteed to work without a doubt.",
            retrieval_confidence=0.1,
            chunks_found=1
        )
        assert state.state == TernaryState.OVERCONFIDENT
        assert state.is_danger_zone
        assert state.should_abstain

    def test_strong_rag_confident_response(self, detector):
        state = detector.analyze(
            "The function returns the sum of two numbers.",
            retrieval_confidence=0.85,
            chunks_found=5
        )
        assert state.state == TernaryState.CONFIDENT
        assert not state.should_abstain
        assert state.grounded

    def test_weak_rag_confident_response_is_danger_zone(self, detector):
        """Weak RAG + confident response = DANGER (key Setun insight!)."""
        state = detector.analyze(
            "The function definitely returns the sum.",
            retrieval_confidence=0.15,
            chunks_found=2
        )
        # Should either be UNCERTAIN or OVERCONFIDENT, both trigger abstention
        assert state.should_abstain
        assert not state.grounded

    def test_no_chunks_abstains(self, detector):
        state = detector.analyze(
            "The answer is 42.",
            retrieval_confidence=0.0,
            chunks_found=0
        )
        assert state.state == TernaryState.UNCERTAIN
        assert state.should_abstain
        assert not state.grounded
        assert "no_rag_context" in state.markers_found


class TestPreCheck:
    """Tests for question pre-screening."""

    @pytest.fixture
    def detector(self):
        return EpistemicDetector()

    def test_future_prediction_caught(self, detector):
        should_abstain, reason = detector.should_abstain_on_question(
            "What will Bitcoin be worth in 2030?"
        )
        assert should_abstain
        assert "prediction" in reason.lower()

    def test_stock_prediction_caught(self, detector):
        should_abstain, reason = detector.should_abstain_on_question(
            "What will the stock price be tomorrow?"
        )
        assert should_abstain

    def test_lottery_caught(self, detector):
        should_abstain, reason = detector.should_abstain_on_question(
            "What are tomorrow's lottery numbers?"
        )
        assert should_abstain

    def test_normal_question_passes(self, detector):
        should_abstain, reason = detector.should_abstain_on_question(
            "How does this sorting algorithm work?"
        )
        assert not should_abstain
        assert reason == ""


class TestSetunTernaryMapping:
    """Verify the Setun ternary mapping table works correctly."""

    @pytest.fixture
    def detector(self):
        return EpistemicDetector()

    def test_high_rag_confident(self, detector):
        """High RAG + Confident = CONFIDENT, grounded."""
        state = detector.analyze(
            "The function calculates the sum.",
            retrieval_confidence=0.85,
            chunks_found=5
        )
        assert state.state == TernaryState.CONFIDENT
        assert state.grounded

    def test_high_rag_uncertain(self, detector):
        """High RAG + Uncertain = UNCERTAIN, grounded."""
        state = detector.analyze(
            "I'm not sure, maybe it could be the sum. Perhaps.",
            retrieval_confidence=0.85,
            chunks_found=5
        )
        assert state.state == TernaryState.UNCERTAIN
        assert state.grounded  # RAG was good

    def test_low_rag_confident_is_danger(self, detector):
        """Low RAG + Confident = OVERCONFIDENT (-1) = DANGER ZONE."""
        state = detector.analyze(
            "It definitely calculates the sum. Absolutely certain.",
            retrieval_confidence=0.1,
            chunks_found=1
        )
        assert state.state == TernaryState.OVERCONFIDENT
        assert state.is_danger_zone
        assert not state.grounded


class TestEpistemicState:
    """Tests for EpistemicState dataclass."""

    def test_is_confident(self):
        state = EpistemicState(
            state=TernaryState.CONFIDENT, confidence=0.9, should_abstain=False,
            reason="test", markers_found=[], grounded=True
        )
        assert state.is_confident
        assert not state.is_uncertain
        assert not state.is_overconfident
        assert not state.is_danger_zone

    def test_is_uncertain(self):
        state = EpistemicState(
            state=TernaryState.UNCERTAIN, confidence=0.5, should_abstain=True,
            reason="test", markers_found=[], grounded=False
        )
        assert state.is_uncertain
        assert not state.is_confident
        assert not state.is_danger_zone

    def test_is_overconfident_is_danger_zone(self):
        state = EpistemicState(
            state=TernaryState.OVERCONFIDENT, confidence=0.6, should_abstain=True,
            reason="test", markers_found=[], grounded=False
        )
        assert state.is_overconfident
        assert state.is_danger_zone
        assert not state.is_confident

    def test_str_representation(self):
        state = EpistemicState(
            state=TernaryState.CONFIDENT, confidence=0.85, should_abstain=False,
            reason="test", markers_found=[], grounded=True
        )
        str_repr = str(state)
        assert "CONFIDENT" in str_repr
        assert "85%" in str_repr
        assert "grounded" in str_repr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
