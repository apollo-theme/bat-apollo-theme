#!/usr/bin/env python3
"""Generate Apollo.tmTheme from the bundled palette snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE_PATH = ROOT / "palette" / "apollo.json"
OUTPUT_PATH = ROOT / "Apollo.tmTheme"
PALETTE_SHA256 = "550f8c36cf4ef6ac99551541d1fe9554f77d563fa1e7c129a6a82583321d61ef"


def load_palette() -> dict:
    raw = PALETTE_PATH.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != PALETTE_SHA256:
        raise ValueError(f"palette snapshot hash mismatch: {digest}")
    palette = json.loads(raw)
    if palette.get("id") != "apollo" or palette.get("schemaVersion") != 1:
        raise ValueError("unsupported Apollo palette snapshot")
    return palette


def resolve_role(palette: dict, role: str) -> str:
    reference = palette["roles"][role]
    if not (reference.startswith("{colors.") and reference.endswith("}")):
        raise ValueError(f"role {role!r} is not a color reference")
    return palette["colors"][reference[8:-1]]


def render(palette: dict) -> bytes:
    role = lambda name: resolve_role(palette, name)
    colors = palette["colors"]

    def rule(name: str, scope: str, foreground: str, font_style: str = "") -> dict:
        settings = {"foreground": foreground}
        if font_style:
            settings["fontStyle"] = font_style
        return {"name": name, "scope": scope, "settings": settings}

    theme = {
        "name": "Apollo",
        "author": "D0n9X1n",
        "semanticClass": "theme.dark.apollo",
        "settings": [
            {
                "settings": {
                    "background": role("canvas"),
                    "caret": role("cursor"),
                    "foreground": role("textPrimary"),
                    "invisibles": role("textInactive"),
                    "lineHighlight": colors["surface"],
                    "selection": role("selection"),
                    "selectionForeground": role("textPrimary"),
                }
            },
            rule("Comments", "comment, punctuation.definition.comment", role("textInactive"), "italic"),
            rule("Strings", "string, constant.other.symbol", role("success")),
            rule("Numbers and constants", "constant.numeric, constant.language, constant.character", colors["magenta"]),
            rule("Keywords", "keyword, storage.modifier", role("information")),
            rule("Operators", "keyword.operator, punctuation.separator, punctuation.terminator", role("textSecondary")),
            rule("Functions", "entity.name.function, support.function", role("focus")),
            rule("Parameters", "variable.parameter", colors["magenta"]),
            rule("Variables", "variable, meta.definition.variable", role("textPrimary")),
            rule("Types", "entity.name.type, entity.name.class, support.type, storage.type", colors["cyan"]),
            rule("Properties", "variable.other.property, support.variable.property", colors["cyan"]),
            rule("Tags", "entity.name.tag", role("information")),
            rule("Attributes", "entity.other.attribute-name", role("focus")),
            rule("Headings", "markup.heading", role("focus"), "bold"),
            rule("Bold", "markup.bold", role("textSecondary"), "bold"),
            rule("Italic", "markup.italic", role("textSecondary"), "italic"),
            rule("Links", "markup.underline.link", role("information"), "underline"),
            rule("Inserted", "markup.inserted", role("success")),
            rule("Changed", "markup.changed", role("warning")),
            rule("Deleted and invalid", "markup.deleted, invalid", role("error")),
        ],
    }
    return plistlib.dumps(theme, fmt=plistlib.FMT_XML, sort_keys=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if Apollo.tmTheme is stale")
    args = parser.parse_args()
    expected = render(load_palette())
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_bytes() != expected:
            print(f"{OUTPUT_PATH.relative_to(ROOT)} is not generated from the palette")
            return 1
        print("Apollo.tmTheme is up to date")
        return 0
    OUTPUT_PATH.write_bytes(expected)
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
