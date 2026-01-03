import asyncio
import logging
import time
import json
from typing import Any
from config.settings import settings

logger = logging.getLogger(__name__)


async def invoke_llm_with_timeout(llm: Any, prompt: str, timeout: float | None = None) -> Any:
    """Invoke a blocking LLM call in a thread with a timeout.

    Runs `llm.invoke(prompt)` inside a thread to avoid blocking the event loop,
    and enforces a timeout so HTTP handlers don't hang indefinitely.
    Raises TimeoutError on timeout. The default timeout will come from settings.llm_timeout.
    """
    timeout = timeout if timeout is not None else settings.llm_timeout
    start = time.time()
    logger.debug("LLM invoke start: timeout=%s, prompt_len=%d", timeout, len(prompt) if isinstance(prompt, str) else 0)

    try:
        result = await asyncio.wait_for(asyncio.to_thread(lambda: llm.invoke(prompt)), timeout)
        duration = time.time() - start
        logger.info("LLM invoke completed in %.2fs", duration)

        # Normalize and handle streamed NDJSON responses from streaming LLM providers
        try:
            raw_text = None
            if hasattr(result, 'text'):
                raw_text = result.text
            elif hasattr(result, 'content'):
                raw_text = result.content
            else:
                raw_text = str(result)

            if isinstance(raw_text, bytes):
                raw_text = raw_text.decode('utf-8', errors='ignore')

            # If response appears to be NDJSON stream, parse lines and concatenate assistant content
            combined = None
            if isinstance(raw_text, str) and '\n' in raw_text and '"message"' in raw_text:
                pieces = []
                for line in raw_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    # Support structure: {"message": {"role": "assistant", "content": "..."}, ...}
                    msg = obj.get('message') if isinstance(obj.get('message'), dict) else None
                    if msg and msg.get('role') == 'assistant':
                        content_piece = msg.get('content') or ''
                        pieces.append(content_piece)
                if pieces:
                    combined = ''.join(pieces)

            # Log preview
            if combined:
                logger.debug("LLM combined NDJSON preview: %s", combined[:1000])
                class SimpleResp:
                    pass
                resp = SimpleResp()
                resp.content = combined
                return resp
            else:
                # Fallback: log preview and return original result
                try:
                    preview = raw_text[:1000] if isinstance(raw_text, str) else str(raw_text)[:1000]
                    logger.debug("LLM result preview: %s", preview)
                except Exception:
                    logger.exception("Failed to log LLM result preview")
                return result
        except Exception:
            logger.exception("Error normalizing LLM result")
            return result
    except asyncio.TimeoutError as e:
        duration = time.time() - start
        logger.warning("LLM invocation timed out after %.2fs (configured %ss)", duration, timeout)
        raise TimeoutError(f"LLM invocation timed out after {timeout} seconds") from e
