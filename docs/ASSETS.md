# Assets

- `artwork/comm-welcome.png`: approved owl icon, generated with OpenAI imagegen
  and edited to remove the decorative star. Original 1254×1254 RGBA PNG.
- `usr/share/icons/hicolor/*/apps/org.bigcommunity.CommWelcome.png`: resized
  derivatives, 16–1024 pixels. Shared by the launcher and About.
  Transparency is preserved. The source is raster, not SVG.
- `assets/desktop.svg`: original local desktop illustration, MIT.
- `assets/community-owl.svg`: new community owl, copied unchanged from
  `community-release/usr/share/icons/hicolor/scalable/apps/about.svg` in the
  BigCommunity repositories. MIT, Copyright (c) 2024 Community Big; the same
  copyright notice is preserved in this project's LICENSE.
- `assets/wallpaper-{olhar,pena,aurora}.jpg`: 640×360 previews of wallpapers
  created and supplied by Leonardo Athayde for the October 2026 release.
  Sources: `masters-sem-selo/{olhar,pena}-dark.png` and
  `exploracoes/aurora-v2c-16x9-clara-chatgpt-1672x941.png` (the approved pale
  light version) in the supplied
  wallpaper collection. Resized and center-cropped, metadata stripped;
  originals are unchanged. These previews appear in the AshyWall introduction.
- `assets/welcome-portrait.jpg`: portrait crop of the same supplied
  `masters-sem-selo/olhar-dark.png`, preserving both eyes and the cyan/violet
  edge lighting. The crop is 2400×2688 at offset (1275, 0), resized to 960×1075,
  with metadata stripped. GTK adapts the display crop to the available space.
- `assets/appimage-creator.svg`: official AppImage Creator icon, copied unchanged
  from `usr/share/appimage-creator/icons/appimage-creator.svg` in
  github.com/big-comm/appimage-creator. GPL-3.0, as that project; kept as a
  separate file and shown only while the app is not installed.
- `assets/langforge.svg`: official LangForge icon, copied unchanged from
  `usr/share/icons/hicolor/scalable/apps/langforge.svg` in
  github.com/big-comm/LangForge. MIT. Shown only while the app is not installed.
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
