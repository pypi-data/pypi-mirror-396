GEMINI_LIVE_LIMITS = {
    "free": {
        "gemini-2.0-flash-live-001": {"rpm": 10, "tpm": 1_000_000, "rpd": 200}, 
    },
    "tier1": {
        "gemini-2.0-flash-live-001": {"rpm": 50, "tpm": 4_000_000, "rpd": 10_000},
    },
    "tier2": {
        "gemini-2.0-flash-live-001": {"rpm": 1_000, "tpm": 10_000_000, "rpd": 50_000},
    },
    "tier3": {
        "gemini-2.0-flash-live-001": {"rpm": 5_000, "tpm": 100_000_000, "rpd": float('inf')},
    }
}

GEMINI_API_LIMITS = {
    "free": {
        "gemini-2.5-pro": {"rpm": 5, "tpm": 250_000, "rpd": 100},
        "gemini-2.5-flash": {"rpm": 10, "tpm": 250_000, "rpd": 250},
        "gemini-2.5-flash-lite": {"rpm": 15, "tpm": 250_000, "rpd": 1_000},
        "gemini-2.0-flash": {"rpm": 15, "tpm": 1_000_000, "rpd": 200},
        "gemini-2.0-flash-lite": {"rpm": 30, "tpm": 1_000_000, "rpd": 200},
    },
    "tier1": {
        "gemini-2.5-pro": {"rpm": 150, "tpm": 2_000_000, "rpd": 10_000},
        "gemini-2.5-flash": {"rpm": 1_000, "tpm": 1_000_000, "rpd": 10_000},
        "gemini-2.5-flash-lite": {"rpm": 4_000, "tpm": 4_000_000, "rpd": float('inf')},
        "gemini-2.0-flash": {"rpm": 2_000, "tpm": 4_000_000, "rpd": float('inf')},
        "gemini-2.0-flash-lite": {"rpm": 4_000, "tpm": 4_000_000, "rpd": float('inf')},
    },
    "tier2": {
        "gemini-2.5-pro": {"rpm": 1_000, "tpm": 5_000_000, "rpd": 50_000},
        "gemini-2.5-flash": {"rpm": 2_000, "tpm": 3_000_000, "rpd": 100_000},
        "gemini-2.5-flash-lite": {"rpm": 10_000, "tpm": 10_000_000, "rpd": float('inf')},
        "gemini-2.0-flash": {"rpm": 10_000, "tpm": 10_000_000, "rpd": float('inf')},
        "gemini-2.0-flash-lite": {"rpm": 20_000, "tpm": 10_000_000, "rpd": float('inf')},
    },
    "tier3": {
        "gemini-2.5-pro": {"rpm": 2_000, "tpm": 8_000_000, "rpd": float('inf')},
        "gemini-2.5-flash": {"rpm": 10_000, "tpm": 8_000_000, "rpd": float('inf')},
        "gemini-2.5-flash-lite": {"rpm": 30_000, "tpm": 30_000_000, "rpd": float('inf')},
        "gemini-2.0-flash": {"rpm": 30_000, "tpm": 30_000_000, "rpd": float('inf')},
        "gemini-2.0-flash-lite": {"rpm": 30_000, "tpm": 30_000_000, "rpd": float('inf')},
    }
}

OPENAI_API_LIMITS = {
    "free": {
        "gpt-4o-mini": {"rpm": 50, "tpm": 200000, "rpd": float("inf")},
        "gpt-4.1": {"rpm": 30, "tpm": 300000, "rpd": float("inf")},
        "gpt-4o": {"rpm": 15, "tpm": 300000, "rpd": float("inf")},
    },
    "tier1": {
        "gpt-4o-mini": {"rpm": 200, "tpm": 2000000, "rpd": float("inf")},
        "gpt-4.1": {"rpm": 150, "tpm": 2000000, "rpd": float("inf")},
        "gpt-4o": {"rpm": 80, "tpm": 2000000, "rpd": float("inf")},
    },
}