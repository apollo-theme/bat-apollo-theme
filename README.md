<h1 align="center">bat Apollo Theme</h1>

<p align="center">Apollo gives bat a warm, high-contrast syntax view with focused TextMate scope mappings.</p>

<p align="center">
  <a href="https://apollo-theme.github.io/#app-bat"><img alt="Preview" src="https://img.shields.io/badge/status-Preview-fabd2f?style=flat-square&labelColor=141617"></a>
  <a href="https://github.com/apollo-theme/bat-apollo-theme/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/apollo-theme/bat-apollo-theme/ci.yml?branch=main&style=flat-square&label=CI&labelColor=141617"></a>
  <a href="https://github.com/apollo-theme/bat-apollo-theme/releases/latest"><img alt="Latest Release" src="https://img.shields.io/github/v/release/apollo-theme/bat-apollo-theme?display_name=tag&sort=semver&style=flat-square&label=Release&color=d3869b&labelColor=141617"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-b8bb26?style=flat-square&labelColor=141617"></a>
  <a href="https://github.com/sharkdp/bat"><img alt="Theme for bat" src="https://img.shields.io/badge/app-bat-83a598?style=flat-square&labelColor=141617"></a>
  <a href="palette/apollo.json"><img alt="Canonical Apollo palette" src="https://img.shields.io/badge/palette-canonical-8ec07c?style=flat-square&labelColor=141617"></a>
</p>

<p align="center">
  <a href="https://apollo-theme.github.io/#app-bat"><img src="https://raw.githubusercontent.com/apollo-theme/apollo-theme.github.io/main/previews/bat.svg" alt="Simulated bat Apollo Theme preview"></a>
</p>
<p align="center"><em>Simulated preview. Syntax grammar, terminal, and font rendering may vary.</em></p>

Apollo ships as a standalone `Apollo.tmTheme` for bat. Its mappings distinguish common syntax, markup, and diff scopes while leaving your bat configuration untouched until you explicitly select the theme.

## Install

Clone the repository, then copy the theme only when the destination is unused. The marker records ownership so uninstall can distinguish this copy from a pre-existing theme:

```sh
git clone https://github.com/apollo-theme/bat-apollo-theme "$HOME/.config/bat-apollo-theme"
theme_dir="$(bat --config-dir)/themes"
marker="$HOME/.config/bat-apollo-theme/.installed-theme-path"
mkdir -p "$theme_dir"
if [ -e "$theme_dir/Apollo.tmTheme" ]; then
  printf '%s\n' 'Apollo.tmTheme already exists; nothing was overwritten.'
else
  cp "$HOME/.config/bat-apollo-theme/Apollo.tmTheme" "$theme_dir/Apollo.tmTheme"
  printf '%s\n' "$theme_dir/Apollo.tmTheme" > "$marker"
  bat cache --build
fi
```

## Activate

Use Apollo for one command:

```sh
BAT_THEME=Apollo bat path/to/file
```

Or opt in for the current shell with `export BAT_THEME=Apollo`. No bat config file is edited.

## Uninstall

The uninstall guard removes the installed theme only when this clone recorded the expected destination and the file still matches the clone. A theme that is unowned, moved, or modified is preserved.

```sh
clone_dir="$HOME/.config/bat-apollo-theme"
marker="$clone_dir/.installed-theme-path"
if [ -f "$marker" ]; then
  installed_theme="$(cat "$marker")"
  expected_theme="$(bat --config-dir)/themes/Apollo.tmTheme"
  if [ "$installed_theme" = "$expected_theme" ] &&
     cmp -s "$installed_theme" "$clone_dir/Apollo.tmTheme"; then
    rm -f "$installed_theme"
    bat cache --build
  else
    printf '%s\n' 'Apollo.tmTheme was not installed by this clone or has changed; it was preserved.'
  fi
fi
unset BAT_THEME
rm -rf "$clone_dir"
```

## Visual check

Render a small Python sample without paging or decorations:

```sh
printf '%s\n' 'def hello(name):' '    return "hello " + name' |
  bat --language=Python --style=plain --color=always --theme=Apollo
```

The keyword should be blue, function gold, parameter magenta, string green, and ordinary text warm beige.

## Development

```sh
python3 scripts/generate.py --check
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

The checker validates the TextMate plist and, when bat is installed, builds an isolated cache and renders a sample. Change scope mappings in `scripts/generate.py`; do not hand-edit generated `Apollo.tmTheme`.

## License

[MIT](LICENSE)
