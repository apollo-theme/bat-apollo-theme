# Apollo for bat

A standalone TextMate theme for bat with Apollo defaults and focused mappings for common syntax, markup, and diff scopes.

Repository: https://github.com/apollo-theme/bat-apollo-theme

## Install

Clone the repository, then copy the theme only if that destination is unused:

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

Use Apollo once:

```sh
BAT_THEME=Apollo bat path/to/file
```

Or opt in for the current shell with `export BAT_THEME=Apollo`. No bat config file is edited.

## Uninstall

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
