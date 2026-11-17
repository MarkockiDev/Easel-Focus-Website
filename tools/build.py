#!/usr/bin/env python3
"""Builds every page of the site, in every language, from content/<lang>/*.json.

    python3 tools/build.py        # then commit the generated HTML

The output is plain HTML, so GitHub Pages needs no build step.

Content files (one folder per language, same shape as content/en/):
  ui.json       navigation, footer and page-level strings
  home.json     the home page (HTML with placeholders)
  guides.json   the guides, in order
  faq.json      questions and answers, in groups
  privacy.json  the privacy policy, section by section

Placeholders inside content HTML:
  {p}  path to the site root (assets live there)
  {l}  path to this language's root (pages live there)
  {badge} / {badge_lazy}  the localized App Store badge
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://easelfocus.app/"
APP = "https://apps.apple.com/app/id6793262483"
FEEDBACK = "https://markockidev.canny.io/easel"
MAKER = "https://markockiadam.com"
EMAIL = "adam@easelfocus.app"
UPDATED_ISO = "2026-11-17"
VERSION = "5"   # bump to bust browser caches of css/js

# code, folder, html lang / hreflang, Apple badge locale
LANGS = [
    ("en", "", "en", "en-us"),
    ("pl", "pl/", "pl", "pl-pl"),
    ("es", "es/", "es", "es-es"),
    ("fr", "fr/", "fr", "fr-fr"),
    ("zh-Hans", "zh-hans/", "zh-Hans", "zh-cn"),
    ("hi", "hi/", "hi", "en-us"),          # Apple has no Hindi badge; the Indian App Store uses English
    ("ja", "ja/", "ja", "ja-jp"),
    ("ko", "ko/", "ko", "ko-kr"),
    ("pt-BR", "pt-br/", "pt-BR", "pt-br"),
]

e = html.escape
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]


def load(code):
    d = os.path.join(ROOT, "content", code)
    return {k: json.load(open(os.path.join(d, k + ".json"))) for k in ("ui", "home", "guides", "faq", "privacy")}


import sys
ONLY = set(sys.argv[1:])          # e.g. `build.py en pl` builds just those; default: every complete language
C = {}
for _L in LANGS:
    if ONLY and _L[0] not in ONLY:
        continue
    try:
        C[_L[0]] = load(_L[0])
    except (FileNotFoundError, json.JSONDecodeError):
        pass                      # not translated (yet): skipped, and left out of the language menu
ACTIVE = [L for L in LANGS if L[0] in C]


def badge_width(locale, height):
    svg = open(os.path.join(ROOT, "assets/img/badges", f"{locale}-black.svg")).read()
    _, _, w, h = map(float, re.search(r'viewBox="([^"]+)"', svg).group(1).split())
    return round(w / h * height)


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


# ───────────────────────── shared pieces ─────────────────────────

ICON_GLOBE = '<svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3 12h18M12 3c2.6 2.6 3.8 5.6 3.8 9s-1.2 6.4-3.8 9c-2.6-2.6-3.8-5.6-3.8-9S9.4 5.6 12 3z" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
ICON_SUN = '<svg class="i-sun" aria-hidden="true" viewBox="0 0 24 24" width="20" height="20"><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 2.5v2.2M12 19.3v2.2M4.6 4.6l1.6 1.6M17.8 17.8l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.6 19.4l1.6-1.6M17.8 6.2l1.6-1.6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'
ICON_MOON = '<svg class="i-moon" aria-hidden="true" viewBox="0 0 24 24" width="20" height="20"><path d="M19.5 14.6A8 8 0 0 1 9.4 4.5a8 8 0 1 0 10.1 10.1z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>'
ICON_MENU = '<svg aria-hidden="true" viewBox="0 0 24 24" width="22" height="22"><path d="M4 8.5h16M4 15.5h16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
ICON_CHEVRON = '<svg class="chev" aria-hidden="true" viewBox="0 0 12 12" width="10" height="10"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def badge(L, p, ui, height=54, lazy=False):
    loc = L[3]
    w = badge_width(loc, height)
    lz = ' loading="lazy"' if lazy else ""
    alt = e(ui["badge_alt"])
    return (f'<a class="badge" href="{APP}">'
            f'<img class="on-light" src="{p}assets/img/badges/{loc}-black.svg" alt="{alt}" width="{w}" height="{height}"{lz}>'
            f'<img class="on-dark" src="{p}assets/img/badges/{loc}-white.svg" alt="{alt}" width="{w}" height="{height}"{lz}>'
            f'</a>')


def lang_links(p, rel, current):
    items = []
    for L in ACTIVE:
        code, folder, hl = L[0], L[1], L[2]
        href = (p + folder + rel) or "./"
        cur = ' aria-current="true"' if code == current else ""
        items.append(f'<li><a href="{href}" hreflang="{hl}" lang="{hl}" data-lang="{code}"{cur}>{e(C[code]["ui"]["language_name"])}</a></li>')
    return '<ul class="langs">' + "".join(items) + "</ul>"


def header(L, p, l, rel, current, ui):
    home = l or "./"

    def nav(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{href}"{cur}>{e(label)}</a>'
    links = (nav(l + "guides/", ui["nav_guides"], "guides") +
             nav(l + "faq/", ui["nav_questions"], "faq") +
             nav(l + "privacy/", ui["nav_privacy"], "privacy"))
    langs = lang_links(p, rel, L[0])
    seg = "".join(f'<button type="button" data-theme-set="{v}" aria-pressed="false">{e(ui[k])}</button>'
                  for v, k in (("auto", "theme_auto"), ("light", "theme_light"), ("dark", "theme_dark")))
    return f"""  <a class="skip" href="#main">{e(ui["skip"])}</a>
  <header class="top">
    <div class="wrap">
      <a class="brand" href="{home}" aria-label="{e(ui["home_aria"])}">
        <img src="{p}assets/img/icon.jpg" alt="" width="36" height="36">
        <span>Easel</span>
      </a>
      <nav class="primary" aria-label="{e(ui["nav_label"])}">{links}</nav>
      <div class="tools">
        <details class="lang pop">
          <summary title="{e(ui["language"])}" aria-label="{e(ui["language"])}: {e(ui["language_name"])}">{ICON_GLOBE}<span>{e(ui["language_name"])}</span>{ICON_CHEVRON}</summary>
          <div class="pop-panel">{langs}</div>
        </details>
        <button class="theme-toggle" type="button" title="{e(ui["appearance"])}" data-to-dark="{e(ui["theme_toggle_to_dark"])}" data-to-light="{e(ui["theme_toggle_to_light"])}" aria-label="{e(ui["theme_toggle_to_dark"])}">{ICON_SUN}{ICON_MOON}</button>
        <a class="get" href="{APP}">{e(ui["nav_download"])}</a>
        <details class="menu pop">
          <summary title="{e(ui["menu"])}" aria-label="{e(ui["menu"])}">{ICON_MENU}</summary>
          <div class="pop-panel menu-panel">
            <nav class="menu-links" aria-label="{e(ui["menu"])}">{nav(home, ui["nav_home"], "home")}{links}</nav>
            <p class="label">{e(ui["appearance"])}</p>
            <div class="seg" role="group" aria-label="{e(ui["appearance"])}">{seg}</div>
            <p class="label">{e(ui["language"])}</p>
            {langs}
          </div>
        </details>
      </div>
    </div>
  </header>"""


def footer(L, p, l, ui):
    return f"""  <footer>
    <div class="wrap">
      <div class="row">
        <a class="brand" href="{l or './'}" aria-label="{e(ui["home_aria"])}"><img src="{p}assets/img/icon.jpg" alt="" width="36" height="36" loading="lazy"><span>Easel</span></a>
        <nav aria-label="{e(ui["footer_label"])}">
          <a href="{APP}">{e(ui["footer_app_store"])}</a>
          <a href="{l}guides/">{e(ui["footer_guides"])}</a>
          <a href="{l}faq/">{e(ui["footer_questions"])}</a>
          <a href="{l}privacy/">{e(ui["footer_privacy"])}</a>
          <a href="{FEEDBACK}">{e(ui["footer_feedback"])}</a>
          <a href="mailto:{EMAIL}">{e(ui["footer_contact"])}</a>
          <a href="{MAKER}">{e(ui["footer_maker"])}</a>
        </nav>
      </div>
      <p class="fine">{e(ui["fine"])}</p>
    </div>
  </footer>"""


def getbar(L, p, ui):
    return f"""  <div class="getbar" role="complementary" aria-label="{e(ui["getbar_label"])}">
    <img class="icon" src="{p}assets/img/icon.jpg" alt="" width="40" height="40">
    <span class="t"><b>Easel</b><span>{e(ui["getbar_subtitle"])}</span></span>
    {badge(L, p, ui, 40, lazy=True)}
  </div>"""


def suggestions(rel):
    """Each language's 'also available in …' line, so site.js can offer a visitor their own language."""
    return {L[0]: {"text": C[L[0]]["ui"]["suggest"], "link": C[L[0]]["ui"]["suggest_link"],
                   "dismiss": C[L[0]]["ui"]["dismiss"], "path": L[1] + rel, "hl": L[2]} for L in ACTIVE}


