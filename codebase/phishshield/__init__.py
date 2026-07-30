"""PhishShield AI — explainable phishing-email detection (hackathon MVP).

Intended pipeline:  ingest -> header_checks (deterministic) -> LLM reasoning
(one real AI call) -> aggregate -> verdict.

Work in progress: only `config.py` exists so far. `ingest.py`, `header_checks.py`,
`provider.py`, `prompts.py` and `analyze.py` are still to be built — see CLAUDE.md.
Nothing is re-exported yet so importing this package stays side-effect free.
"""

__all__ = []
