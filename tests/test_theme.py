from __future__ import annotations

import hashlib
import importlib.util
import plistlib
import shutil
import subprocess
import tempfile
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
    def test_both_textmate_variants_are_deterministic(self) -> None:
        self.assertEqual(
            hashlib.sha256((ROOT / "palette" / "apollo-light.json").read_bytes()).hexdigest(),
            "b0dbdeb719ed1931c424e9590562689325ecac1609e2fed6406ec5c4d3dc5763",
        )
        expected = generate.render_outputs()
        self.assertEqual(set(expected), {ROOT / "Apollo.tmTheme", ROOT / "Apollo Light.tmTheme"})
        for path, content in expected.items():
            self.assertEqual(path.read_bytes(), content)
            check.validate_plist(path)
        light = plistlib.loads((ROOT / "Apollo Light.tmTheme").read_bytes())
        self.assertEqual(light["name"], "Apollo Light")
        self.assertEqual(light["semanticClass"], "theme.light.apollo-light")

    def test_documented_uninstall_preserves_unowned_or_modified_themes(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn('.installed-theme-hashes', readme)
        self.assertIn('Apollo.tmTheme', readme)
        self.assertIn('Apollo Light.tmTheme', readme)
        self.assertIn('shasum -a 256', readme)
        self.assertIn('touch "$marker"', readme)
        self.assertNotIn(': > "$marker"', readme)
        self.assertIn('grep -F -v', readme)
        self.assertNotIn('rm -f "$theme_dir/Apollo.tmTheme"', readme)
        self.assertNotIn('rm -f "$theme_dir/Apollo Light.tmTheme"', readme)

    def test_documented_install_is_idempotent_and_preserves_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / "clone"
            themes = Path(directory) / "themes"
            shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            themes.mkdir()
            script = r'''
clone_dir="$1"
theme_dir="$2"
marker="$clone_dir/.installed-theme-hashes"
install() {
  installed=0
  mkdir -p "$theme_dir"
  touch "$marker"
  for name in 'Apollo.tmTheme' 'Apollo Light.tmTheme'; do
    source_theme="$clone_dir/$name"
    installed_theme="$theme_dir/$name"
    if [ -e "$installed_theme" ]; then
      :
    else
      cp "$source_theme" "$installed_theme"
      hash="$(shasum -a 256 "$installed_theme" | cut -d ' ' -f 1)"
      grep -F -v "$(printf '%s\t' "$name")" "$marker" > "$marker.tmp" || true
      mv "$marker.tmp" "$marker"
      printf '%s\t%s\n' "$name" "$hash" >> "$marker"
      installed=1
    fi
  done
}
install
install
[ "$(wc -l < "$marker" | tr -d ' ')" = 2 ]
removed=0
while IFS="$(printf '\t')" read -r name expected_hash; do
  installed_theme="$theme_dir/$name"
  actual_hash="$(shasum -a 256 "$installed_theme" | cut -d ' ' -f 1)"
  if [ "$actual_hash" = "$expected_hash" ]; then rm -- "$installed_theme"; removed=1; fi
done < "$marker"
[ "$removed" -eq 1 ]
[ ! -e "$theme_dir/Apollo.tmTheme" ]
[ ! -e "$theme_dir/Apollo Light.tmTheme" ]
'''
            subprocess.run(["sh", "-c", script, "sh", str(clone), str(themes)], check=True)

    @unittest.skipUnless(shutil.which("bat"), "bat is not installed")
    def test_isolated_bat_cache_builds_once_and_renders_both_variants(self) -> None:
        check.validate_bat()


if __name__ == "__main__":
    unittest.main()
