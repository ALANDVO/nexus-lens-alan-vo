"""Security utilities: credential scanning patterns and redaction helpers.

No real credentials are ever embedded. Patterns are generic detectors used by
the conformance engine's ``security.token_scan`` check.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPattern:
    name: str
    regex: re.Pattern[str]
    description: str


# Generic credential detectors — applied to arbitrary manifest strings so that
# plugins do not accidentally publish leaked keys.
TOKEN_PATTERNS: list[TokenPattern] = [
    TokenPattern(
        "github_pat",
        re.compile(r"github_pat_[A-Za-z0-9_]{20,}", re.IGNORECASE),
        "GitHub fine-grained personal access token",
    ),
    TokenPattern(
        "github_short",
        re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}", re.IGNORECASE),
        "GitHub OAuth / classic token",
    ),
    TokenPattern(
        "openai",
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        "OpenAI-style API key",
    ),
    TokenPattern(
        "openrouter",
        re.compile(r"sk-or-v1-[a-f0-9]{32,}"),
        "OpenRouter API key",
    ),
    TokenPattern(
        "anthropic",
        re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"),
        "Anthropic API key",
    ),
    TokenPattern(
        "aws_access_key",
        re.compile(r"AKIA[0-9A-Z]{16}"),
        "AWS access key ID",
    ),
]

REDACTED = "REDACTED"


def redact_credentials(text: str) -> str:
    """Replace credential-pattern matches in *text* with ``REDACTED``."""
    result = text
    for pat in TOKEN_PATTERNS:
        result = pat.regex.sub(REDACTED, result)
    return result


def scan_string(value: str) -> list[str]:
    """Return the names of credential patterns found in *value*."""
    hits: list[str] = []
    for pat in TOKEN_PATTERNS:
        if pat.regex.search(value):
            hits.append(pat.name)
    return hits