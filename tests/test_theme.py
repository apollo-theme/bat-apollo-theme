from __future__ import annotations

import importlib.util
import shutil
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generate = load_module("bat_generate", ROOT / "scripts" / "generate.py")
check = load_module("bat_check", ROOT / "scripts" / "check.py")


class ApolloBatThemeTests(unittest.TestCase):
    def test_textmate_plist_has_apollo_defaults_and_useful_scopes(self) -> None:
        self.assertEqual((ROOT / "Apollo.tmTheme").read_bytes(), generate.render(generate.load_palette()))
        check.validate_plist()

    @unittest.skipUnless(shutil.which("bat"), "bat is not installed")
    def test_isolated_bat_cache_builds_and_renders(self) -> None:
        check.validate_bat()


if __name__ == "__main__":
    unittest.main()
