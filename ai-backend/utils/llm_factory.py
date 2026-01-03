from utils.groq_client import GroqClient

def create_llm():
    """Return the configured LLM client. Default to Groq client only."""
    return GroqClient()