HEAD_SCRIPT = ("<script>document.documentElement.classList.add('js');"
               "try{var t=localStorage.getItem('easel-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)}catch(e){}</script>")


def page(L, rel, title, description, body, current="", jsonld=None, og_title=None, og_type="article", extra_head="", extra_scripts=""):
    code, folder, hl = L[0], L[1], L[2]
    ui = C[code]["ui"]
    path = folder + rel
    p = "../" * path.count("/")
    l = p + folder
    url = BASE + path
    alts = "".join(f'  <link rel="alternate" hreflang="{A[2]}" href="{BASE}{A[1]}{rel}">\n' for A in ACTIVE)
    alts += f'  <link rel="alternate" hreflang="x-default" href="{BASE}{rel}">\n'
    ld = "".join('  <script type="application/ld+json">' + json.dumps(b, ensure_ascii=False) + "</script>\n" for b in (jsonld or []))
    content = body(p, l).replace("{badge_lazy}", badge(L, p, ui, lazy=True)).replace("{badge}", badge(L, p, ui))
    eh = extra_head.replace("{p}", p)
    es = extra_scripts.replace("{p}", p)
    doc = f"""<!doctype html>
<html lang="{hl}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{url}">
{alts}  <meta name="apple-itunes-app" content="app-id=6793262483">
  <meta name="theme-color" content="#F5F2EC">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Easel">
  <meta property="og:locale" content="{hl.replace('-', '_')}">
  <meta property="og:title" content="{e(og_title or title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{BASE}assets/img/og.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(og_title or title)}">
  <meta name="twitter:description" content="{e(description)}">
  <meta name="twitter:image" content="{BASE}assets/img/og.jpg">
  <link rel="icon" href="{p}favicon-32.png" sizes="32x32" type="image/png">
  <link rel="icon" href="{p}assets/img/icon-192.png" sizes="192x192" type="image/png">
  <link rel="apple-touch-icon" href="{p}apple-touch-icon.png">
{eh}  <link rel="stylesheet" href="{p}assets/site.css?v={VERSION}">
  {HEAD_SCRIPT}
{ld}</head>
<body class="has-getbar">
{header(L, p, l, rel, current, ui)}

  <main id="main">
{content}
  </main>

{footer(L, p, l, ui)}
{getbar(L, p, ui)}
  <script type="application/json" id="i18n" data-lang="{code}" data-root="{p}">{json.dumps(suggestions(rel), ensure_ascii=False)}</script>
{es}  <script src="{p}assets/site.js?v={VERSION}" defer></script>
</body>
</html>
"""
    doc = label_tables(doc)
    out = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(doc)
    return url


