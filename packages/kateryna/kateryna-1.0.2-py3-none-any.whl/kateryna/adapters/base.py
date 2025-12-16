"""
Base Adapter for Kateryna Epistemic LLM Clients
===============================================

Abstract base class for wrapping any LLM client with epistemic analysis.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..detector import EpistemicDetector, calculate_retrieval_confidence
from ..state import EpistemicState, EpistemicResponse, TernaryState


class BaseEpistemicAdapter(ABC):
    """
    Abstract base class for epistemic LLM adapters.

    Subclass this to add epistemic analysis to any LLM client.

    Example:
        class MyLLMAdapter(BaseEpistemicAdapter):
            def __init__(self, client):
                super().__init__()
                self.client = client

            async def _generate(self, prompt, system=None, **kwargs):
                return await self.client.complete(prompt, system_prompt=system)
    """

    ABSTENTION_MESSAGES = {
        "prediction": (
            "I don't have reliable information to answer this question. "
            "It asks about future events or predictions that I cannot make with confidence."
        ),
        "uncertain": (
            "I'm not confident enough to answer this question. "
            "I'd rather say I don't know than risk giving you incorrect information."
        ),
        "overconfident": (
            "WARNING: My response may be unreliable. I found myself being confident "
            "about something without sufficient grounding. Please verify this information "
            "from authoritative sources before acting on it."
        ),
        "no_context": (
            "I couldn't find relevant information in the knowledge base to answer this question. "
            "Without grounding in source material, I'd rather abstain than risk hallucinating."
        ),
        "weak_grounding": (
            "The information I found in the knowledge base isn't relevant enough to confidently "
            "answer this question. I'd rather say I don't know than make something up."
        ),
        "danger_zone": (
            "DANGER: I detected a high-confidence response without adequate grounding. "
            "This is the exact pattern that leads to hallucinations. "
            "I cannot provide a reliable answer to this question."
        ),
    }

    EPISTEMIC_SYSTEM_SUFFIX = (
        "\n\nIMPORTANT: If you are uncertain about something, say so clearly. "
        "Use phrases like 'I'm not sure' or 'I don't know' when appropriate. "
        "Never make up information. It's better to admit uncertainty than to hallucinate."
    )

    def __init__(
        self,
        auto_abstain: bool = True,
        show_confidence: bool = False,
        min_retrieval_confidence: float = 0.3
    ):
        """
        Initialize the epistemic adapter.

        Args:
            auto_abstain: If True, replace uncertain responses with abstention messages
            show_confidence: If True, append confidence info to responses
            min_retrieval_confidence: Minimum RAG confidence to proceed with generation
        """
        self.detector = EpistemicDetector(min_retrieval_confidence=min_retrieval_confidence)
        self.auto_abstain = auto_abstain
        self.show_confidence = show_confidence
        self.min_retrieval_confidence = min_retrieval_confidence

    @abstractmethod
    async def _generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the underlying LLM.

        Implement this method in subclasses.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            **kwargs: Additional arguments for the LLM

        Returns:
            The raw LLM response text
        """
        pass

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        check_question_first: bool = True,
        **kwargs
    ) -> EpistemicResponse:
        """
        Generate a response with epistemic analysis (no RAG).

        Args:
            prompt: The user prompt
            system: Optional system prompt
            check_question_first: If True, check for unanswerable questions first
            **kwargs: Additional arguments for the LLM

        Returns:
            EpistemicResponse with content and epistemic state
        """
        # Pre-check for unanswerable questions
        if check_question_first:
            should_abstain, reason = self.detector.should_abstain_on_question(prompt)
            if should_abstain:
                return EpistemicResponse(
                    content=self.ABSTENTION_MESSAGES["prediction"],
                    epistemic_state=EpistemicState(
                        state=TernaryState.UNCERTAIN,
                        confidence=0.0,
                        should_abstain=True,
                        reason=reason,
                        markers_found=["pre_check"]
                    ),
                    original_response="",
                    was_modified=True
                )

        # Enhance system prompt with epistemic instructions
        enhanced_system = (system or "") + self.EPISTEMIC_SYSTEM_SUFFIX

        # Generate response
        response = await self._generate(prompt, system=enhanced_system, **kwargs)

        # Analyze response
        epistemic_state = self.detector.analyze(response, question=prompt)

        # Apply abstention if needed
        content, was_modified = self._apply_abstention(response, epistemic_state)

        return EpistemicResponse(
            content=content,
            epistemic_state=epistemic_state,
            original_response=response,
            was_modified=was_modified
        )

    async def generate_with_rag(
        self,
        prompt: str,
        rag_chunks: List[Dict[str, Any]],
        system: Optional[str] = None,
        check_question_first: bool = True,
        **kwargs
    ) -> EpistemicResponse:
        """
        Generate a response with RAG-grounded epistemic analysis.

        This is the Setun-inspired method: confidence requires evidence.
        If RAG retrieval confidence is low, we abstain rather than hallucinate.

        Args:
            prompt: The user prompt
            rag_chunks: Retrieved chunks from any vector DB
            system: Optional system prompt
            check_question_first: If True, check for unanswerable questions first
            **kwargs: Additional arguments for the LLM

        Returns:
            EpistemicResponse with content, epistemic state, and grounding info
        """
        # Calculate RAG retrieval confidence
        retrieval_confidence, chunks_count = calculate_retrieval_confidence(rag_chunks)

        # Pre-check for unanswerable questions
        if check_question_first:
            should_abstain, reason = self.detector.should_abstain_on_question(prompt)
            if should_abstain:
                return EpistemicResponse(
                    content=self.ABSTENTION_MESSAGES["prediction"],
                    epistemic_state=EpistemicState(
                        state=TernaryState.UNCERTAIN,
                        confidence=0.0,
                        should_abstain=True,
                        reason=reason,
                        markers_found=["pre_check"],
                        retrieval_confidence=retrieval_confidence,
                        chunks_found=chunks_count,
                        grounded=False
                    ),
                    original_response="",
                    was_modified=True
                )

        # PRE-RAG ABSTENTION: No chunks found
        if chunks_count == 0:
            return EpistemicResponse(
                content=self.ABSTENTION_MESSAGES["no_context"],
                epistemic_state=EpistemicState(
                    state=TernaryState.UNCERTAIN,
                    confidence=0.0,
                    should_abstain=True,
                    reason="No relevant context found in knowledge base",
                    markers_found=["no_rag_context"],
                    retrieval_confidence=0.0,
                    chunks_found=0,
                    grounded=False
                ),
                original_response="",
                was_modified=True
            )

        # PRE-RAG ABSTENTION: Retrieval confidence too low
        if retrieval_confidence < self.min_retrieval_confidence:
            return EpistemicResponse(
                content=self.ABSTENTION_MESSAGES["weak_grounding"],
                epistemic_state=EpistemicState(
                    state=TernaryState.UNCERTAIN,
                    confidence=retrieval_confidence,
                    should_abstain=True,
                    reason=f"Insufficient grounding (RAG confidence: {retrieval_confidence:.0%})",
                    markers_found=["weak_rag_grounding"],
                    retrieval_confidence=retrieval_confidence,
                    chunks_found=chunks_count,
                    grounded=False
                ),
                original_response="",
                was_modified=True
            )

        # Build context from RAG chunks
        rag_context = self._format_rag_context(rag_chunks)

        # Build enhanced prompt
        enhanced_prompt = f"""Based on the following relevant context:

{rag_context}

---

Question: {prompt}

Answer based on the context above. If the context doesn't contain relevant information, say so."""

        # Enhanced system prompt for RAG
        enhanced_system = (system or "") + (
            "\n\nIMPORTANT: Base your answer on the provided context. "
            "If you are uncertain or the context doesn't help, say so clearly. "
            "Never make up information beyond what's in the context."
        )

        # Generate response
        response = await self._generate(enhanced_prompt, system=enhanced_system, **kwargs)

        # Analyze with RAG context
        epistemic_state = self.detector.analyze(
            response,
            question=prompt,
            retrieval_confidence=retrieval_confidence,
            chunks_found=chunks_count
        )

        # Apply abstention if needed
        content, was_modified = self._apply_abstention(response, epistemic_state)

        return EpistemicResponse(
            content=content,
            epistemic_state=epistemic_state,
            original_response=response,
            was_modified=was_modified
        )

    def _format_rag_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format RAG chunks into context string."""
        context_parts = []
        for chunk in chunks[:5]:
            content = chunk.get('document', chunk.get('content', chunk.get('text', '')))
            metadata = chunk.get('metadata', {})
            source = metadata.get('file', metadata.get('source', 'unknown'))

            if content:
                context_parts.append(f"### {source}\n{content}")

        return "\n\n".join(context_parts)

    def _apply_abstention(
        self,
        response: str,
        epistemic_state: EpistemicState
    ) -> tuple[str, bool]:
        """Apply abstention logic to response."""
        was_modified = False

        if self.auto_abstain and epistemic_state.should_abstain:
            if epistemic_state.is_danger_zone:
                # OVERCONFIDENT (-1) - the danger zone
                content = self.ABSTENTION_MESSAGES["danger_zone"]
                was_modified = True
            elif epistemic_state.is_uncertain:
                # UNCERTAIN (0)
                if not epistemic_state.grounded:
                    content = self.ABSTENTION_MESSAGES["weak_grounding"]
                else:
                    content = self.ABSTENTION_MESSAGES["uncertain"]
                was_modified = True
            else:
                content = response
        else:
            content = response

        # Optionally append confidence info
        if self.show_confidence and not was_modified:
            grounding = "grounded" if epistemic_state.grounded else "ungrounded"
            rag_info = ""
            if epistemic_state.retrieval_confidence is not None:
                rag_info = f", RAG: {epistemic_state.retrieval_confidence:.0%}"
            content += (
                f"\n\n[Confidence: {epistemic_state.confidence:.0%} - "
                f"{epistemic_state.state.name}, {grounding}{rag_info}]"
            )

        return content, was_modified
