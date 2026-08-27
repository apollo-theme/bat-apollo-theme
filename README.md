# Apollo for bat

A standalone TextMate theme for bat with Apollo defaults and focused mappings for common syntax, markup, and diff scopes.

Repository: https://github.com/apollo-theme/bat-apollo-theme

## Install

Clone the repository, then copy the theme only if that destination is unused:

```sh
git clone https://github.com/apollo-theme/bat-apollo-theme "$HOME/.config/bat-apollo-theme"
theme_dir="$(bat --config-dir)/themes"
mkdir -p "$theme_dir"
if [ -e "$theme_dir/Apollo.tmTheme" ]; then
  printf '%s\n' 'Apollo.tmTheme already exists; nothing was overwritten.'
else
  cp "$HOME/.config/bat-apollo-theme/Apollo.tmTheme" "$theme_dir/Apollo.tmTheme"
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
theme_dir="$(bat --config-dir)/themes"
rm -f "$theme_dir/Apollo.tmTheme"
bat cache --build
unset BAT_THEME
rm -rf "$HOME/.config/bat-apollo-theme"
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
