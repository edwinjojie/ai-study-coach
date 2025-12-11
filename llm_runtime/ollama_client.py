import requests
import json
from utilities.llm_parsers import safe_parse_json

class OllamaClient:
    """
    A simple client for interacting with the Ollama API.
    """
    def __init__(self, model="llama3.1:8b", base_url="http://localhost:11434/api/generate", timeout=120):
        """
        Initialize the Ollama client.

        Args:
            model (str): The model name to use (default: "llama3.1:8b").
            base_url (str): The API endpoint URL (default: "http://localhost:11434/api/generate").
            timeout (int): Request timeout in seconds (default: 120).
        """
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def ask(self, prompt: str, max_tokens: int = 1024) -> str:
        """
        Send a prompt to the Ollama model and return the generated text.

        Args:
            prompt (str): The input prompt.
            max_tokens (int): Maximum tokens to generate (default: 1024).

        Returns:
            str: The generated response text.

        Raises:
            requests.RequestException: If the HTTP request fails.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.RequestException as e:
            return f"Error connecting to LLM: {str(e)}"

    def ask_json(self, prompt: str, schema_key: str = None) -> dict:
        """
        Send a prompt and attempt to parse the response as JSON.

        Args:
            prompt (str): The input prompt.
            schema_key (str, optional): Not used in simple implementation but reserved for schema validation.

        Returns:
            dict: The parsed JSON object or {"_raw": text} if parsing fails.
        """
        text = self.ask(prompt)
        return safe_parse_json(text)
