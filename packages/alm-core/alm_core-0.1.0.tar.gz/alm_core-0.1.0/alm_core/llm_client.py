"""
LLM Client - Interface for Cognitive Engine
Abstracts LLM provider interactions with built-in safety.
"""

from typing import List, Dict, Any, Optional
import json


class LLMClient:
    """
    Abstract interface for LLM interactions.
    Supports multiple providers (OpenAI, Anthropic, local models).
    """
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider ('openai', 'anthropic', 'local')
            api_key: API key for the provider
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate client based on provider."""
        if self.provider == "openai":
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        elif self.provider == "anthropic":
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        
        elif self.provider == "local":
            # For local models (Ollama, LM Studio, etc.)
            self._client = None  # Will use HTTP requests
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            messages: Conversation history
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated text response
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        # Add system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        if self.provider == "openai":
            return self._generate_openai(messages, temp, max_tok)
        
        elif self.provider == "anthropic":
            return self._generate_anthropic(messages, temp, max_tok)
        
        elif self.provider == "local":
            return self._generate_local(messages, temp, max_tok)
        
        else:
            raise ValueError(f"Provider {self.provider} not implemented")
    
    def _generate_openai(self, messages: List[Dict[str, str]], temp: float, max_tok: int) -> str:
        """Generate using OpenAI API."""
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def _generate_anthropic(self, messages: List[Dict[str, str]], temp: float, max_tok: int) -> str:
        """Generate using Anthropic API."""
        try:
            # Anthropic uses a different format
            system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
            other_messages = [m for m in messages if m["role"] != "system"]
            
            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tok,
                temperature=temp,
                system=system_msg,
                messages=other_messages
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    def _generate_local(self, messages: List[Dict[str, str]], temp: float, max_tok: int) -> str:
        """Generate using local model (Ollama, etc.)."""
        import requests
        
        try:
            # Assuming Ollama-compatible endpoint
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temp,
                        "num_predict": max_tok
                    }
                }
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Local model error: {str(e)}")
    
    def generate_structured(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON response.
        
        Args:
            messages: Conversation history
            schema: JSON schema for the expected response
            system_prompt: Optional system prompt
            
        Returns:
            Parsed JSON response
        """
        # Add schema instruction to system prompt
        schema_instruction = f"\n\nYou must respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        full_system = (system_prompt or "") + schema_instruction
        
        response_text = self.generate(messages, system_prompt=full_system)
        
        # Extract JSON from response (handles markdown code blocks)
        json_str = response_text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM did not return valid JSON: {e}\n\nResponse: {response_text}")
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimate of token count.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def set_model(self, model: str):
        """Change the active model."""
        self.model = model
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
