# Customize — codechu-cli

Extension points, internationalization, and built-in discovery
tools. Patterns previously bundled in the README's body.

## Custom color palette

```python
from codechu_cli import Color

c = Color(palette={"low": "92", "high": "93", "alert": "91;1"})
print(c.low("ok"), c.high("warn"), c.alert("fail"))
```

The default palette is merged in — only override the keys you care
about.

## Force color on / off (override TTY detection)

```python
from codechu_cli import Color

c_force_on = Color(enabled=True)     # always emit ANSI
c_force_off = Color(enabled=False)   # never emit
c_auto = Color()                     # default: auto-detect via stream.isatty()
```

`codechu-cli` does not read `NO_COLOR` itself; the caller decides
the policy. (Reading `NO_COLOR` belongs to the application, not the
library.)

## Custom progress bar look

```python
from codechu_cli import ProgressBar

bar = (
    ProgressBar(100)
    .fill("█")
    .empty("░")
    .template("{bar} {pct}% · {elapsed} · ETA {eta}")
)
for _ in range(100):
    bar.advance(label="working…")
bar.finish()
```

Available template fields: `{bar}`, `{pct}`, `{current}`, `{total}`,
`{label}`, `{elapsed}`, `{eta}`, `{spinner}`, `{remaining}`,
`{rate}`.

## Register a custom emoji

```python
from codechu_cli import emoji

emoji.register("snap", "📦", "snap")
print(emoji.e("snap"))    # "📦" or "snap" depending on capabilities
```

The third argument is the ASCII fallback used when the terminal
cannot render the glyph.

## Custom keymap for `select` / `multiselect`

```python
from codechu_cli import select

# vi-style only
select("Pick branch", branches, keymap={"up": ("k",), "down": ("j",)})
```

## Internationalization

The library ships English defaults and does **not** bundle gettext /
.po files — that's an application concern. For the handful of
strings it emits autonomously (the select / multiselect hint line,
the confirm suffix, the prompt validator error, the numbered-fallback
"Enter your choice"), inject a translator callable:

```python
from gettext import gettext as _

confirm("Devam edilsin mi?", translate=_,
        yes_chars=("e", "evet"), no_chars=("h", "hayır"))
select("Bir seçin", choices, translate=_)
multiselect("Hedefler", targets, translate=_)
prompt("Yedek adı", validate=v, translate=_)
```

This follows the
[STANDARDS.md §11 library carve-out](https://github.com/codechu/codechu-org/blob/main/STANDARDS.md):
libraries accept a translator hook rather than shipping their own
catalog.

## Raw ASCII-art banners

`ascii_banner(art, ...)` prints a multi-line ASCII-art string with
optional color. Text-to-art generation (rendering a plain string
like `"DISK"` as multi-line glyph blocks via a font) is out of
scope for this library — that's a typography problem with its own
quality trade-offs. Future plugin libraries under the
`codechu-glyph-*` namespace will own that, depending on
`codechu-cli` for the rendering plumbing.

For now: bring your own art, or pick from the `LOGOS` registry:

```python
from codechu_cli import LOGOS, ascii_banner

ascii_banner(LOGOS["codechu"], color="info")
ascii_banner(my_own_art_string, color="dim")
```

## Discover styles

With 65 spinner styles, finding the right one is the hard part.

```bash
# Preview every style live
python -m codechu_cli demo

# Filter by family (13 families: classic, chaos, matrix, conveyor, …)
python -m codechu_cli demo --family chaos

# Filter by mood tag (calm, busy, chaotic, playful, minimal, narrow, wide)
python -m codechu_cli demo --tag calm

# Just list everything
python -m codechu_cli list
```

Or programmatically:

```python
from codechu_cli import SPINNER_FAMILIES, STYLE_TAGS, STYLE_COMPATIBILITY

print(SPINNER_FAMILIES["chaos"])
# ['static', 'storm', 'sparks', 'fireworks', 'electricity', 'maelstrom', 'build-up']

# Pick one safe for any terminal
safe_styles = [s for s, cap in STYLE_COMPATIBILITY.items() if cap == "ascii"]
```

## Stability of style names

Style names (the keys in `SPINNER_STYLES`, `BAR_STYLES`) are part of
the **public API**. Adding new names is non-breaking; removing or
renaming requires a deprecation cycle (warn for one minor version,
then remove on the next). Family names and tag names follow the
same rule.
