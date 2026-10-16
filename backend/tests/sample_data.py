"""Reusable sample manifests for tests.

Tokens used in fixtures are constructed at runtime (prefix + repeated char)
per security-fixture policy — never pasted as literals.
"""

from __future__ import annotations

# A fully conformant manifest — should score 100 / "excellent".
CLEAN_MANIFEST: dict = {
    "name": "typescript-lsp",
    "description": "Language Server Protocol plugin for TypeScript with "
    "go-to-definition, hover, and reference support.",
    "source": "anthropics/claude-plugins-official",
    "plugin_type": "lsp",
    "config": {
        "lspServers": {
            "typescript": {
                "command": "typescript-language-server",
                "args": ["--stdio"],
                "extensionToLanguage": {".ts": "typescript"},
            }
        },
        "lspConfig": {
            "plugin": {"pluginId": "typescript-lsp", "name": "TypeScript LSP"},
        },
    },
}

# No .lsp.json for an LSP plugin — should produce a WARN.
LSP_MISSING_CONFIG: dict = {
    "name": "gopls-lsp",
    "description": "Go language server plugin for Claude Code.",
    "source": "anthropics/claude-plugins-official",
    "plugin_type": "lsp",
    "config": {
        "lspServers": {
            "go": {"command": "gopls", "args": ["--stdio"]},
        },
        # lspConfig intentionally absent → issue 379 class
    },
}

# Invalid source format — should produce a FAIL.
BAD_SOURCE_MANIFEST: dict = {
    "name": "broken-plugin",
    "description": "A plugin with an invalid source reference.",
    "source": "anthropics/claude-plugins-official/.claude-plugin/marketplace.json",
    "plugin_type": "mcp",
}

# Missing required fields, short description, LSP type without lspServers.
INCOMPLETE_MANIFEST: dict = {
    "name": "",
    "description": "x",
    "source": "",
    "plugin_type": "lsp",
    "config": {},
}


def manifest_with_synthetic_token() -> dict:
    """Return a manifest containing a runtime-constructed fake credential.

    The token is built from a provider prefix plus 36 zero characters — it is
    clearly synthetic and never a real credential.
    """
    fake_token = "ghp_" + "0" * 36  # synthetic: prefix + repeated zero char
    return {
        "name": "leaky-plugin",
        "description": "Plugin that accidentally embeds a key in its manifest.",
        "source": "owner/repo",
        "plugin_type": "mcp",
        "config": {"secret": fake_token},
    }


def plugin_create_payload(manifest: dict) -> dict:
    """Build a full POST /plugins payload from a raw manifest dict."""
    return {
        "name": manifest.get("name") or "plugin",
        "description": manifest.get("description") or "A plugin.",
        "source": manifest.get("source") or "owner/repo",
        "plugin_type": manifest.get("plugin_type") or "other",
        "manifest": manifest,
    }