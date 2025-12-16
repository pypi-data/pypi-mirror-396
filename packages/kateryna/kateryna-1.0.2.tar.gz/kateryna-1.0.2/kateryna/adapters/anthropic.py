"""
Anthropic Adapter for Kateryna Epistemic Analysis
=================================================

Wraps Anthropic's Claude API with Setun-inspired epistemic analysis.
"""

from typing import Optional

try:
    from anthropic import Anthropic, AsyncAnthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from .base import BaseEpistemicAdapter
from ..state import EpistemicState, EpistemicResponse, TernaryState


class AnthropicEpistemicAdapter(BaseEpistemicAdapter):
    """
    Async epistemic adapter for Anthropic's Claude API.

    Example:
        from anthropic import AsyncAnthropic
        from kateryna.adapters.anthropic import AnthropicEpistemicAdapter

        client = AnthropicEpistemicAdapter(
            anthropic_client=AsyncAnthropic(),
            model="claude-3-5-sonnet-20241022"
        )

        response = await client.generate_with_rag(
            "How does this function work?",
            rag_chunks=my_retrieved_chunks
        )
    """

    def __init__(
        self,
        anthropic_client: Optional["AsyncAnthropic"] = None,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        **kwargs
    ):
        if not HAS_ANTHROPIC:
            raise ImportError(
                "Anthropic package not installed. "
                "Install with: pip install kateryna[anthropic]"
            )

        super().__init__(**kwargs)

        if anthropic_client:
            self.client = anthropic_client
        else:
            self.client = AsyncAnthropic(api_key=api_key)

        self.model = model

    async def _generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            **kwargs
        )

        if message.content and len(message.content) > 0:
            return message.content[0].text
        return ""


class AnthropicSyncEpistemicAdapter:
    """
    Synchronous epistemic adapter for Anthropic's Claude API.

    Example:
        from anthropic import Anthropic
        from kateryna.adapters.anthropic import AnthropicSyncEpistemicAdapter

        client = AnthropicSyncEpistemicAdapter(Anthropic())
        response = client.generate("What is the capital of France?")
    """

    def __init__(
        self,
        anthropic_client: Optional["Anthropic"] = None,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        **kwargs
    ):
        if not HAS_ANTHROPIC:
            raise ImportError(
                "Anthropic package not installed. "
                "Install with: pip install kateryna[anthropic]"
            )

        from ..detector import EpistemicDetector, calculate_retrieval_confidence

        self.detector = EpistemicDetector()
        self.calculate_retrieval_confidence = calculate_retrieval_confidence

        if anthropic_client:
            self.client = anthropic_client
        else:
            self.client = Anthropic(api_key=api_key)

        self.model = model
        self.auto_abstain = kwargs.get('auto_abstain', True)
        self.show_confidence = kwargs.get('show_confidence', False)
        self.min_retrieval_confidence = kwargs.get('min_retrieval_confidence', 0.3)

        self.ABSTENTION_MESSAGES = BaseEpistemicAdapter.ABSTENTION_MESSAGES
        self.EPISTEMIC_SYSTEM_SUFFIX = BaseEpistemicAdapter.EPISTEMIC_SYSTEM_SUFFIX

    def _generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            **kwargs
        )

        if message.content and len(message.content) > 0:
            return message.content[0].text
        return ""

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> EpistemicResponse:
        """Generate with epistemic analysis."""
        should_abstain, reason = self.detector.should_abstain_on_question(prompt)
        if should_abstain:
            return EpistemicResponse(
                content=self.ABSTENTION_MESSAGES["prediction"],
                epistemic_state=EpistemicState(
                    state=TernaryState.UNCERTAIN, confidence=0.0, should_abstain=True,
                    reason=reason, markers_found=["pre_check"]
                ),
                original_response="",
                was_modified=True
            )

        enhanced_system = (system or "") + self.EPISTEMIC_SYSTEM_SUFFIX
        response = self._generate(prompt, system=enhanced_system, **kwargs)
        epistemic_state = self.detector.analyze(response, question=prompt)

        content = response
        was_modified = False
        if self.auto_abstain and epistemic_state.should_abstain:
            if epistemic_state.is_danger_zone:
                content = self.ABSTENTION_MESSAGES["danger_zone"]
            else:
                content = self.ABSTENTION_MESSAGES["uncertain"]
            was_modified = True

        return EpistemicResponse(
            content=content,
            epistemic_state=epistemic_state,
            original_response=response,
            was_modified=was_modified
        )

    def generate_with_rag(self, prompt: str, rag_chunks: list, system: Optional[str] = None, **kwargs) -> EpistemicResponse:
        """Generate with RAG grounding."""
        retrieval_confidence, chunks_count = self.calculate_retrieval_confidence(rag_chunks)

        should_abstain, reason = self.detector.should_abstain_on_question(prompt)
        if should_abstain:
            return EpistemicResponse(
                content=self.ABSTENTION_MESSAGES["prediction"],
                epistemic_state=EpistemicState(
                    state=TernaryState.UNCERTAIN, confidence=0.0, should_abstain=True,
                    reason=reason, markers_found=["pre_check"],
                    retrieval_confidence=retrieval_confidence,
                    chunks_found=chunks_count, grounded=False
                ),
                original_response="",
                was_modified=True
            )

        if chunks_count == 0:
            return EpistemicResponse(
                content=self.ABSTENTION_MESSAGES["no_context"],
                epistemic_state=EpistemicState(
                    state=TernaryState.UNCERTAIN, confidence=0.0, should_abstain=True,
                    reason="No relevant context found",
                    markers_found=["no_rag_context"],
                    retrieval_confidence=0.0, chunks_found=0, grounded=False
                ),
                original_response="",
                was_modified=True
            )

        if retrieval_confidence < self.min_retrieval_confidence:
            return EpistemicResponse(
                content=self.ABSTENTION_MESSAGES["weak_grounding"],
                epistemic_state=EpistemicState(
                    state=TernaryState.UNCERTAIN, confidence=retrieval_confidence, should_abstain=True,
                    reason=f"Insufficient grounding (RAG: {retrieval_confidence:.0%})",
                    markers_found=["weak_rag_grounding"],
                    retrieval_confidence=retrieval_confidence,
                    chunks_found=chunks_count, grounded=False
                ),
                original_response="",
                was_modified=True
            )

        context_parts = []
        for chunk in rag_chunks[:5]:
            content = chunk.get('document', chunk.get('content', chunk.get('text', '')))
            if content:
                context_parts.append(content)
        rag_context = "\n\n".join(context_parts)

        enhanced_prompt = f"Based on this context:\n\n{rag_context}\n\n---\n\nQuestion: {prompt}"
        enhanced_system = (system or "") + "\n\nBase your answer on the provided context only."

        response = self._generate(enhanced_prompt, system=enhanced_system, **kwargs)
        epistemic_state = self.detector.analyze(
            response, question=prompt,
            retrieval_confidence=retrieval_confidence,
            chunks_found=chunks_count
        )

        content = response
        was_modified = False
        if self.auto_abstain and epistemic_state.should_abstain:
            if epistemic_state.is_danger_zone:
                content = self.ABSTENTION_MESSAGES["danger_zone"]
            else:
                content = self.ABSTENTION_MESSAGES["weak_grounding"]
            was_modified = True

        return EpistemicResponse(
            content=content,
            epistemic_state=epistemic_state,
            original_response=response,
            was_modified=was_modified
        )
