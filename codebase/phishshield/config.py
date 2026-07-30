"""Configuration + shared paths. Loads codebase/.env if present."""
from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # dotenv is optional; env vars still work without it
    def load_dotenv(*_args, **_kwargs):
        return False

# codebase/ directory (parent of this package)
CODEBASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = CODEBASE_DIR.parent
WHITELIST_PATH = CODEBASE_DIR / "company_policy" / "domain-whitelist.json"
TRANSCRIPT_DIR = REPO_DIR / "eval" / "transcripts"

load_dotenv(CODEBASE_DIR / ".env")

MODEL = os.getenv("PHISHSHIELD_MODEL", "gpt-4o-mini")
# Mock is ON if explicitly forced, OR if there is simply no key to call with.
FORCE_MOCK = os.getenv("PHISHSHIELD_MOCK", "").strip() in {"1", "true", "True"}
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
USE_MOCK = FORCE_MOCK or not OPENAI_API_KEY


def load_whitelist() -> dict:
    """Company known-good directory — the grounding source for legitimacy checks."""
    with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
