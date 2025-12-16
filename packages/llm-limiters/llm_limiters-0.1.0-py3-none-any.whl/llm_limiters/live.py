import time
import asyncio
import logging
from collections import deque
from typing import Dict, Deque, Tuple
from src.llm_limiters.constants import GEMINI_LIVE_LIMITS

logger = logging.getLogger(__name__)

class LiveRateLimiter:
    def __init__(self, tier: str = "free"):
        self.tier = tier if tier in GEMINI_LIVE_LIMITS else "free"
        self.limits = GEMINI_LIVE_LIMITS[self.tier]
        
        # Async Lock to prevent race conditions between WebSocket connections
        self._lock = asyncio.Lock()
        
        # Storage for logs
        # request_logs: Stores timestamp of when a session started
        self.request_logs: Dict[str, Deque[float]] = {m: deque() for m in self.limits}
        
        # token_logs: Stores (timestamp, token_count)
        self.token_logs: Dict[str, Deque[Tuple[float, int]]] = {m: deque() for m in self.limits}
        
        # Cooldowns for when Google sends 429 errors
        self.model_cooldowns: Dict[str, float] = {}

    def _prune_logs(self, model: str, current_time: float):
        """Removes logs older than 60 seconds to keep the window accurate."""
        # Prune Requests (RPM)
        while self.request_logs[model] and current_time - self.request_logs[model][0] > 60:
            self.request_logs[model].popleft()
        
        # Prune Tokens (TPM)
        while self.token_logs[model] and current_time - self.token_logs[model][0][0] > 60:
            self.token_logs[model].popleft()

    async def check_availability(self, model: str) -> Tuple[bool, str]:
        """
        Checks if a new session is allowed.
        Returns: (is_allowed: bool, reason: str)
        """
        if model not in self.limits:
            # If model isn't configured, we assume it's allowed (or you can block it)
            return True, "Model not tracked"

        async with self._lock:
            current_time = time.time()
            
            # 1. Check Cooldown (triggered by previous errors)
            if model in self.model_cooldowns:
                if current_time < self.model_cooldowns[model]:
                    return False, f"System in cooldown. Try again in {int(self.model_cooldowns[model] - current_time)}s"
                else:
                    del self.model_cooldowns[model]

            self._prune_logs(model, current_time)
            limits = self.limits[model]

            # 2. Check RPM (Sessions per minute)
            if len(self.request_logs[model]) >= limits["rpm"]:
                return False, f"Too many people connected (RPM Limit: {limits['rpm']})"

            # 3. Check TPM (Tokens per minute)
            used_tokens = sum(t for ts, t in self.token_logs[model])
            if used_tokens >= limits["tpm"]:
                return False, f"System overloaded (TPM Limit: {limits['tpm']})"

            # 4. Check RPD (Sessions per day)
            day_ago = current_time - 86400
            daily_requests = sum(1 for ts in self.request_logs[model] if ts > day_ago)
            if daily_requests >= limits["rpd"]:
                return False, f"Daily limit reached ({limits['rpd']})"

            return True, "OK"

    async def acquire_session(self, model: str):
        """Records that a session has started (Increments RPM)."""
        if model not in self.limits: return
        async with self._lock:
            self.request_logs[model].append(time.time())

    async def record_token_usage(self, model: str, token_count: int):
        """Records token usage during the session (Increments TPM)."""
        if model not in self.limits or token_count <= 0: return
        async with self._lock:
            self.token_logs[model].append((time.time(), token_count))

    async def trigger_cooldown(self, model: str, wait_seconds: int = 60):
        """Blocks the model for a set time (used when Google returns 429)."""
        async with self._lock:
            self.model_cooldowns[model] = time.time() + wait_seconds

# Initialize the limiter
# Change "free" to "tier1", "tier2", etc. as needed
LIVE_LIMITER = LiveRateLimiter(tier="free")