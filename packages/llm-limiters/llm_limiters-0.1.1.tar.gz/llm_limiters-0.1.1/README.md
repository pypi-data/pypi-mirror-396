
# LLM Limiters

A lightweight, thread-safe, and async Python library to manage rate limits (RPM, TPM, RPD) for LLMs like Google Gemini and OpenAI.

## Installation

```bash
pip install llm-limiters
```

## Usage

### Standard Rate Limiter (Decorators)

```python
from llm_limiters import RateLimiter

limiter = RateLimiter(tier="free")

@limiter.limit(model_priority=["gemini-2.0-flash", "gpt-4o-mini"])
def call_llm(prompt, model_name=None):
    # Your API call here
    return response
```

### Live/WebSocket Limiter

```python
import asyncio
from llm_limiters import LiveRateLimiter

async def main():
    limiter = LiveRateLimiter(tier="tier1")
    
    allowed, reason = await limiter.check_availability("gemini-2.0-flash-live-001")
    if allowed:
        await limiter.acquire_session("gemini-2.0-flash-live-001")
        # Start websocket...
```
