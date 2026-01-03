import httpx
import logging
from typing import Any
from config.settings import settings

logger = logging.getLogger(__name__)

class GroqClient:
    """Minimal Groq API wrapper exposing an `invoke(prompt)` method compatible
    with the rest of the codebase. It performs a simple POST to the configured
    Groq API URL and returns an object with a `.content` attribute containing
    the model response text.

    NOTE: Set `GROQ_API_KEY` and `GROQ_API_URL` in your .env before using.
    """

    def __init__(self):
        self.api_key = settings.groq_api_key
        self.api_url = settings.groq_api_url
        if not self.api_key or not self.api_url:
            logger.warning("GroqClient created without API key or URL configured")

    def invoke(self, prompt: str) -> Any:
        if not self.api_key or not self.api_url:
            raise RuntimeError("Groq API key or URL not configured (set GROQ_API_KEY and GROQ_API_URL)")

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        # Use proper Groq/OpenAI-compatible chat completion format
        payload = {
            "model": settings.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": settings.llm_temperature
        }

        # Use small timeout here; the outer invoke_llm_with_timeout will run this in a thread
        with httpx.Client(timeout=settings.llm_timeout + 5.0) as client:
            resp = client.post(self.api_url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error(f"Groq API error {resp.status_code}: {resp.text}")
            resp.raise_for_status()
            # Try JSON response first
            try:
                j = resp.json()
                # Common Groq shapes vary; try to find text content
                if isinstance(j, dict):
                    # Look for fields commonly used: 'output', 'text', 'content', 'choices'
                    if 'output' in j:
                        content = j['output']
                        if isinstance(content, list):
                            content = ''.join(str(x) for x in content)
                        return SimpleResp(content)
                    if 'text' in j:
                        return SimpleResp(j['text'])
                    if 'content' in j:
                        return SimpleResp(j['content'])
                    if 'choices' in j and isinstance(j['choices'], list) and j['choices']:
                        # Try common choice shape (OpenAI/Groq format)
                        c = j['choices'][0]
                        if isinstance(c, dict) and 'message' in c:
                            msg = c['message']
                            if isinstance(msg, dict):
                                return SimpleResp(msg.get('content') or '')
                            return SimpleResp(str(msg))
                        if isinstance(c, dict) and 'text' in c:
                            return SimpleResp(c.get('text') or '')
                # Fallback to text
            except Exception:
                logger.debug("Groq response not JSON, falling back to text")

            return SimpleResp(resp.text)


class SimpleResp:
    def __init__(self, content: str):
        self.content = content
