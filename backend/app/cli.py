#!/usr/bin/env python3
"""Command-line interface for Nexus Lens.

Provides a reproducible entry point for the deterministic conformance engine:

    python -m app.cli analyze-manifest <manifest.json>

No LLM key or network access required — the offline engine scores the manifest
and prints structured findings.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .services.conformance import analyze


def _cmd_analyze_manifest(file_path: str) -> int:
    path = Path(file_path)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    try:
        manifest = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON — {exc}", file=sys.stderr)
        return 2

    if not isinstance(manifest, dict):
        print("error: manifest must be a JSON object", file=sys.stderr)
        return 2

    result = analyze(manifest)
    print(json.dumps(result.to_dict(), indent=2, default=str))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexus-lens",
        description="Nexus Lens — Claude Code plugin conformance CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_analyze = sub.add_parser(
        "analyze-manifest",
        help="Run deterministic conformance analysis on a plugin manifest JSON file.",
    )
    p_analyze.add_argument("file", help="Path to a plugin manifest JSON file")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "analyze-manifest":
        return _cmd_analyze_manifest(args.file)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())