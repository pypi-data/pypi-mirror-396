"""
Ollama client integration for the Agentic Resume Builder.

This module provides connection management and validation for Ollama,
ensuring all AI processing remains local.
"""

import logging
from typing import List, Optional

import ollama
from ollama import Client

from agentic_resume_builder.config import OllamaConfig
from agentic_resume_builder.exceptions import (
    ModelNotFoundError,
    OllamaConnectionError,
)

logger = logging.getLogger(__name__)


class OllamaConnectionManager:
    """Manages connection to Ollama and validates configuration.
    
    This class ensures that:
    - Ollama is available and running
    - The specified model exists or suggests alternatives
    - All processing remains local (no external API calls)
    """

    def __init__(self, config: OllamaConfig):
        """Initialize the Ollama connection manager.
        
        Args:
            config: Ollama configuration with base_url, model, etc.
            
        Raises:
            OllamaConnectionError: If Ollama is not available
            ModelNotFoundError: If the specified model is not found
        """
        self.config = config
        self._client: Optional[Client] = None
        self._available_models: Optional[List[str]] = None
        
        # Validate connection and model on initialization
        self._validate_connection()
        self._validate_model()
        
    def _validate_connection(self) -> None:
        """Check if Ollama is available at the configured URL.
        
        Raises:
            OllamaConnectionError: If connection fails
        """
        # Verify the base_url is local first (before any network calls)
        if not self._is_local_endpoint(self.config.base_url):
            raise OllamaConnectionError(
                self.config.base_url,
                "Only local endpoints are allowed. Use http://localhost:11434 or http://127.0.0.1:11434"
            )
        
        try:
            # Create client and test connection
            self._client = Client(host=self.config.base_url)
            
            # Try to list models to verify connection
            self._client.list()
            
            logger.info(f"Successfully connected to Ollama at {self.config.base_url}")
            
        except ollama.ResponseError as e:
            raise OllamaConnectionError(
                self.config.base_url,
                f"Ollama server error: {str(e)}"
            )
        except Exception as e:
            # Provide helpful installation instructions
            error_msg = (
                f"Could not connect to Ollama at {self.config.base_url}. "
                "Please ensure Ollama is installed and running.\n\n"
                "Installation instructions:\n"
                "- macOS/Linux: Visit https://ollama.ai/download\n"
                "- After installation, run: ollama serve\n"
                "- Pull a model: ollama pull llama3.2:3b"
            )
            raise OllamaConnectionError(self.config.base_url, error_msg)
    
    def _is_local_endpoint(self, url: str) -> bool:
        """Verify that the endpoint is local only.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if the URL is a local endpoint, False otherwise
        """
        url_lower = url.lower()
        local_indicators = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "[::1]",  # IPv6 localhost
        ]
        
        return any(indicator in url_lower for indicator in local_indicators)
    
    def _validate_model(self) -> None:
        """Validate that the specified model exists.
        
        Raises:
            ModelNotFoundError: If the model is not found
        """
        try:
            # Get list of available models
            models_response = self._client.list()
            self._available_models = [model['name'] for model in models_response.get('models', [])]
            
            # Check if the configured model exists
            # Model names might have tags like "llama3.2:3b" or "llama3.2:latest"
            model_found = False
            for available_model in self._available_models:
                # Check exact match or base name match
                if (self.config.model == available_model or 
                    self.config.model == available_model.split(':')[0] or
                    available_model.startswith(f"{self.config.model}:")):
                    model_found = True
                    break
            
            if not model_found:
                # Suggest alternatives
                suggestions = self._suggest_alternative_models()
                raise ModelNotFoundError(
                    self.config.model,
                    available_models=suggestions
                )
            
            logger.info(f"Model '{self.config.model}' is available")
            
        except ModelNotFoundError:
            raise
        except Exception as e:
            logger.warning(f"Could not validate model: {e}")
            # Don't fail if we can't validate, but log the warning
    
    def _suggest_alternative_models(self) -> List[str]:
        """Suggest alternative models based on what's available.
        
        Returns:
            List of suggested model names
        """
        if not self._available_models:
            return ["llama3.2:3b", "llama3.2", "mistral", "codellama"]
        
        # Return available models, prioritizing common ones
        preferred_models = ["llama3.2:3b", "llama3.2", "llama3", "mistral", "codellama", "phi"]
        suggestions = []
        
        # First add preferred models that are available
        for preferred in preferred_models:
            for available in self._available_models:
                if available.startswith(preferred):
                    suggestions.append(available)
                    break
        
        # Then add any other available models
        for model in self._available_models:
            if model not in suggestions:
                suggestions.append(model)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_client(self) -> Client:
        """Get the Ollama client instance.
        
        Returns:
            Configured Ollama client
            
        Raises:
            OllamaConnectionError: If client is not initialized
        """
        if self._client is None:
            raise OllamaConnectionError(
                self.config.base_url,
                "Client not initialized"
            )
        return self._client
    
    def get_available_models(self) -> List[str]:
        """Get list of available models.
        
        Returns:
            List of model names
        """
        if self._available_models is None:
            try:
                models_response = self._client.list()
                self._available_models = [
                    model['name'] for model in models_response.get('models', [])
                ]
            except Exception as e:
                logger.warning(f"Could not fetch available models: {e}")
                return []
        
        return self._available_models
    
    def verify_local_processing(self) -> bool:
        """Verify that all processing is local.
        
        This method confirms that the configured endpoint is local
        and no external API calls will be made.
        
        Returns:
            True if processing is guaranteed to be local
        """
        return self._is_local_endpoint(self.config.base_url)
    
    def test_generation(self, prompt: str = "Hello") -> str:
        """Test model generation with a simple prompt.
        
        Args:
            prompt: Test prompt to send to the model
            
        Returns:
            Generated response text
            
        Raises:
            OllamaConnectionError: If generation fails
        """
        try:
            response = self._client.generate(
                model=self.config.model,
                prompt=prompt,
                options={
                    'temperature': self.config.temperature,
                }
            )
            return response.get('response', '')
        except Exception as e:
            raise OllamaConnectionError(
                self.config.base_url,
                f"Generation test failed: {str(e)}"
            )
