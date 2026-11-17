# Easel — website

The marketing site for **Easel: Focus Timer & Art**, an iPhone and iPad focus timer that slowly reveals a public-domain painting from The Met as you focus.

- Live: https://markockidev.github.io/Easel-Focus-Website/
- App Store: https://apps.apple.com/app/id6793262483

Plain HTML and CSS with one small script (`assets/reveal.js`, the hero's fog reveal). No build step: GitHub Pages serves the repository root from `main`.

Preview locally:

```sh
python3 -m http.server 8642
```

Paintings are public-domain works from The Metropolitan Museum of Art's Open Access collection. The App Store badge is Apple's official artwork, used per Apple's marketing guidelines.
