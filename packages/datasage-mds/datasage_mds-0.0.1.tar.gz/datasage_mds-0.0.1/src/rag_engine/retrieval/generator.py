from typing import List, Dict, Any
import json
import urllib.request
import urllib.error
from .data_models import Document

class GenerationError(Exception):
    """
    Custom exception for generation errors.
    """
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error

class Ollama:
    """
    A simple Ollama client to connect to Ollama.
    """
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def complete(self, prompt: str) -> str:
        """
        Structure an instruction prompt for the LLM.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise GenerationError(f"Ollama API returned status {response.status}")
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError as e:
            raise GenerationError(f"Failed to connect to Ollama at {self.base_url}: {e}", original_error=e)
        except Exception as e:
            raise GenerationError(f"An unexpected error occurred during generation: {e}", original_error=e)

class LLMGenerator:
    def __init__(self, model: str = "llama3.1"):
        self.llm = Ollama(model=model)

    def generate_answer(self, question: str, context_docs: List[Document]) -> str:
        """
        Generate an answer to a question using the LLM.
        """
        try:
            context_str = "\n\n".join(
                f"Source: {doc.metadata}\nContent: {doc.page_content}" 
                for doc in context_docs
            )
            prompt = f"Use the following context to answer the question:\n\n{context_str}\n\nQuestion: {question}\nAnswer:"
            
            response = self.llm.complete(prompt)
            return str(response)
        except Exception as e:
            raise GenerationError(f"Failed to generate answer: {e}", original_error=e)

    def summarize_docs(self, docs: List[Document]) -> str:
        """
        Generate a bullet-point summary from a list of documents.
        """
        try:
            context_str = "\n\n".join(doc.page_content for doc in docs)
            prompt = f"Summarize the following text in concise bullet points:\n\n{context_str}\n\nSummary:"
            return self.llm.complete(prompt)
        except Exception as e:
            raise GenerationError(f"Failed to summarize documents: {e}", original_error=e)

    def evaluate_relevance(self, question: str, answer: str) -> str:
        """
        Ask the LLM to rate the relevance of the answer to the question.
        """
        try:
            prompt = (
                f"Question: {question}\n"
                f"Answer: {answer}\n\n"
                "Rate the relevance of the answer to the question on a scale of 1 to 10. "
                "Provide a brief explanation for your rating."
            )
            return self.llm.complete(prompt)
        except Exception as e:
            raise GenerationError(f"Failed to evaluate relevance: {e}", original_error=e)