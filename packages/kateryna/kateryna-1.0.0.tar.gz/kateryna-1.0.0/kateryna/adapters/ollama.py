"""
Ollama Adapter for Kateryna Epistemic Analysis
==============================================

Wraps local Ollama models with Setun-inspired epistemic analysis.
Works with any Ollama model (Llama, Mistral, Qwen, etc.)
"""

from typing import Optional
import json

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from .base import BaseEpistemicAdapter
from ..state import EpistemicState, EpistemicResponse, TernaryState


class OllamaEpistemicAdapter(BaseEpistemicAdapter):
    """
    Async epistemic adapter for local Ollama models.

    Example:
        from kateryna.adapters.ollama import OllamaEpistemicAdapter

        client = OllamaEpistemicAdapter(model="llama3.2")

        response = await client.generate_with_rag(
            "How does this COBOL code work?",
            rag_chunks=my_retrieved_chunks
        )

        if response.epistemic_state.is_danger_zone:
            print("WARNING: Potential hallucination detected")
    """

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        if not HAS_HTTPX:
            raise ImportError(
                "httpx package not installed. "
                "Install with: pip install httpx"
            )

        super().__init__(**kwargs)
        self.model = model
        self.base_url = base_url.rstrip('/')
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def _generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        client = await self._get_client()

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        if system:
            payload["system"] = system

        response = await client.post(
            f"{self.base_url}/api/generate",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


class OllamaSyncEpistemicAdapter:
    """
    Synchronous epistemic adapter for local Ollama models.

    Example:
        from kateryna.adapters.ollama import OllamaSyncEpistemicAdapter

        client = OllamaSyncEpistemicAdapter(model="llama3.2")
        response = client.generate("Explain this code")
        print(response.content)
    """

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        if not HAS_HTTPX:
            raise ImportError(
                "httpx package not installed. "
                "Install with: pip install httpx"
            )

        from ..detector import EpistemicDetector, calculate_retrieval_confidence

        self.detector = EpistemicDetector()
        self.calculate_retrieval_confidence = calculate_retrieval_confidence

        self.model = model
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=120.0)

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
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        if system:
            payload["system"] = system

        response = self.client.post(
            f"{self.base_url}/api/generate",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

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

    def close(self):
        """Close the HTTP client."""
        self.client.close()