def label_tables(doc):
    """Give each table cell a data-label from its column heading, so phones can stack rows."""
    def one(m):
        t = m.group(0)
        heads = [strip_tags(h).strip() for h in re.findall(r"<th[^>]*>(.*?)</th>", t)]

        def row(r):
            i = [0]

            def cell(c):
                lab = heads[i[0]] if i[0] < len(heads) else ""
                i[0] += 1
                return f'<td data-label="{e(lab)}">'
            return re.sub(r"<td>", cell, r.group(0))
        return re.sub(r"<tr>.*?</tr>", row, t, flags=re.S)
    return re.sub(r'<table class="data">.*?</table>', one, doc, flags=re.S)


def crumbs(l, ui, trail):
    parts = [f'<a href="{l or "./"}">{e(ui["crumb_home"])}</a>']
    for href, label in trail[:-1]:
        parts.append(f'<a href="{l}{href}">{e(label)}</a>')
    parts.append(f'<span aria-current="page">{e(trail[-1][1])}</span>')
    return f'<nav class="crumbs" aria-label="{e(ui["breadcrumb_label"])}">' + ' <span aria-hidden="true">/</span> '.join(parts) + "</nav>"


def breadcrumb_ld(L, ui, trail):
    root = BASE + L[1]
    items = [{"@type": "ListItem", "position": 1, "name": ui["crumb_home"], "item": root}]
    for i, (href, label) in enumerate(trail, start=2):
        items.append({"@type": "ListItem", "position": i, "name": label, "item": root + href})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def fill(s, p, l):
    return s.replace("{p}", p).replace("{l}", l)


def callout(label, text):
    return f'<div class="callout"><span class="label">{label}</span>{text}</div>'


# ───────────────────────── pages ─────────────────────────

