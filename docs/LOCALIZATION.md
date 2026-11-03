# Localization

English is the source language. `locale/LINGUAS` defines 29 locales, including
28 translation targets. `pt` is European Portuguese, `pt_BR` is Brazilian
Portuguese, `no` is Norwegian Bokmål, and `zh` is Simplified Chinese.

Translations were produced locally with `gpt-5.6-luna` at `xhigh`, explicitly
selected by the maintainer. Workers passed the LangForge harness before
production. Validation checks message coverage, placeholders, protected names,
gettext syntax, compiled assets and desktop entries. Structural validation is
not a substitute for native-speaker review.

## Files

- `locale/comm-welcome.pot`: Python UI and desktop source messages.
- `locale/<language>.po`: editable catalogs; English repeats the source.
- `data/*.desktop.in`: untranslated launcher templates.
- `usr/share/locale/*/LC_MESSAGES/comm-welcome.mo`: committed runtime catalogs.
- `usr/share/applications/` and `etc/xdg/autostart/`: generated desktop entries.

The runtime catalogs are deliberately versioned. The distribution's unchanged
PKGBUILD template copies `usr/` and `etc/` directly; packages therefore include
translations without calling a translation service or changing the template.
Other build caches remain ignored. Both checkout and installed execution use
the adjacent `usr/share/locale` directory.

## Update locally

```sh
python3 scripts/i18n.py extract
# Merge catalogs, translate changed entries, then review them.
python3 scripts/i18n.py compile
make check
```

`compile` only runs gettext tools locally. It does not translate text, call an
API, commit changes or push. Include updated PO/MO files and desktop entries
in the same review. CI should validate and package these reviewed assets.

## Isolated visual checks

```sh
LANGUAGE=pt_BR bash scripts/visual-check.sh /tmp/welcome-pt_BR --localized-only
LANGUAGE=he bash scripts/visual-check.sh /tmp/welcome-he --localized-only
```

These checks render six scenarios through Broadway without installing
browsers or touching the visible desktop session. Real GNOME/Wayland and
screen-reader verification remain separate.
