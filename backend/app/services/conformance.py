"""Deterministic conformance analysis engine for Claude Code plugin manifests.

The engine inspects a plugin manifest (the merged contents of marketplace.json,
``.lsp.json`` and plugin.json) and returns a reproducible quality score plus
structured findings. No LLM, no network, no randomness.

Check catalogue:
    source.format          — ``source`` must be a valid ``owner/repo`` ref
    lsp.config_present     — ``lspServers`` without a ``.lsp.json`` (``lspConfig``)
    plugin.required_fields — name, description, source must be present
    plugin.description_quality — description must be substantive
    plugin.type_consistency — ``plugin_type == lsp`` implies ``lspServers``
    security.token_scan    — recursive scan for credential-shaped values
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from ..core.security import scan_string

GITHUB_SOURCE_RE = re.compile(r"^[A-Za-z0-9.-]{1,39}/[A-Za-z0-9._-]{1,100}$")

MIN_DESCRIPTION_LEN = 20
PLACEHOLDER_DESCRIPTIONS = frozenset(
    {"todo", "placeholder", "lorem ipsum", "coming soon", "tbd"}
)


class Severity(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class Finding:
    check_id: str
    severity: Severity
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    score: int
    band: str
    findings: list[Finding]
    checks_run: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "band": self.band,
            "findings": [
                {
                    "check_id": f.check_id,
                    "severity": f.severity.value,
                    "message": f.message,
                    "evidence": f.evidence,
                }
                for f in self.findings
            ],
            "checks_run": self.checks_run,
        }


# --- Score weights ---
WEIGHTS: dict[Severity, int] = {Severity.FAIL: 25, Severity.WARN: 10, Severity.PASS: 0}


def compute_score(findings: list[Finding]) -> int:
    score = 100
    for f in findings:
        score -= WEIGHTS[f.severity]
    return max(0, min(100, score))


def score_band(score: int) -> str:
    if score >= 90:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 50:
        return "needs_review"
    return "poor"


# --- Individual checks ---

def check_source_format(manifest: dict[str, Any]) -> list[Finding]:
    """Validate ``source`` is a valid GitHub ``owner/repo`` reference."""
    source = manifest.get("source", "")
    if not source or not isinstance(source, str):
        return [
            Finding(
                "source.format",
                Severity.FAIL,
                "Missing 'source': a GitHub owner/repo reference is required.",
                {"field": "source", "value": str(source)[:80]},
            )
        ]
    if not GITHUB_SOURCE_RE.match(source):
        return [
            Finding(
                "source.format",
                Severity.FAIL,
                f"Source '{source[:40]}' is not a valid owner/repo reference "
                "(expected 'owner/repo').",
                {"field": "source", "value": source[:80], "pattern": "owner/repo"},
            )
        ]
    return []


def check_lsp_config(manifest: dict[str, Any]) -> list[Finding]:
    """If ``lspServers`` is declared, a ``.lsp.json`` (``lspConfig``) must accompany it."""
    config = manifest.get("config", {})
    if not isinstance(config, dict):
        return []
    lsp_servers = config.get("lspServers")
    if lsp_servers is None:
        return []  # Not an LSP plugin — nothing to check.

    lsp_config = config.get("lspConfig")
    if isinstance(lsp_config, dict):
        return []  # .lsp.json present — pass.

    servers = list(lsp_servers.keys()) if isinstance(lsp_servers, dict) else []
    return [
        Finding(
            "lsp.config_present",
            Severity.WARN,
            "LSP servers declared in marketplace.json but no .lsp.json config "
            "(lspConfig) present. Installed plugins will omit LSP configuration.",
            {"lsp_servers": servers[:5], "missing_field": "lspConfig"},
        )
    ]


def check_required_fields(manifest: dict[str, Any]) -> list[Finding]:
    """Verify required top-level fields: name, description, source."""
    findings: list[Finding] = []
    for name in ("name", "description", "source"):
        val = manifest.get(name)
        if not val or (isinstance(val, str) and not val.strip()):
            findings.append(
                Finding(
                    f"plugin.{name}",
                    Severity.WARN,
                    f"Required field '{name}' is missing or empty.",
                    {"field": name, "value": str(val)[:80] if val else None},
                )
            )
    return findings


def check_description_quality(manifest: dict[str, Any]) -> list[Finding]:
    """Description must be substantive, not a placeholder."""
    desc = manifest.get("description", "")
    if not desc or not isinstance(desc, str):
        return []
    stripped = desc.strip()
    if len(stripped) < MIN_DESCRIPTION_LEN:
        return [
            Finding(
                "plugin.description_quality",
                Severity.WARN,
                f"Description is too short ({len(stripped)} chars); "
                f"recommend >= {MIN_DESCRIPTION_LEN}.",
                {"field": "description", "length": len(stripped)},
            )
        ]
    if stripped.lower() in PLACEHOLDER_DESCRIPTIONS:
        return [
            Finding(
                "plugin.description_quality",
                Severity.WARN,
                "Description appears to be a placeholder.",
                {"field": "description", "value": stripped[:40]},
            )
        ]
    return []


def check_type_consistency(manifest: dict[str, Any]) -> list[Finding]:
    """If ``plugin_type`` is 'lsp', the config should declare ``lspServers``."""
    ptype = manifest.get("plugin_type", "other")
    config = manifest.get("config", {})
    if not isinstance(config, dict):
        return []
    if ptype == "lsp" and not config.get("lspServers"):
        return [
            Finding(
                "plugin.type_consistency",
                Severity.WARN,
                "Plugin type is 'lsp' but no lspServers declared in config.",
                {"plugin_type": ptype, "has_lspServers": False},
            )
        ]
    return []


def check_token_scan(manifest: dict[str, Any]) -> list[Finding]:
    """Recursively scan all string values for credential-shaped patterns."""
    findings: list[Finding] = []

    def walk(obj: Any, path: str = "root") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")
        elif isinstance(obj, str):
            hits = scan_string(obj)
            if hits:
                findings.append(
                    Finding(
                        "security.token_scan",
                        Severity.FAIL,
                        f"Potential credential pattern detected ({', '.join(hits)}).",
                        {"path": path, "patterns": hits},
                    )
                )

    walk(manifest)
    return findings


# Registry of all checks. New checks append to this list.
CHECKS: list[Callable[[dict[str, Any]], list[Finding]]] = [
    check_source_format,
    check_lsp_config,
    check_required_fields,
    check_description_quality,
    check_type_consistency,
    check_token_scan,
]


def analyze(manifest: dict[str, Any]) -> AnalysisResult:
    """Run every registered check against *manifest* and aggregate the score."""
    findings: list[Finding] = []
    checks_run: list[str] = []
    for check in CHECKS:
        checks_run.append(check.__name__)
        findings.extend(check(manifest))
    score = compute_score(findings)
    return AnalysisResult(
        score=score,
        band=score_band(score),
        findings=findings,
        checks_run=checks_run,
    )