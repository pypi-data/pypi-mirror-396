"""Base LLM interface for PromptSentry."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a chat response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM is available and ready."""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the model name."""
        pass
