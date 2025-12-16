"""Qwen 2.5 1.5B LLM implementation for PromptSentry."""

from typing import List, Dict, Any, Optional

from promptsentry.llm.base import BaseLLM
from promptsentry.models.config import LLMConfig


class QwenLLM(BaseLLM):
    """
    Qwen 2.5 Coder 0.5B implementation for local LLM inference.
    
    This is a lightweight, code-specialized model (~1GB) suitable for
    security analysis that can run on CPU or GPU.
    """
    
    DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the Qwen LLM.
        
        Args:
            config: LLM configuration
        """
        self.config = config or LLMConfig()
        self._model = None
        self._tokenizer = None
        self._device = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Load the model and tokenizer."""
        if self._initialized:
            return
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except ImportError:
            raise ImportError(
                "transformers and torch are required for Qwen. "
                "Install with: pip install transformers torch"
            )
        
        # Determine device
        if self.config.device == "auto":
            if torch.cuda.is_available():
                self._device = "cuda"
            elif torch.backends.mps.is_available():
                self._device = "mps"
            else:
                self._device = "cpu"
        else:
            self._device = self.config.device
        
        # Load tokenizer
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
        )
        
        # Prepare model loading kwargs
        load_kwargs = {
            "trust_remote_code": True,
        }
        
        # Device-specific settings
        if self._device == "cuda":
            load_kwargs["device_map"] = "auto"
            if self.config.load_in_4bit:
                try:
                    from transformers import BitsAndBytesConfig
                    load_kwargs["quantization_config"] = BitsAndBytesConfig(
                        load_in_4bit=True,
                    )
                except ImportError:
                    pass  # Skip quantization if bitsandbytes not available
                    
        elif self._device == "mps":
            import torch
            load_kwargs["torch_dtype"] = torch.float16
        else:  # CPU
            import torch
            load_kwargs["torch_dtype"] = torch.float32
        
        # Load model
        self._model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            **load_kwargs,
        )
        
        # Move to device if needed (for MPS)
        if self._device == "mps" and not hasattr(self._model, "device_map"):
            self._model = self._model.to("mps")
        
        self._initialized = True
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the prompt.
        
        Args:
            prompt: Input prompt text
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        if not self._initialized:
            self.initialize()
        
        # Prepare inputs
        inputs = self._tokenizer(prompt, return_tensors="pt")
        
        # Move to device
        if self._device:
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
        
        # Generation parameters
        gen_kwargs = {
            "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "do_sample": kwargs.get("temperature", self.config.temperature) > 0,
            "pad_token_id": self._tokenizer.eos_token_id,
        }
        
        # Generate
        outputs = self._model.generate(**inputs, **gen_kwargs)
        
        # Decode - skip input tokens
        response = self._tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True,
        )
        
        return response.strip()
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a chat response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response
        """
        if not self._initialized:
            self.initialize()
        
        # Apply chat template
        text = self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        
        return self.generate(text, **kwargs)
    
    def is_available(self) -> bool:
        """Check if the model is available."""
        return self._initialized
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.config.model_name
    
    @property
    def device(self) -> Optional[str]:
        """Get the device the model is running on."""
        return self._device
