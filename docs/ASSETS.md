# Assets

- `artwork/comm-welcome.png`: approved owl icon, generated with OpenAI imagegen
  and edited to remove the decorative star. Original 1254×1254 RGBA PNG.
- `usr/share/icons/hicolor/*/apps/org.bigcommunity.CommWelcome.png`: resized
  derivatives, 16–1024 pixels. Shared by the launcher, Welcome and About.
  Transparency is preserved. The source is raster, not SVG.
- `assets/desktop.svg`: original local desktop illustration, MIT.
- `assets/telegram-symbolic.svg`: original paper-plane glyph, MIT.
- `assets/heart-symbolic.svg`: original donation glyph, MIT.
- `assets/{pix,usdt,bitcoin}-symbolic.svg`: original payment glyphs, MIT.
- App/browser icons: resolved from installed desktop entries, the system icon
  theme, or installed BigLinux WebApps assets. Not redistributed here.
- User-supplied mockups informed layout only. Placeholder icons and BigLinux
  branding were not imported.

## Regenerate icon sizes

Requires ImageMagick for development only.

```sh
for size in 16 24 32 48 64 128 256 512 1024; do
    directory="usr/share/icons/hicolor/${size}x${size}/apps"
    mkdir -p "$directory"
    magick artwork/comm-welcome.png -resize "${size}x${size}" \
        "$directory/org.bigcommunity.CommWelcome.png"
done
```
