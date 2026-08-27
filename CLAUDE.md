# bat Apollo theme development

- `palette/apollo.json` is the exact canonical snapshot. Update the pinned SHA-256 in `scripts/generate.py` only when deliberately refreshing it.
- Edit `scripts/generate.py`, not generated `Apollo.tmTheme`.
- Keep TextMate scope mappings focused and valid for bat/syntect.
- Generate: `python3 scripts/generate.py`
- Check plist, optional plutil, isolated bat cache, and render: `python3 scripts/check.py`
- Test all: `python3 -m unittest discover -s tests -v`
- Single native test: `python3 -m unittest -v tests.test_theme.ApolloBatThemeTests.test_isolated_bat_cache_builds_and_renders`
