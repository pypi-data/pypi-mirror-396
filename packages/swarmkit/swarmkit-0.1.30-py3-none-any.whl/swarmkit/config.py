"""Configuration types for SwarmKit SDK."""

from dataclasses import dataclass
from typing import List, Literal, Optional


AgentType = Literal['codex', 'claude', 'gemini', 'qwen']
WorkspaceMode = Literal['knowledge', 'swe']
ReasoningEffort = Literal['low', 'medium', 'high', 'xhigh']


@dataclass
class AgentConfig:
    """Agent configuration.

    Args:
        type: Agent type (codex, claude, gemini, qwen)
        api_key: SwarmKit API key from https://dashboard.swarmlink.ai
        model: Model name (optional - uses agent's default if not specified)
        reasoning_effort: Reasoning effort for Codex models (optional)
        betas: Beta headers for Claude (Sonnet 4.5 only; e.g. ["context-1m-2025-08-07"] for 1M context)
    """
    type: AgentType
    api_key: str
    model: Optional[str] = None
    reasoning_effort: Optional[ReasoningEffort] = None
    betas: Optional[List[str]] = None


@dataclass
class E2BProvider:
    """E2B sandbox provider configuration.

    Args:
        api_key: E2B API key
        template_id: E2B template ID (optional - auto-selected based on agent type)
        timeout_ms: Sandbox timeout in milliseconds (default: 3600000 = 1 hour)
    """
    api_key: str
    template_id: Optional[str] = None
    timeout_ms: int = 3600000

    @property
    def type(self) -> Literal['e2b']:
        """Provider type."""
        return 'e2b'

    @property
    def config(self) -> dict:
        """Provider configuration dict."""
        result = {'apiKey': self.api_key}
        if self.template_id:
            result['templateId'] = self.template_id
        if self.timeout_ms:
            result['timeoutMs'] = self.timeout_ms
        return result


# Type alias for sandbox provider (extensible for future providers)
SandboxProvider = E2BProvider
