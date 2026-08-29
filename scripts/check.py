#!/usr/bin/env python3
"""Validate both TextMate themes and build one isolated bat cache."""

from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
    "Apollo": ROOT / "Apollo.tmTheme",
    "Apollo Light": ROOT / "Apollo Light.tmTheme",
}
RESTRICTED_DARK = "#665c54"
REQUIRED_SCOPES = {"comment", "string", "constant.numeric", "keyword", "entity.name.function", "entity.name.type", "markup.heading", "invalid"}
EXPECTED_DEFAULTS = {
    "Apollo": {"background": "#141617", "foreground": "#cfbc97", "caret": "#fabd2f", "selection": "#3c3836"},
    "Apollo Light": {"background": "#f9f5d7", "foreground": "#3c3836", "caret": "#8a5200", "selection": "#ebdbb2"},
}
EXPECTED_SEQUENCES = {
    "Apollo": ("38;2;131;165;152", "38;2;250;189;47", "38;2;184;187;38"),
    "Apollo Light": ("38;2;7;102;120", "38;2;138;82;0", "38;2;107;103;0"),
}


def run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, text=True, capture_output=True, env=env)


def validate_plist(theme_path: Path = THEMES["Apollo"]) -> None:
    data = plistlib.loads(theme_path.read_bytes())
    name = data.get("name")
    if name not in THEMES or not isinstance(data.get("settings"), list):
        raise AssertionError("invalid TextMate theme structure")
    defaults = data["settings"][0]["settings"]
    for key, value in EXPECTED_DEFAULTS[name].items():
        if defaults.get(key) != value:
            raise AssertionError(f"{name} {key}: expected {value}, got {defaults.get(key)}")
    scopes = {scope.strip() for item in data["settings"][1:] for scope in item.get("scope", "").split(",")}
    if not REQUIRED_SCOPES <= scopes:
        raise AssertionError(f"missing syntax scopes: {sorted(REQUIRED_SCOPES - scopes)}")
    if name == "Apollo" and RESTRICTED_DARK in theme_path.read_text(encoding="utf-8").lower():
        raise AssertionError(f"{RESTRICTED_DARK} remains restricted in Apollo Dark")


def validate_bat() -> None:
    executable = shutil.which("bat")
    if not executable:
        raise FileNotFoundError("bat")
    with tempfile.TemporaryDirectory(prefix="apollo-bat-") as temp:
        config = Path(temp) / "config"
        cache = Path(temp) / "cache"
        (config / "themes").mkdir(parents=True)
        cache.mkdir()
        for theme in THEMES.values():
            shutil.copy2(theme, config / "themes" / theme.name)
        env = os.environ.copy()
        env.update({
            "BAT_CONFIG_DIR": str(config),
            "XDG_CACHE_HOME": str(cache),
            "COLORTERM": "truecolor",
            "TERM": "xterm-256color",
        })
        run([executable, "cache", "--build"], env)
        themes = run([executable, "--list-themes"], env).stdout.splitlines()
        for name in THEMES:
            if name not in themes:
                raise AssertionError(f"isolated bat cache did not register {name}")
        sample = "def hello(name):\n    return 'hello ' + name\n"
        for name, sequences in EXPECTED_SEQUENCES.items():
            result = subprocess.run(
                [executable, "--theme", name, "--color=always", "--style=plain", "--language=Python"],
                input=sample,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            for sequence in sequences:
                if sequence not in result.stdout:
                    raise AssertionError(f"rendered {name} output lacks sequence {sequence}")


def main() -> int:
    run([sys.executable, str(ROOT / "scripts" / "generate.py"), "--check"])
    for theme in THEMES.values():
        validate_plist(theme)
    plutil = shutil.which("plutil")
    if plutil:
        for theme in THEMES.values():
            run([plutil, "-lint", str(theme)])
        print("plutil XML validation passed for both variants")
    if shutil.which("bat"):
        validate_bat()
        print("one isolated bat cache built and both variants rendered")
    else:
        print("bat not installed; native cache validation skipped")
    print("bat Apollo theme checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
