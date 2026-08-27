#!/usr/bin/env python3
"""Validate Apollo.tmTheme and build an isolated bat cache when bat is installed."""

from __future__ import annotations

import plistlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "Apollo.tmTheme"
RESTRICTED = "#665c54"
REQUIRED_SCOPES = {"comment", "string", "constant.numeric", "keyword", "entity.name.function", "entity.name.type", "markup.heading", "invalid"}


def run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, text=True, capture_output=True, env=env)


def validate_plist() -> None:
    data = plistlib.loads(THEME.read_bytes())
    if data.get("name") != "Apollo" or not isinstance(data.get("settings"), list):
        raise AssertionError("invalid TextMate theme structure")
    defaults = data["settings"][0]["settings"]
    expected = {"background": "#141617", "foreground": "#cfbc97", "caret": "#fabd2f", "selection": "#3c3836"}
    for key, value in expected.items():
        if defaults.get(key) != value:
            raise AssertionError(f"{key}: expected {value}, got {defaults.get(key)}")
    scopes = {scope.strip() for item in data["settings"][1:] for scope in item.get("scope", "").split(",")}
    if not REQUIRED_SCOPES <= scopes:
        raise AssertionError(f"missing syntax scopes: {sorted(REQUIRED_SCOPES - scopes)}")
    if RESTRICTED in THEME.read_text(encoding="utf-8").lower():
        raise AssertionError(f"{RESTRICTED} is restricted to ANSI bright black")


def validate_bat() -> None:
    executable = shutil.which("bat")
    if not executable:
        raise FileNotFoundError("bat")
    with tempfile.TemporaryDirectory(prefix="apollo-bat-") as temp:
        config = Path(temp) / "config"
        cache = Path(temp) / "cache"
        (config / "themes").mkdir(parents=True)
        cache.mkdir()
        shutil.copy2(THEME, config / "themes" / THEME.name)
        import os
        env = os.environ.copy()
        env.update({
            "BAT_CONFIG_DIR": str(config),
            "XDG_CACHE_HOME": str(cache),
            "COLORTERM": "truecolor",
            "TERM": "xterm-256color",
        })
        run([executable, "cache", "--build"], env)
        themes = run([executable, "--list-themes"], env).stdout.splitlines()
        if "Apollo" not in themes:
            raise AssertionError("isolated bat cache did not register Apollo")
        sample = "def hello(name):\n    return 'hello ' + name\n"
        result = subprocess.run([executable, "--theme", "Apollo", "--color=always", "--style=plain", "--language=Python"], input=sample, env=env, text=True, capture_output=True, check=True)
        for sequence in ("38;2;131;165;152", "38;2;250;189;47", "38;2;184;187;38"):
            if sequence not in result.stdout:
                raise AssertionError(f"rendered bat output lacks Apollo sequence {sequence}")


def main() -> int:
    run([sys.executable, str(ROOT / "scripts" / "generate.py"), "--check"])
    validate_plist()
    plutil = shutil.which("plutil")
    if plutil:
        run([plutil, "-lint", str(THEME)])
        print("plutil XML validation passed")
    if shutil.which("bat"):
        validate_bat()
        print("isolated bat cache and render passed")
    else:
        print("bat not installed; native cache validation skipped")
    print("bat Apollo theme checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
