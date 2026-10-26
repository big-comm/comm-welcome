# Welcome art direction

The opening pairs the community's own owl portrait with a short native
introduction. It has one primary action (desktop personalization), an index of
six BigApps with a one-line benefit each, and a path to the full catalog.

## Composition

- The owl is the visual anchor. Preserve both eyes and the cyan/violet edge
  lighting. Avoid putting text or controls over the face.
- Keep the official lockup small enough to act as a signature. The greeting,
  not the product name, leads the reading order.
- Use the system font throughout, with generous spacing and a restrained
  hierarchy. Keep actionable text specific and short.
- Keep app icons authentic and resolve launchers from the current installation.
  Introductions explain practical uses before the explicit Open action.
- Apps are an index, not a wall of cards: icon, name, one benefit, hairline
  rules and generous spacing. Hover and focus come from Adwaita's flat buttons;
  high contrast adds visible outlines. Benefits on the home fit one line at
  900×730, so the opening needs no scrolling.
- Let Adwaita own surfaces, input states, focus, dialogs, and light/dark colors.
  The portrait's dark background belongs to the artwork, not the whole window.

## Adaptation

At 650sp the two columns become a vertical sequence. The owl becomes a 168px
banner, the greeting loses its fixed line break and both app indexes use one
column. Column counts follow the window, not the length of the text. Content can scroll with
large text or short windows; neither typography nor controls are shrunk to fit.
There are no automatic slides or decorative animation. The wordmark switches
to solid native foreground text in high contrast.

## References and boundaries

The community lockup comes from comm-release. Its blue/violet gradient also
appears in fastfetch and the [project website](https://communitybig.org/).
The portrait is supplied release artwork; see [asset provenance](ASSETS.md).
The Big Gnome Center and AshyWall interfaces inform spacing and native controls,
without importing their screenshots into the application.

GNOME references: [UI styling](https://developer.gnome.org/hig/guidelines/ui-styling.html)
and [windows](https://developer.gnome.org/hig/patterns/containers/windows.html).
The composition is implemented with GTK widgets and a Pango-measured wordmark.
Broadway screenshots inspect that implementation; Wayland and real assistive
technology validation remain separate.