def build_home(L):
    h = C[L[0]]["home"]
    ld = [{"@context": "https://schema.org", "@type": "MobileApplication", "name": "Easel: Focus Timer & Art",
           "operatingSystem": "iOS 17.0 or later", "applicationCategory": "ProductivityApplication",
           "description": h["og_description"], "inLanguage": L[2], "installUrl": APP,
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
           "author": {"@type": "Person", "name": "Adam", "url": MAKER}}]
    return page(L, "", h["title"], h["description"], lambda p, l: fill(h["body"], p, l),
                current="home", jsonld=ld, og_title=h["og_title"], og_type="website",
                extra_head=f'  <meta property="og:image:alt" content="{e(h["og_image_alt"])}">\n  <link rel="preload" href="{{p}}assets/img/van-gogh.jpg" as="image">\n',
                extra_scripts=f'  <script src="{{p}}assets/reveal.js?v={VERSION}" defer></script>\n')


def guide_toc(l, ui, guides, current):
    items = "".join(
        f'<li><a href="{l}guides/{g["slug"]}/"{" aria-current=\"page\"" if g["slug"] == current else ""}><span class="n">{ROMAN[i]}</span>{e(g["nav"])}</a></li>'
        for i, g in enumerate(guides))
    return f"""<aside class="toc">
          <details open><summary>{e(ui["toc_all_guides"])}</summary>
            <nav aria-label="{e(ui["toc_the_guides"])}"><p class="label">{e(ui["toc_the_guides"])}</p><ol>{items}</ol></nav>
          </details>
        </aside>"""


def build_guides(L):
    ui, guides = C[L[0]]["ui"], C[L[0]]["guides"]
    urls = []
    for i, g in enumerate(guides):
        prev_g = guides[i - 1] if i > 0 else None
        next_g = guides[i + 1] if i + 1 < len(guides) else None
        trail = [("guides/", ui["crumb_guides"]), (f"guides/{g['slug']}/", g["nav"])]

        def body(p, l, g=g, i=i, prev_g=prev_g, next_g=next_g, trail=trail):
            pager = f'<nav class="pager" aria-label="{e(ui["pager_label"])}">'
            if prev_g:
                pager += f'<a class="prev" href="{l}guides/{prev_g["slug"]}/"><span class="label">{e(ui["pager_prev"])}</span><span>{e(prev_g["nav"])}</span></a>'
            if next_g:
                pager += f'<a class="next" href="{l}guides/{next_g["slug"]}/"><span class="label">{e(ui["pager_next"])}</span><span>{e(next_g["nav"])}</span></a>'
            pager += "</nav>"
            return f"""    <div class="wrap">
      <header class="page-head">
        {crumbs(l, ui, trail)}
        <p class="label"><span class="numeral">{ROMAN[i]}</span> &nbsp;{e(g["room"])}</p>
        <h1>{e(g["title"])}</h1>
        <p class="lede">{fill(g["lede"], p, l)}</p>
      </header>
      <div class="doc">
        {guide_toc(l, ui, guides, g["slug"])}
        <article class="prose">
{fill(g["body"], p, l)}
          {pager}
        </article>
      </div>
    </div>"""

        ld = [breadcrumb_ld(L, ui, trail), {
            "@context": "https://schema.org", "@type": "TechArticle", "inLanguage": L[2],
            "headline": g["title"], "description": g["desc"], "dateModified": UPDATED_ISO,
            "about": {"@type": "MobileApplication", "name": "Easel: Focus Timer & Art", "operatingSystem": "iOS"},
            "author": {"@type": "Person", "name": "Adam", "url": MAKER},
            "mainEntityOfPage": BASE + L[1] + f"guides/{g['slug']}/"}]
        urls.append(page(L, f"guides/{g['slug']}/", g["seo"], g["desc"], body, current="guides", jsonld=ld, og_title=g["title"]))

    def hub(p, l):
        cards = "".join(
            f'<a class="card" href="{l}guides/{g["slug"]}/"><span class="n">{ROMAN[i]}</span><h2>{e(g["nav"])}</h2><p>{e(g["card"])}</p></a>'
            for i, g in enumerate(guides))
        return f"""    <div class="wrap">
      <header class="page-head">
        {crumbs(l, ui, [("guides/", ui["crumb_guides"])])}
        <p class="label">{e(ui["guides_label"])}</p>
        <h1>{e(ui["guides_h1"])}</h1>
        <p class="lede">{fill(ui["guides_lede"], p, l)}</p>
      </header>
      <div class="cards">{cards}</div>
    </div>"""
    urls.insert(0, page(L, "guides/", ui["guides_title"], ui["guides_description"], hub, current="guides",
                        jsonld=[breadcrumb_ld(L, ui, [("guides/", ui["crumb_guides"])])], og_title=ui["guides_og_title"]))
    return urls


