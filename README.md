# Easel — website

The marketing site for **Easel: Focus Timer & Art**, an iPhone and iPad focus timer that slowly reveals a public-domain painting from The Met as you focus.

- Live: https://easelfocus.app/
- App Store: https://apps.apple.com/app/id6793262483

Plain HTML and CSS with two small scripts (`assets/reveal.js`, the hero's fog reveal; `assets/site.js`, the menu, day/night switch, language suggestion and download bar). GitHub Pages serves the repository root from `main`, with no build step.

**Every page is generated** by `tools/build.py` from the content in `content/<language>/` (`ui`, `home`, `guides`, `faq`, `privacy` JSON). English lives at the root, other languages in `/pl/`, `/es/`, `/fr/`, `/zh-hans/`, `/hi/`, `/ja/`, `/ko/`, `/pt-br/`, matching the app's nine languages.

To change text: edit `content/en/…`, update the same string in each language folder, check with `python3 tools/check_i18n.py <lang>`, run `python3 tools/build.py`, and commit the output.

Link previews (the image shown when the site is shared on X, iMessage, WhatsApp…) are rendered per language by `python3 tools/og.py` (needs Google Chrome and a local server on port 8642) into `assets/img/og/`.

Preview locally:

```sh
python3 -m http.server 8642
```

Paintings are public-domain works from The Metropolitan Museum of Art's Open Access collection. The App Store badge is Apple's official artwork, used per Apple's marketing guidelines.
