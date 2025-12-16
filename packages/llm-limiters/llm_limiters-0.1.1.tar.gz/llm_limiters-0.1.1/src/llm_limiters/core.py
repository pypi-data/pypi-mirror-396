import time
import functools
from collections import deque
from threading import Lock
from typing import List, Dict, Deque, Tuple, Callable, Any
import re
import logging
from .constants import GEMINI_API_LIMITS, OPENAI_API_LIMITS

logger = logging.getLogger(__name__)

class RateLimitExceededError(Exception):
    pass
class ModelNotFoundError(Exception):
    pass

class RateLimiter:
    def __init__(self, tier: str = "free", custom_limits: Dict[str, Dict[str, int]] = None):
        if tier not in GEMINI_API_LIMITS:
            raise ValueError(f"Invalid tier '{tier}'. Available tiers: {list(GEMINI_API_LIMITS.keys())}")
        self.tier = tier
        self.limits = {
            **GEMINI_API_LIMITS[tier],
            **OPENAI_API_LIMITS.get(tier, {}),
            **(custom_limits or {})
        }
        self._lock = Lock()
        self.request_logs: Dict[str, Deque[float]] = {model: deque() for model in self.limits}
        self.token_logs: Dict[str, Deque[Tuple[float, int]]] = {model: deque() for model in self.limits}
        self.model_cooldowns: Dict[str, float] = {}

    def _prune_logs(self, model: str, current_time: float):
        while self.request_logs[model] and current_time - self.request_logs[model][0] > 60:
            self.request_logs[model].popleft()
        while self.token_logs[model] and current_time - self.token_logs[model][0][0] > 60:
            self.token_logs[model].popleft()

    def _check_capacity(self, model: str) -> Tuple[bool, str]:
        if model not in self.limits:
            raise ModelNotFoundError(f"Model '{model}' not found for tier '{self.tier}'.")

        with self._lock:
            current_time = time.time()
            self._prune_logs(model, current_time)

            rpm_limit = self.limits[model]["rpm"]
            if len(self.request_logs[model]) >= rpm_limit:
                return (False, f"RPM limit of {rpm_limit} reached")

            tpm_limit = self.limits[model]["tpm"]
            used_tokens_last_minute = sum(t for ts, t in self.token_logs[model])
            if used_tokens_last_minute >= tpm_limit:
                return (False, f"TPM limit of {tpm_limit} reached")

            rpd_limit = self.limits[model]["rpd"]
            day_ago = current_time - 86400
            rpd_count = sum(1 for ts in self.request_logs[model] if ts > day_ago)
            if rpd_count >= rpd_limit:
                return (False, f"RPD limit of {rpd_limit} reached")

            return (True, "Capacity available")


    def _update_usage(self, model: str, tokens_used: int):
        with self._lock:
            current_time = time.time()
            self.request_logs[model].append(current_time)
            self.token_logs[model].append((current_time, tokens_used))

    def _extract_tokens_used(self, response):
        # --- OpenAI format ---
        if hasattr(response, "usage") and response.usage:
            if hasattr(response.usage, "total_tokens"):
                return response.usage.total_tokens
            if isinstance(response.usage, dict) and "total_tokens" in response.usage:
                return response.usage["total_tokens"]

        # --- Gemini format ---
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            if hasattr(response.usage_metadata, "total_token_count"):
                return response.usage_metadata.total_token_count
            if isinstance(response.usage_metadata, dict) and "totalTokenCount" in response.usage_metadata:
                return response.usage_metadata["totalTokenCount"]
        return 0

    def limit(self, model_priority: List[str]):
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                current_time = time.time()
                for model in model_priority:
                    if model in self.model_cooldowns and current_time < self.model_cooldowns.get(model, 0):
                        logger.info(f"Model '{model}' is in cooldown. Skipping.")
                        continue
                    
                    capacity_available, reason = self._check_capacity(model)
                    if capacity_available:
                        try:
                            kwargs['model_name'] = model
                            response = func(*args, **kwargs)
                            tokens_used = self._extract_tokens_used(response)
                            self._update_usage(model, tokens_used)
                            return response
                        except Exception as e:
                            msg = str(e)

                            status_code = getattr(e, "status_code", None)
                            error_code  = getattr(e, "code", None)

                            is_rate_limit = (
                                status_code == 429
                                or error_code in ("rate_limit_exceeded", "quota_exceeded", "resource_exhausted")
                                or any(k in msg for k in [
                                    "429",
                                    "rateLimitExceeded",
                                    "RESOURCE_EXHAUSTED",
                                    "Quota",
                                    "Rate limit reached",
                                    "Too many requests",
                                    "You exceeded your current quota",
                                    "Please try again in",
                                ])
                            )

                            if is_rate_limit:
                                retry_after = 30
                                match = re.search(r"'retryDelay': '(\d+)s'", msg)
                                if match:
                                    retry_after = int(match.group(1)) + 1800

                                self.model_cooldowns[model] = time.time() + retry_after
                                continue

                            # NOT a rate-limit error → fail immediately
                            raise

                raise RateLimitExceededError(f"All models in priority list {model_priority} are rate-limited or unavailable.")
            return wrapper
        return decorator
    
RATE_LIMITER = RateLimiter(tier="free")