def build_faq(L):
    ui, faq = C[L[0]]["ui"], C[L[0]]["faq"]

    def body(p, l):
        groups = toc = ""
        for gi, grp in enumerate(faq):
            gid = f"q-{gi + 1}"
            toc += f'<li><a href="#{gid}"><span class="n">{ROMAN[gi]}</span>{e(grp["group"])}</a></li>'
            items = "".join(f'<details><summary>{e(it["q"])}</summary><div class="answer"><p>{fill(it["a"], p, l)}</p></div></details>' for it in grp["items"])
            groups += f'<h2 id="{gid}">{e(grp["group"])}</h2><div class="qa">{items}</div>'
        return f"""    <div class="wrap">
      <header class="page-head">
        {crumbs(l, ui, [("faq/", ui["crumb_questions"])])}
        <p class="label">{e(ui["faq_label"])}</p>
        <h1>{e(ui["faq_h1"])}</h1>
        <p class="lede">{fill(ui["faq_lede"], p, l)}</p>
      </header>
      <div class="doc">
        <aside class="toc"><details open><summary>{e(ui["toc_topics"])}</summary><nav aria-label="{e(ui["toc_topics"])}"><p class="label">{e(ui["toc_topics"])}</p><ol>{toc}</ol></nav></details></aside>
        <div class="prose">{groups}
          {callout(e(ui["faq_still_label"]), fill(ui["faq_still_html"], p, l))}
        </div>
      </div>
    </div>"""
    ld = [breadcrumb_ld(L, ui, [("faq/", ui["crumb_questions"])]), {
        "@context": "https://schema.org", "@type": "FAQPage", "inLanguage": L[2],
        "mainEntity": [{"@type": "Question", "name": it["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(fill(it["a"], BASE, BASE + L[1]))}}
                       for grp in faq for it in grp["items"]]}]
    return page(L, "faq/", ui["faq_title"], ui["faq_description"], body, current="faq", jsonld=ld, og_title=ui["faq_og_title"])


def build_privacy(L):
    ui, sections = C[L[0]]["ui"], C[L[0]]["privacy"]

    def body(p, l):
        toc = "".join(f'<li><a href="#{s["id"]}"><span class="n">{ROMAN[i]}</span>{e(s["title"])}</a></li>' for i, s in enumerate(sections))
        secs = "".join(f'<h2 id="{s["id"]}"><span class="numeral">{ROMAN[i]}</span>&ensp;{e(s["title"])}</h2>{fill(s["body"], p, l)}' for i, s in enumerate(sections))
        summary = "".join(f'<div class="placard"><h3>{e(c["h"])}</h3><p>{e(c["p"])}</p></div>' for c in ui["privacy_summary"])
        note = f'<p class="updated translation-note">{fill(ui["privacy_translation_note"], p, l)}</p>' if ui.get("privacy_translation_note") else ""
        return f"""    <div class="wrap">
      <header class="page-head">
        {crumbs(l, ui, [("privacy/", ui["crumb_privacy"])])}
        <p class="label">{e(ui["privacy_label"])}</p>
        <h1>{e(ui["privacy_h1"])}</h1>
        <p class="lede">{e(ui["privacy_lede"])}</p>
        <p class="updated">{e(ui["privacy_updated"])}</p>
        {note}
      </header>
      <div class="summary-grid">{summary}</div>
      <div class="doc">
        <aside class="toc"><details open><summary>{e(ui["toc_contents"])}</summary><nav aria-label="{e(ui["toc_contents"])}"><p class="label">{e(ui["toc_contents"])}</p><ol>{toc}</ol></nav></details></aside>
        <article class="prose">{secs}</article>
      </div>
    </div>"""
    return page(L, "privacy/", ui["privacy_title"], ui["privacy_description"], body, current="privacy",
                jsonld=[breadcrumb_ld(L, ui, [("privacy/", ui["crumb_privacy"])])], og_title=ui["privacy_og_title"])


def build_sitemap(urls):
    rows = "\n".join(f"  <url><loc>{u}</loc><lastmod>{UPDATED_ISO}</lastmod></url>" for u in urls)
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n')


if __name__ == "__main__":
    urls = []
    for L in ACTIVE:
        urls.append(build_home(L))
        urls += build_guides(L)
        urls.append(build_faq(L))
        urls.append(build_privacy(L))
    build_sitemap(urls)
    print(f"built {len(urls)} pages in {len(ACTIVE)} language(s): {', '.join(L[0] for L in ACTIVE)}")
