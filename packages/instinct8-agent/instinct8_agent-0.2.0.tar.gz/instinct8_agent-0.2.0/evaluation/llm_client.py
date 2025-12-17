"""
Unified LLM Client Adapter

Supports both Anthropic API and OpenRouter API (OpenAI-compatible).
Automatically detects which to use based on environment variables:
- ANTHROPIC_API_KEY -> Uses Anthropic API
- OPENROUTER_API_KEY -> Uses OpenRouter API (OpenAI-compatible)

For OpenRouter, you can specify the model using OpenRouter model IDs.
"""

import os
from typing import Optional, List, Dict, Any
from enum import Enum


class LLMProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


class UnifiedLLMClient:
    """
    Unified client that works with both Anthropic and OpenRouter APIs.
    """
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize the unified LLM client.
        
        Args:
            provider: Force a specific provider, or None to auto-detect
        """
        self._provider = provider or self._detect_provider()
        self._client = self._create_client()
    
    @property
    def provider(self) -> LLMProvider:
        """Get the current provider."""
        return self._provider
    
    def _detect_provider(self) -> LLMProvider:
        """Detect which provider to use based on environment variables."""
        if os.getenv("OPENROUTER_API_KEY"):
            return LLMProvider.OPENROUTER
        elif os.getenv("ANTHROPIC_API_KEY"):
            return LLMProvider.ANTHROPIC
        else:
            # Default to Anthropic if neither is set (for backward compatibility)
            return LLMProvider.ANTHROPIC
    
    def _create_client(self):
        """Create the appropriate client based on provider."""
        if self._provider == LLMProvider.OPENROUTER:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    raise ValueError("OPENROUTER_API_KEY not set")
                
                # OpenRouter uses OpenAI-compatible API
                return OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                    default_headers={
                        "HTTP-Referer": "https://github.com/instinct8/context-compression",  # Optional
                        "X-Title": "Context Compression Evaluation",  # Optional
                    }
                )
            except ImportError:
                raise ImportError(
                    "openai package required for OpenRouter support. "
                    "Install with: pip install openai"
                )
        else:
            try:
                from anthropic import Anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not set")
                return Anthropic(api_key=api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required for Anthropic support. "
                    "Install with: pip install anthropic"
                )
    
    def create_message(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int,
        system: Optional[str] = None,
    ) -> Any:
        """
        Create a message/completion using the appropriate API.
        
        Args:
            model: Model identifier (provider-specific)
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            system: Optional system prompt (Anthropic format)
        
        Returns:
            Response object with .content[0].text attribute (normalized)
        """
        if self._provider == LLMProvider.OPENROUTER:
            # OpenRouter uses OpenAI-compatible format
            # Convert Anthropic format to OpenAI format
            openai_messages = []
            if system:
                openai_messages.append({"role": "system", "content": system})
            openai_messages.extend(messages)
            
            response = self._client.chat.completions.create(
                model=model,
                messages=openai_messages,
                max_tokens=max_tokens,
            )
            
            # Normalize to Anthropic-like format
            return _OpenAIResponseWrapper(response)
        else:
            # Anthropic format
            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system
            
            response = self._client.messages.create(**kwargs)
            return response
    
    @property
    def messages(self):
        """Property to maintain Anthropic-like API compatibility."""
        class MessagesWrapper:
            def __init__(self, client):
                self._client = client
            
            def create(self, **kwargs):
                return self._client.create_message(**kwargs)
        
        return MessagesWrapper(self)


class _OpenAIResponseWrapper:
    """
    Wrapper to normalize OpenAI/OpenRouter responses to Anthropic-like format.
    """
    
    def __init__(self, openai_response):
        self._response = openai_response
    
    @property
    def content(self):
        """Normalize OpenAI response.content to Anthropic format."""
        class ContentItem:
            def __init__(self, text):
                self.text = text
        
        # OpenAI returns message.content as a string
        text = self._response.choices[0].message.content
        return [ContentItem(text)]
    
    @property
    def text(self):
        """Direct access to text (for convenience)."""
        return self._response.choices[0].message.content


def get_default_model(provider: Optional[LLMProvider] = None) -> str:
    """
    Get the default model for the provider.
    
    Args:
        provider: Provider to use, or None to auto-detect
    
    Returns:
        Model identifier string
    """
    if provider is None:
        provider = UnifiedLLMClient().provider
    
    if provider == LLMProvider.OPENROUTER:
        # OpenRouter model IDs - using Claude 3.5 Sonnet equivalent
        # You can change this to any OpenRouter-supported model
        return os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    else:
        # Anthropic default
        return "claude-sonnet-4-20250514"

