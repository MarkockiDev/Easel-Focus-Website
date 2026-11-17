#!/usr/bin/env python3
"""Builds the site's inner pages (guides, questions, privacy) from the content below.

The output is plain HTML committed to the repo, so GitHub Pages needs no build step.
Run after editing this file:   python3 tools/build.py

The home page (index.html) is hand-written; keep its header and footer in step with
`header()` and `footer()` here.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://markockidev.github.io/Easel-Focus-Website/"   # change here (and in index.html) when easelfocus.app goes live
APP = "https://apps.apple.com/app/id6793262483"
FEEDBACK = "https://markockidev.canny.io/easel"
MAKER = "https://markockiadam.com"
EMAIL = "adam@easelfocus.app"
UPDATED = "17 November 2026"
UPDATED_ISO = "2026-11-17"

e = html.escape


# ───────────────────────── chrome ─────────────────────────

def header(p, current=""):
    def nav(href, label, key, cls=""):
        cur = ' aria-current="page"' if key == current else ""
        c = f' class="{cls}"' if cls else ""
        return f'<a{c} href="{href}"{cur}>{label}</a>'
    return f"""  <a class="skip" href="#main">Skip to content</a>
  <header class="top">
    <div class="wrap">
      <a class="brand" href="{p}./" aria-label="Easel, home">
        <img src="{p}assets/img/icon.jpg" alt="" width="36" height="36">
        Easel
      </a>
      <nav aria-label="Primary" class="label">
        {nav(p + "guides/", "Guides", "guides")}
        {nav(p + "faq/", '<span class="long">Questions</span><span class="short" aria-hidden="true">FAQ</span>', "faq")}
        <a class="get" href="{APP}">Download</a>
      </nav>
    </div>
  </header>"""


def footer(p):
    return f"""  <footer>
    <div class="wrap">
      <div class="row">
        <a class="brand" href="{p}./" aria-label="Easel, home"><img src="{p}assets/img/icon.jpg" alt="" width="36" height="36" loading="lazy">Easel</a>
        <nav aria-label="Footer">
          <a href="{APP}">App Store</a>
          <a href="{p}guides/">Guides</a>
          <a href="{p}faq/">Questions</a>
          <a href="{p}privacy/">Privacy policy</a>
          <a href="{FEEDBACK}">Feedback &amp; ideas</a>
          <a href="mailto:{EMAIL}">Contact</a>
          <a href="{MAKER}">The maker</a>
        </nav>
      </div>
      <p class="fine">Paintings are public-domain works from The Metropolitan Museum of Art’s Open Access collection. Easel is an independent app and is not affiliated with or endorsed by The Met. Apple, the Apple logo, iPhone and iPad are trademarks of Apple Inc., registered in the U.S. and other countries and regions. App Store is a service mark of Apple Inc.</p>
    </div>
  </footer>"""


def page(path, title, description, body, current="", jsonld=None, og_title=None):
    """path: '' for root, 'guides/', 'guides/pomodoro/' ..."""
    depth = path.count("/")
    p = "../" * depth
    url = BASE + path
    ld = ""
    for block in (jsonld or []):
        ld += '  <script type="application/ld+json">' + json.dumps(block, ensure_ascii=False) + "</script>\n"
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{url}">
  <meta name="apple-itunes-app" content="app-id=6793262483">
  <meta name="theme-color" content="#F5F2EC" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#161310" media="(prefers-color-scheme: dark)">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Easel">
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
  <link rel="stylesheet" href="{p}assets/site.css?v=4">
{ld}</head>
<body class="has-getbar">
{header(p, current)}

  <main id="main">
{body(p)}
  </main>

{footer(p)}
  <div class="getbar" role="complementary" aria-label="Get Easel">
    <img class="icon" src="{p}assets/img/icon.jpg" alt="" width="40" height="40">
    <span class="t"><b>Easel</b><span>Focus timer &amp; art</span></span>
    <a class="badge" href="https://apps.apple.com/app/id6793262483">
      <picture>
        <source srcset="{p}assets/img/app-store-badge-white.svg" media="(prefers-color-scheme: dark)">
        <img src="{p}assets/img/app-store-badge-black.svg" alt="Download on the App Store" width="120" height="40">
      </picture>
    </a>
  </div>
  <script src="{p}assets/site.js?v=4" defer></script>
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
    import re
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


def crumbs(p, trail):
    parts = [f'<a href="{p}./">Easel</a>']
    for href, label in trail[:-1]:
        parts.append(f'<a href="{p}{href}">{e(label)}</a>')
    parts.append(f'<span aria-current="page">{e(trail[-1][1])}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(parts) + "</nav>"


def breadcrumb_ld(trail):
    items = [{"@type": "ListItem", "position": 1, "name": "Easel", "item": BASE}]
    for i, (href, label) in enumerate(trail, start=2):
        items.append({"@type": "ListItem", "position": i, "name": label, "item": BASE + href})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def shot(src, alt, caption=None):
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure><div class="shot"><img src="{{p}}assets/img/{src}" width="603" height="1311" loading="lazy" alt="{e(alt)}"></div>{cap}</figure>'


def figs(*items):
    return '<div class="figs">' + "".join(items) + "</div>"


def callout(label, text):
    return f'<div class="callout"><span class="label">{label}</span>{text}</div>'


ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]


# ───────────────────────── guides ─────────────────────────
# Each guide: slug, title (h1), nav label, SEO title, description, body (HTML, may use {p}).

GUIDES = [
  dict(
    slug="getting-started", nav="Getting started", room="The first visit",
    title="Getting started with Easel",
    seo="Getting started with Easel, the focus timer that reveals a painting",
    desc="Your first focus session in Easel, step by step: choose how long to focus, begin, and watch a painting from The Met emerge from the fog until it’s fully revealed at 0:00.",
    lede="Easel is a focus timer with a reward you can see. Choose how long you’ll work, and a painting from The Met slowly emerges from the fog while you focus. Here’s your first session, from opening the app to the finished painting.",
    body="""
<h2 id="home">The home screen</h2>
<p>Everything starts on one quiet screen. From top to bottom:</p>
<ul>
  <li><strong>Gallery</strong> (top left): the paintings you’ve uncovered.</li>
  <li><strong>Settings</strong> (top right): appearance, sounds, reminders, widgets’ daily goal and more.</li>
  <li><strong>What will you focus on?</strong> An optional line for what you’re working on.</li>
  <li><strong>Single or Pomodoro</strong>: one session, or four focus blocks with short breaks.</li>
  <li><strong>Focus for</strong>: 5, 15, 25, 45 or 60 minutes, or <em>Custom</em> for anything from 5 to 120.</li>
  <li><strong>Focus with</strong>: which paintings to draw from. <em>All paintings</em> surprises you.</li>
  <li><strong>Begin</strong>.</li>
</ul>
""" + figs(shot("shot-home.jpg", "Easel’s home screen: Gallery and Settings buttons, the line What will you focus on?, Single or Pomodoro, durations of 5 to 60 minutes or Custom, Focus with All paintings, and Begin.", "The home screen, where every session starts."),
           shot("shot-setup.jpg", "The home screen with an intention typed in: Finish the chapter draft, 25 minutes selected.", "With an intention and 25 minutes chosen.")) + """
<h2 id="first-session">Your first session</h2>
<ol class="steps">
  <li><strong>Choose a length.</strong> 25 minutes is a good start. Tap <em>Custom</em> to pick any length from 5 to 120 minutes on a wheel.</li>
  <li><strong>Say what it’s for</strong> (optional). Type it in the line at the top, or leave it empty and Easel will ask you <em>“What will you focus on?”</em> when you tap Begin. See <a href="{p}guides/focus-question/">the focus question</a>.</li>
  <li><strong>Tap Begin.</strong> Easel picks a painting and loads it completely before the session starts, so the reveal never waits on your connection.</li>
  <li><strong>Work.</strong> The painting clears from the centre outward as the minutes pass. The timer sits quietly at the top; you don’t need to watch it.</li>
  <li><strong>At 0:00 the painting is fully revealed.</strong> A cream museum placard rises at the bottom with how long you focused, what for, the title, artist and date. Tap <strong>Done</strong> and it hangs in your gallery.</li>
</ol>
""" + figs(shot("shot-fog.jpg", "A focus session halfway through: a Cézanne portrait emerging from the fog, 2:23 remaining.", "Halfway: the fog is lifting."),
           shot("shot-revealed.jpg", "Cézanne’s Gustave Boyer in a Straw Hat, fully revealed at 0:00, with a cream museum placard: 5 minutes · Finish the chapter draft, the title and artist, info and share buttons, and Done.", "At 0:00: revealed, with its placard.")) + """
<h2 id="where-next">Where to go next</h2>
<ul>
  <li><a href="{p}guides/focus-sessions/">Focus sessions and the fog reveal</a>: locking your phone, ending early, sounds.</li>
  <li><a href="{p}guides/pomodoro/">Pomodoro</a>: four blocks with breaks, a new painting each time.</li>
  <li><a href="{p}guides/gallery/">Your gallery</a>: every painting you’ve earned, with its museum label.</li>
</ul>
""" + callout("Lost in the app?", "<p>Every screen in Easel has a way back: the <strong>‹ back</strong> button at the top left, the <strong>⌄</strong> chevron on Statistics, or a swipe down on sheets. You always return to the home screen. More in <a href=\"{p}guides/troubleshooting/#lost\">Troubleshooting</a>.</p>"),
  ),
  dict(
    slug="focus-sessions", nav="Focus sessions", room="During a session",
    title="Focus sessions and the fog reveal",
    seo="How Easel’s focus sessions and fog reveal work",
    desc="How a focus session works in Easel: the fog reveal, the timer, leaving the app or locking your phone, ending early, ambient music, sound effects and haptics.",
    lede="A session is the heart of Easel: one painting, slowly revealed while you work. This guide explains what happens during a session and what you can do while it runs.",
    body="""
<h2 id="reveal">How the reveal works</h2>
<p>Each session hangs a painting behind a soft, drifting fog. As time passes, it clears from the centre outward. The pace is gentle at first and opens up towards the end, so the last minutes feel like an arrival. At 0:00 the painting is completely clear, corners included.</p>
<p>Above the painting you’ll see the remaining time and, if you set one, your intention. Both are faint on purpose: Easel wants you looking at your work, not the clock.</p>
""" + figs(shot("shot-fog.jpg", "A session in progress, with the countdown, intention, mute button and End.", "The session screen: sound at the top left, End at the top right.")) + """
<h2 id="leaving">Leaving the app or locking your phone</h2>
<p>Go ahead. The timer is anchored to the moment your session will end, not to ticks while the app is open, so it keeps true time while Easel is in the background or your phone is locked. Come back and the painting is exactly as far along as it should be.</p>
<ul>
  <li>While Easel is open on a session, it keeps the screen from dimming so you can watch the reveal.</li>
  <li>On the Lock Screen and in the Dynamic Island, a <strong>Live Activity</strong> shows the countdown. See <a href="{p}guides/widgets-and-live-activities/">Widgets and Live Activities</a>.</li>
  <li>If the session finishes while you’re away, the painting is waiting for you when you return.</li>
</ul>
<h2 id="end-early">Ending a session early</h2>
<p>Tap <strong>End</strong> at the top right, then confirm. The painting won’t finish, so it isn’t added to your gallery, and the session doesn’t count towards your statistics or streak. In Pomodoro, ending early ends the whole set.</p>
<h2 id="sound">Sound, music and haptics</h2>
<ul>
  <li><strong>The speaker button</strong> (top left during a session) mutes or unmutes sound for the session.</li>
  <li><strong>Ambient music</strong>: quiet piano while a painting reveals. Turn it on in <em>Settings → During a session</em>.</li>
  <li><strong>Sound effects</strong>: the chime when a painting completes.</li>
  <li><strong>Haptic feedback</strong>: gentle taps on buttons and at the start and end of a session.</li>
</ul>
<h2 id="label">When the painting is revealed</h2>
<p>At 0:00 the whole painting is clear, and a museum placard rises at the bottom of the screen: the session’s length and your intention, then the painting’s title, artist and date. On the placard you can:</p>
<ul>
  <li>Tap <strong>ⓘ</strong> for the full museum label: medium, dimensions, credit line and a link to view the work at The Met. The label opens to exactly its own height; swipe down to close it.</li>
  <li>Tap <strong>Share</strong> to make a framed card for Stories or posts (see <a href="{p}guides/sharing/">Sharing</a>).</li>
  <li>Tap <strong>Done</strong> to hang it in your gallery and return to the home screen.</li>
</ul>
<p>Every few milestones (10, 25, 50, 100 paintings and beyond) Done opens a small celebration first.</p>
""" + figs(shot("shot-revealed.jpg", "Cézanne’s Gustave Boyer in a Straw Hat, fully revealed at 0:00, with a cream museum placard: 5 minutes · Finish the chapter draft, the title and artist, info and share buttons, and Done.", "The placard at 0:00."),
           shot("shot-label.jpg", "The museum label sheet over the painting: Gustave Boyer (b. 1840) in a Straw Hat, 1870–71, Paul Cézanne, with medium, dimensions, credit line and View at The Met.", "Tap ⓘ for the full museum label.")) + """
""",
  ),
  dict(
    slug="focus-question", nav="What will you focus on?", room="Intentions",
    title="What will you focus on? Setting an intention",
    seo="Setting a focus intention in Easel: What will you focus on?",
    desc="Give each Easel session a purpose: type an intention, reuse a recent one, or choose a subject like Study, Work, Writing or Reading. Your intention travels with the painting into your gallery.",
    lede="Every painting in Easel is earned for something. Naming what you’re about to work on makes a session easier to start, and later your gallery remembers what each painting was for.",
    body="""
<h2 id="type">Type it in</h2>
<p>On the home screen, tap <em>What will you focus on?</em> and type a short line, like <em>“Finish the chapter draft”</em>. Press <strong>Go</strong> on the keyboard to begin straight away. Intentions can be up to 60 characters, and the line stays filled in for your next session, ready for the next block of the same task.</p>
<h2 id="question">Or let Easel ask</h2>
<p>If the line is empty when you tap <strong>Begin</strong>, Easel opens a full-screen question: <em>What will you focus on?</em> Under it you’ll see the session about to start (for example <em>25 minutes · All paintings</em>), then two rooms:</p>
<ol class="steps">
  <li><strong>Lately</strong>: your three most recent intentions, one tap to reuse.</li>
  <li><strong>A subject</strong>: Study, Work, Writing, Reading, Creating, Planning, Practice or Thinking.</li>
</ol>
<p>Choosing one begins the session. To go back without starting, tap <strong>‹</strong> at the top left.</p>
""" + figs(shot("shot-setup.jpg", "The home screen with the intention Finish the chapter draft typed in.", "An intention, typed on the home screen."),
           shot("shot-question.jpg", "The full-screen focus question: What will you focus on? with recent intentions and subjects such as Study and Work.", "The focus question, when the line is empty.")) + """
<h2 id="where">Where your intention appears</h2>
<ul>
  <li>Faintly under the timer during the session.</li>
  <li>On the Live Activity, on your Lock Screen and in the Dynamic Island.</li>
  <li>In your gallery, as <em>“For: …”</em> on the painting’s page.</li>
  <li>On the share card, if you share that painting.</li>
</ul>
""" + callout("Private", "<p>Your intentions are stored only on your device. Easel never sends the text anywhere. See the <a href=\"{p}privacy/\">privacy policy</a>.</p>"),
  ),
  dict(
    slug="pomodoro", nav="Pomodoro", room="Pomodoro",
    title="Using Easel as a Pomodoro timer",
    seo="Pomodoro timer with paintings: how Pomodoro works in Easel",
    desc="Easel’s Pomodoro mode: four 25-minute focus blocks with 5-minute breaks, a new painting revealed in every block. How to start, skip a break and end a set.",
    lede="Pomodoro breaks long work into focused blocks with short rests between them. In Easel, every block reveals its own painting, so a full set leaves four new works in your gallery.",
    body="""
<h2 id="how">How a Pomodoro set works</h2>
<ul>
  <li><strong>Four focus blocks</strong> of 25 minutes each.</li>
  <li><strong>A 5-minute break</strong> after each of the first three blocks.</li>
  <li><strong>A new painting</strong> in every block, each revealed from fog like a single session.</li>
</ul>
<h2 id="start">Starting a set</h2>
<ol class="steps">
  <li>On the home screen, tap <strong>Pomodoro</strong>.</li>
  <li>Choose a collection under <em>Focus with</em>, if you like.</li>
  <li>Tap <strong>Begin</strong>. The focus question shows the set as <em>4 × 25 min</em>.</li>
</ol>
<h2 id="breaks">During a break</h2>
<p>When a block ends, its painting is revealed and saved, and your break begins. The break screen shows the painting you just earned and a countdown. Rest, stretch, look at the painting. When you’re ready, tap <strong>Begin next focus</strong>; you can start before the break is over.</p>
<h2 id="end">Ending a set early</h2>
<p>Tap <strong>End</strong> during a block or a break. Blocks you’ve already finished stay in your gallery; the block in progress doesn’t count.</p>
""" + callout("Tip", "<p>Pomodoro completions are celebrated with their own haptic pattern when the fourth painting is revealed. Turn haptics on or off in <em>Settings → During a session</em>.</p>"),
  ),
  dict(
    slug="collections", nav="Collections", room="Focus with",
    title="Choosing which paintings you focus with",
    seo="Easel collections: European paintings, Japanese prints, flowers & birds",
    desc="Focus with all 606 paintings or choose a collection in Easel: European Paintings, Japanese Prints, American Paintings, Flowers & Birds, a single artist like Hokusai or Rembrandt, or an era.",
    lede="Easel’s paintings come from a hand-picked selection of over 600 public-domain works in The Met’s collection. You can let Easel surprise you, or focus with one style, artist or era.",
    body="""
<h2 id="choose">Choose a collection</h2>
<ol class="steps">
  <li>On the home screen, tap the card under <strong>Focus with</strong> (it reads <em>All paintings</em> at first).</li>
  <li>Pick a collection. Each row shows how many of its works you’ve uncovered, like <em>22 / 90</em>.</li>
  <li>Tap <strong>Done</strong>. Your next sessions draw only from that collection, until you change it.</li>
</ol>
""" + figs(shot("shot-collections.jpg", "The Collections sheet: All paintings, then By style (European Paintings, Japanese Prints, American Paintings, Flowers & Birds) and By artist, each with a count of works uncovered.", "Collections, with your progress in each.")) + """
<h2 id="styles">By style</h2>
<ul>
  <li><strong>European Paintings</strong>: Rembrandt, Vermeer, Van Gogh, Cézanne, Corot, Courbet, Manet, Renoir, Degas and more.</li>
  <li><strong>Japanese Prints</strong>: Katsushika Hokusai, Utagawa Hiroshige and other Edo and Meiji masters.</li>
  <li><strong>American Paintings</strong>: Hudson River School landscapes by Kensett, Inness, Church and others.</li>
  <li><strong>Flowers &amp; Birds</strong>: John James Audubon, Ogata Kōrin and botanical masters.</li>
</ul>
<h2 id="artists">By artist and by era</h2>
<p>Below the styles, the sheet lists artists with several works in Easel, and eras from the Renaissance to the Modern era (1880 onward). Choose one to spend a week with Hokusai, or a month in the nineteenth century.</p>
<h2 id="curation">How the paintings are chosen</h2>
<p>Every work is in the public domain and comes from The Met’s Open Access collection. The selection favours celebrated works and is curated to be calm and suitable for everyone: Easel never picks a painting at random from the museum’s whole collection.</p>
""",
  ),
  dict(
    slug="gallery", nav="Your gallery", room="The gallery",
    title="Your gallery of earned paintings",
    seo="Your Easel gallery: every painting you’ve uncovered",
    desc="Every painting you reveal in Easel hangs in your gallery. Open one to see it large, read its museum label, see what you focused on, and share it.",
    lede="Each finished session hangs its painting in your gallery. Over weeks it becomes a quiet record of everything you’ve made time for.",
    body="""
<h2 id="open">Opening the gallery</h2>
<p>Tap the <strong>gallery button</strong> at the top left of the home screen. The gallery slides in from the left; tap <strong>‹</strong> to slide it back.</p>
<p>Paintings are arranged newest first. At the bottom, a card shows your total time in focus, paintings and current streak; tap it to open <a href="{p}guides/statistics/">Statistics</a>.</p>
""" + figs(shot("shot-gallery.jpg", "The gallery: a grid of earned paintings and a card showing 57h 40m in focus, 111 paintings, a 7-day streak.", "The gallery, with your focus totals at the bottom."),
           shot("shot-exhibit.jpg", "A painting’s page: Cézanne’s Gustave Boyer in a Straw Hat, with its title, date, artist and medium below.", "A painting’s own page, like a museum wall.")) + """
<h2 id="painting">A painting’s page</h2>
<p>Tap any painting to open its page: the work large, then its museum label (title, date, artist, medium, dimensions and more from The Met), then <em>Your visit</em>: the day and time you uncovered it, and what it was for.</p>
<ul>
  <li>Tap <strong>Share</strong> (top right) to make a framed card. See <a href="{p}guides/sharing/">Sharing</a>.</li>
  <li>Without a connection, the page shows what’s saved on your device and a short note that more details need the internet.</li>
</ul>
<h2 id="whole">Sharing the whole gallery</h2>
<p>The share button at the top right of the gallery makes a collage card of your latest paintings.</p>
""",
  ),
  dict(
    slug="sharing", nav="Sharing", room="Sharing",
    title="Sharing a painting you uncovered",
    seo="How to share a painting from Easel to Instagram Stories and more",
    desc="Share any painting you earned in Easel as a framed card, in Story (9:16) or Post (4:5) format. Save it to Photos or send it to Instagram, TikTok, X, Facebook, Messages and more.",
    lede="Every painting you uncover can become a small celebration: a card with the painting in a gilded frame and how long you focused for it.",
    body="""
<h2 id="make">Make a card</h2>
<ol class="steps">
  <li>Tap <strong>Share</strong>: on the finished painting at 0:00, on a painting’s page in your gallery, on the gallery itself, on a milestone or at the end of Year in Review.</li>
  <li>Choose <strong>Story (9:16)</strong> for Stories and Reels, or <strong>Post (4:5)</strong> for feeds.</li>
  <li>Tap <strong>Save</strong> to add it to Photos, or <strong>Share</strong> to open the share sheet.</li>
</ol>
""" + figs(shot("shot-share.jpg", "The share screen: a Story card reading I focused for 1h and uncovered, with Cézanne’s painting in a gilt frame, Save and Share buttons.", "The share screen, with Story and Post formats.")) + """
<h2 id="apps">Instagram, TikTok, X and others</h2>
<p>Instagram, TikTok, X, Facebook, Messages, WhatsApp and Mail all appear under <strong>Share</strong>, as long as the app is installed. When the destination accepts text, Easel adds a short line and a link to the App Store with the card.</p>
<h2 id="photos">Saving to Photos</h2>
<p>The first time you tap Save, iOS asks to let Easel <em>add</em> to your photo library. Easel can only add images; it can’t see or read your photos. If you declined, turn it on in the iPhone Settings app under <em>Apps → Easel → Photos</em>.</p>
""",
  ),
  dict(
    slug="statistics", nav="Statistics & streaks", room="In numbers",
    title="Statistics, streaks and milestones",
    seo="Focus statistics and streaks in Easel",
    desc="How Easel counts your focus time, paintings and streaks: the week chart, the 16-week focus calendar, your current and best streak, and milestones at 10, 25, 50 and 100 paintings.",
    lede="Easel keeps a calm record of your focus: time, paintings, streaks, a week at a glance and a calendar of every day you showed up.",
    body="""
<h2 id="open">Opening Statistics</h2>
<p>Open the gallery and tap the card at the bottom (time · paintings · streak). Statistics rises from the bottom of the screen; tap <strong>⌄</strong> to close it. On iPad with a keyboard, press <kbd>⌘</kbd><kbd>⇧</kbd><kbd>S</kbd>.</p>
""" + figs(shot("shot-stats.jpg", "Statistics: 57h 30m in focus, current streak 6, best streak 12, a bar chart of the past seven days and a 16-week calendar.", "Statistics: totals, streaks, the week and the season.")) + """
<h2 id="what">What you’ll see</h2>
<ul>
  <li><strong>Time in focus</strong>: the total of all completed sessions.</li>
  <li><strong>Current streak and best streak</strong>: consecutive days with at least one completed session.</li>
  <li><strong>Past seven days</strong>: a bar per day, today on the right.</li>
  <li><strong>The last 16 weeks</strong> (26 on iPad): each square is a day; deeper ink means more time in focus.</li>
  <li><strong>Paintings</strong>: how many different works you’ve uncovered, and how many sessions you’ve completed.</li>
</ul>
<h2 id="streaks">How streaks are counted</h2>
<p>A day counts when you complete at least one session. Your current streak stays alive through today, so a streak from yesterday isn’t broken until the day is over. Sessions ended early don’t count.</p>
<h2 id="milestones">Milestones</h2>
<p>At 10, 25, 50, 100, 250, 500 and 1,000 paintings, Easel pauses for a moment: your three latest paintings, fanned in gilt frames, and the number. You can share it, or continue.</p>
<p>And every December there’s <a href="{p}guides/year-in-review/">Year in Review</a>.</p>
""",
  ),
  dict(
    slug="year-in-review", nav="Year in Review", room="The year",
    title="Year in Review: your year in focus",
    seo="Easel Year in Review: your year of focus as an exhibition",
    desc="Every December, Easel’s Year in Review turns your year of focus into a short exhibition: hours in focus, paintings revealed, your favourite artist, longest streak and the painting of the year.",
    lede="Every December, Easel looks back on your year as a short, self-playing exhibition, set to Handel’s Water Music, ending with a card you can share.",
    body="""
<h2 id="when">When it appears</h2>
<p>From <strong>15 December to 2 January</strong> each year, an invitation appears at the top of Statistics: <em>“Your year in Easel”</em>, with <em>Enter the exhibition</em>. In January it looks back on the year that just ended. Sessions up to 31 December are always included.</p>
<p>If notifications are on, Easel sends at most three gentle reminders in that season: on 15 December, 30 December and 2 January.</p>
<h2 id="pages">What’s inside</h2>
<ol class="steps">
  <li>The year.</li>
  <li>Your hours in focus, and when you focus best (morning, afternoon or evening).</li>
  <li>Paintings revealed, and the artist you kept most.</li>
  <li>Your longest run of days, and your fullest month.</li>
  <li>The painting of the year: the one you earned with your longest single focus.</li>
  <li>A thank-you, and a gilded card of your year to share as a Story or post.</li>
</ol>
<h2 id="controls">Watching it</h2>
<ul>
  <li>It plays by itself, a few seconds per page.</li>
  <li><strong>Tap the right side</strong> to skip ahead, <strong>the left side</strong> to go back.</li>
  <li><strong>Touch and hold</strong> to pause.</li>
  <li><strong>Swipe down</strong> to close.</li>
  <li>With VoiceOver, swipe to move between pages.</li>
</ul>
""",
  ),
  dict(
    slug="widgets-and-live-activities", nav="Widgets & Live Activities", room="Beyond the app",
    title="Widgets, Live Activities, Siri and Control Center",
    seo="Easel widgets: Painting of the Day, Live Activity and Control Center",
    desc="Add Easel’s Painting of the Day and Focus & Streak widgets to your Home Screen, Lock Screen or StandBy, follow sessions in a Live Activity, and start focusing from Siri, Shortcuts or Control Center.",
    lede="Easel lives beyond the app: a painting of the day that clears as you focus, your streak at a glance, a countdown on your Lock Screen, and a button in Control Center.",
    body="""
<h2 id="painting-of-the-day">Painting of the Day widget</h2>
<p>Each morning a new painting hangs in the widget, hidden in fog. Every minute of focus clears a little more, from the centre outward. Reach your daily goal and it’s fully revealed, with its title and artist.</p>
<p>Set the goal in <em>Settings → Your daily ritual → Focus each day</em>: 15 to 120 minutes, 25 by default.</p>
<h2 id="add">Adding a widget</h2>
<ol class="steps">
  <li>Touch and hold an empty area of your Home Screen until the apps jiggle.</li>
  <li>Tap <strong>Edit</strong> (or <strong>+</strong>) at the top, then <strong>Add Widget</strong>.</li>
  <li>Search for <strong>Easel</strong>, choose <em>Painting of the Day</em> or <em>Focus &amp; Streak</em>, pick a size and tap <strong>Add Widget</strong>.</li>
</ol>
<p>Both widgets also come in Lock Screen sizes (customise your Lock Screen and tap the widget area), and the small size works in StandBy.</p>
<h2 id="live-activity">Live Activity and Dynamic Island</h2>
<p>When a session starts, Easel shows its countdown on the Lock Screen and, on iPhones that have one, in the Dynamic Island, with your intention and a softly blurred hint of the painting. When the session ends it shows the painting revealed.</p>
""" + figs(shot("shot-live.jpg", "The iPhone Lock Screen showing Easel’s Live Activity with the intention Finish the chapter draft and a countdown.", "A session’s Live Activity on the Lock Screen.")) + """
<p>Not seeing it? In the iPhone Settings app, open <em>Apps → Easel</em> and make sure <strong>Live Activities</strong> is on.</p>
<h2 id="siri">Siri and Shortcuts</h2>
<p>Say <em>“Start a focus session in Easel”</em>, <em>“Start focusing with Easel”</em> or <em>“Reveal a painting in Easel”</em>. In the Shortcuts app, the <strong>Start Focus</strong> action can set a length from 5 to 120 minutes, handy for automations.</p>
<h2 id="control-center">Control Center (iOS 18 and later)</h2>
<p>Open Control Center, tap <strong>+</strong>, then <strong>Add a Control</strong>, and search for Easel. One tap opens Easel and begins with your current choice.</p>
""",
  ),
  dict(
    slug="reminders-and-notifications", nav="Reminders", room="Your daily ritual",
    title="Daily reminders and notifications",
    seo="Easel daily focus reminder and notifications",
    desc="Turn on Easel’s gentle daily reminder, choose its time, and learn which other notifications Easel can send and how to turn each one off.",
    lede="Easel can send one gentle note a day to bring you back to your focus, naming that day’s painting. Notifications are always optional.",
    body="""
<h2 id="daily">Daily reminder</h2>
<ol class="steps">
  <li>Open <strong>Settings</strong> (top right of the home screen).</li>
  <li>In <em>II · Your daily ritual</em>, turn on <strong>Daily reminder</strong>. iOS asks for permission the first time.</li>
  <li>Choose a time (9:00 by default).</li>
</ol>
<p>If you’ve already focused that day, or the time has passed, the reminder moves to tomorrow. You can also turn it on from the last page of the introduction.</p>
""" + figs(shot("shot-settings.jpg", "Settings: During a session (ambient music, sound effects, haptic feedback), Your daily ritual (Focus each day, Daily reminder) and Support (Become a Patron, Saturday note).", "Settings: your daily ritual and support.")) + """
<h2 id="others">Other notifications</h2>
<ul>
  <li><strong>Year in Review</strong>: up to three notes in its season (15 December, 30 December, 2 January), only if you focused that year.</li>
  <li><strong>Saturday note</strong>: a short weekly word, on Saturday mornings, about supporting Easel. Turn it off any time in <em>Settings → Support → Saturday note</em>. It stops by itself once you’ve tipped.</li>
</ul>
<p>Easel never sends notifications unless you’ve allowed them.</p>
<h2 id="off">Turning notifications off</h2>
<p>Switch off the individual notes in Easel’s Settings, or turn off all of them in the iPhone Settings app under <em>Apps → Easel → Notifications</em>.</p>
""",
  ),
  dict(
    slug="settings-and-appearance", nav="Settings & appearance", room="Settings",
    title="Settings: day and night, sounds, language",
    seo="Easel settings: dark mode, sounds, haptics and language",
    desc="A tour of Easel’s Settings: By day, By night or Automatic appearance, ambient music, sound effects and haptics, daily goal, language, the introduction, privacy and feedback.",
    lede="Easel’s Settings are laid out like an exhibition guide: today’s painting at the top, then numbered rooms of preferences.",
    body="""
<h2 id="open">Opening Settings</h2>
<p>Tap the <strong>gear</strong> at the top right of the home screen. Settings slides in from the right; tap <strong>‹</strong> to close it. On iPad with a keyboard, press <kbd>⌘</kbd><kbd>,</kbd>.</p>
""" + figs(shot("shot-day.jpg", "Settings by day: On the easel today, and Appearance set to By day.", "By day."),
           shot("shot-night.jpg", "Settings by night: the same screen on a deep charcoal wall.", "By night.")) + """
<h2 id="rooms">The rooms</h2>
<ol class="steps">
  <li><strong>The gallery</strong>: Appearance. <em>By day</em> is a warm, lit wall; <em>By night</em> a deep charcoal room; <em>Automatic</em> follows your iPhone’s light and dark setting.</li>
  <li><strong>During a session</strong>: ambient music, sound effects, haptic feedback.</li>
  <li><strong>Your daily ritual</strong>: <em>Focus each day</em> (the goal that clears the Painting of the Day widget) and the daily reminder.</li>
  <li><strong>Support</strong>: <a href="{p}guides/patronage/">Become a Patron</a> and the Saturday note.</li>
  <li><strong>About Easel</strong>: language, about the maker, show the introduction again, privacy policy, and feedback.</li>
</ol>
<h2 id="language">Language</h2>
<p>Easel speaks English, Polish, Spanish, French, Simplified Chinese, Hindi, Japanese, Korean and Brazilian Portuguese. Tap <strong>Language</strong> in Settings to open iOS’s page for Easel and choose one; Easel restarts in the new language.</p>
<h2 id="intro">See the introduction again</h2>
<p>Tap <strong>Show introduction</strong> in <em>About Easel</em> to replay the four-page tour of how Easel works.</p>
""",
  ),
  dict(
    slug="patronage", nav="Patronage", room="Support",
    title="Patronage: supporting Easel",
    seo="Is Easel free? Patronage and optional tips",
    desc="Easel is free, with no ads and no subscription. If you’d like to support it, you can leave a one-time tip: A Fine Brush, A Box of Pigments or A Gilded Frame. Tips unlock nothing.",
    lede="Easel is free and made by one person. Every gallery has its patrons; if Easel brings some calm to your days, you can become one of them. Only if you’d like to.",
    body="""
<h2 id="gifts">The gifts</h2>
<p>Open <em>Settings → Support → Become a Patron</em>. There are three one-time gifts:</p>
<ul>
  <li><strong>A Fine Brush</strong>: for the small, careful strokes that make the app better.</li>
  <li><strong>A Box of Pigments</strong>: fresh colour for whatever comes next.</li>
  <li><strong>A Gilded Frame</strong>: hangs the whole work on the wall. A true patron’s gift.</li>
</ul>
<p>Prices are shown in your local currency by the App Store.</p>
""" + figs(shot("shot-patronage.jpg", "The Patronage page: Every gallery has its patrons, with three gifts: A Fine Brush $2.99, A Box of Pigments $4.99 and A Gilded Frame $9.99.", "Patronage, in Settings.")) + """
<h2 id="what-it-does">What a tip does</h2>
<p>Nothing changes in the app: everything in Easel is already yours. Tips are one-time purchases, never subscriptions, and are handled entirely by Apple. Once you’ve tipped, the Saturday note stops.</p>
<p>Other ways to help that cost nothing: rate Easel on the App Store, share a painting, or send an idea on the <a href=\"""" + FEEDBACK + """\">feedback board</a>.</p>
""",
  ),
  dict(
    slug="troubleshooting", nav="Troubleshooting", room="Help",
    title="Troubleshooting and finding your way",
    seo="Easel help: troubleshooting and finding your way around",
    desc="Help for Easel: getting back to the home screen, a painting that won’t load, a missing Live Activity or reminder, the widget fog not clearing, keyboard shortcuts on iPad, and how to contact us.",
    lede="Something not where you expected? Start here. If your question isn’t answered, write to us, and we’ll help.",
    body="""
<h2 id="lost">Getting back to the home screen</h2>
<ul>
  <li><strong>Gallery</strong> and <strong>Settings</strong> close with <strong>‹</strong> at the top left (or a swipe from the edge). The gallery slides back to the left, Settings to the right.</li>
  <li><strong>Statistics</strong> closes with <strong>⌄</strong> at the top left.</li>
  <li><strong>Sheets</strong> (collections, share, museum label) close with <strong>Done</strong> or a swipe down.</li>
  <li><strong>The focus question</strong> closes with <strong>‹</strong> without starting a session.</li>
  <li><strong>During a session</strong>, <strong>End</strong> (then confirm) returns you home.</li>
  <li>On iPad with a keyboard, <kbd>Esc</kbd> goes back from anywhere.</li>
</ul>
<h2 id="wont-load">“The painting couldn’t be loaded”</h2>
<p>Easel downloads each new painting before the session starts, so it needs an internet connection when you tap Begin. Check your connection and tap <strong>Try Again</strong>. Paintings you’ve already seen are kept on your device, so your gallery still works offline.</p>
<h2 id="live">No Live Activity on the Lock Screen</h2>
<p>Open the iPhone Settings app → <em>Apps → Easel</em> and turn on <strong>Live Activities</strong>. If you tapped <em>Don’t Allow</em> on the first prompt, this is where to change it.</p>
<h2 id="reminder">The daily reminder doesn’t arrive</h2>
<ul>
  <li>Check that notifications are on in the iPhone Settings app → <em>Apps → Easel → Notifications</em>.</li>
  <li>If you’ve already focused today, the reminder waits until tomorrow. That’s by design.</li>
  <li>Focus modes and Scheduled Summary can hold notifications back.</li>
</ul>
<h2 id="widget">The widget’s fog isn’t clearing</h2>
<p>Only completed sessions clear the fog; sessions ended early don’t. Your daily goal is set in <em>Settings → Focus each day</em>. Widgets refresh when Easel saves a session; if one seems stuck, open Easel once.</p>
<h2 id="streak">My streak reset</h2>
<p>A streak counts consecutive days with at least one completed session. A day with no completed session ends it. Your best streak is kept in Statistics.</p>
<h2 id="keyboard">Keyboard shortcuts on iPad</h2>
<div class="table-wrap"><table class="data">
  <tr><th scope="col">Keys</th><th scope="col">Does</th></tr>
  <tr><td><kbd>Return</kbd></td><td>Begin a session; Done when a painting is revealed</td></tr>
  <tr><td><kbd>Esc</kbd></td><td>End a session (with confirmation), close a panel</td></tr>
  <tr><td><kbd>⌘</kbd> <kbd>G</kbd></td><td>Open the gallery</td></tr>
  <tr><td><kbd>⌘</kbd> <kbd>,</kbd></td><td>Open Settings</td></tr>
  <tr><td><kbd>⌘</kbd> <kbd>⇧</kbd> <kbd>S</kbd></td><td>Open Statistics</td></tr>
</table></div>
<h2 id="data">Moving to a new iPhone</h2>
<p>Your gallery and history live on your device. They move with an iPhone backup or a direct transfer to a new iPhone; Easel has no account or server of its own. Deleting Easel deletes them.</p>
<h2 id="contact">Still stuck?</h2>
<p>Write to <a href="mailto:""" + EMAIL + """\">""" + EMAIL + """</a>, or post on the <a href=\"""" + FEEDBACK + """\">feedback board</a>. You can also browse <a href="{p}faq/">questions and answers</a>.</p>
""",
  ),
]


def guide_toc(p, current):
    items = []
    for i, g in enumerate(GUIDES):
        cur = ' aria-current="page"' if g["slug"] == current else ""
        items.append(f'<li><a href="{p}guides/{g["slug"]}/"{cur}><span class="n">{ROMAN[i]}</span>{e(g["nav"])}</a></li>')
    return f"""<aside class="toc">
          <details open><summary>All guides</summary>
            <nav aria-label="Guides"><p class="label">The guides</p><ol>{"".join(items)}</ol></nav>
          </details>
        </aside>"""


def build_guides():
    urls = []
    for i, g in enumerate(GUIDES):
        prev_g = GUIDES[i - 1] if i > 0 else None
        next_g = GUIDES[i + 1] if i + 1 < len(GUIDES) else None
        trail = [("guides/", "Guides"), (f"guides/{g['slug']}/", g["nav"])]

        def body(p, g=g, i=i, prev_g=prev_g, next_g=next_g, trail=trail):
            pager = '<nav class="pager" aria-label="More guides">'
            if prev_g:
                pager += f'<a class="prev" href="{p}guides/{prev_g["slug"]}/"><span class="label">‹ Previous</span><span>{e(prev_g["nav"])}</span></a>'
            if next_g:
                pager += f'<a class="next" href="{p}guides/{next_g["slug"]}/"><span class="label">Next ›</span><span>{e(next_g["nav"])}</span></a>'
            pager += "</nav>"
            content = g["body"].replace("{p}", p)
            return f"""    <div class="wrap">
      <header class="page-head">
        {crumbs(p, trail)}
        <p class="label"><span class="numeral">{ROMAN[i]}</span> &nbsp;{e(g["room"])}</p>
        <h1>{e(g["title"])}</h1>
        <p class="lede">{g["lede"]}</p>
      </header>
      <div class="doc">
        {guide_toc(p, g["slug"])}
        <article class="prose">
{content}
          {pager}
        </article>
      </div>
    </div>"""

        ld = [breadcrumb_ld(trail), {
            "@context": "https://schema.org", "@type": "TechArticle",
            "headline": g["title"], "description": g["desc"], "dateModified": UPDATED_ISO,
            "about": {"@type": "MobileApplication", "name": "Easel: Focus Timer & Art", "operatingSystem": "iOS"},
            "author": {"@type": "Person", "name": "Adam", "url": MAKER},
            "mainEntityOfPage": BASE + f"guides/{g['slug']}/",
        }]
        urls.append(page(f"guides/{g['slug']}/", g["seo"], g["desc"], body, current="guides", jsonld=ld, og_title=g["title"]))

    def hub(p):
        cards = "".join(
            f'<a class="card" href="{p}guides/{g["slug"]}/"><span class="n">{ROMAN[i]}</span><h2>{e(g["nav"])}</h2><p>{e(g["desc"].split(". ")[0].rstrip("."))}.</p></a>'
            for i, g in enumerate(GUIDES))
        return f"""    <div class="wrap">
      <header class="page-head">
        {crumbs(p, [("guides/", "Guides")])}
        <p class="label">The exhibition guide</p>
        <h1>How to use Easel</h1>
        <p class="lede">Short, illustrated guides to every room of the app, from your first session to widgets, Pomodoro and Year in Review. If you ever lose your way in Easel, you’ll find it again here.</p>
      </header>
      <div class="cards">{cards}</div>
    </div>"""
    urls.insert(0, page("guides/", "How to use Easel: guides to the focus timer that reveals paintings",
                        "Illustrated guides to Easel, the iPhone and iPad focus timer: your first session, the fog reveal, Pomodoro, collections, your gallery, sharing, statistics, widgets, reminders and troubleshooting.",
                        hub, current="guides",
                        jsonld=[breadcrumb_ld([("guides/", "Guides")])], og_title="How to use Easel"))
    return urls


# ───────────────────────── questions ─────────────────────────

FAQ = [
  ("About Easel", [
    ("What is Easel?", "Easel is a focus timer for iPhone and iPad. You choose how long you’ll focus, and a public-domain painting from The Metropolitan Museum of Art slowly emerges from fog while you work. At 0:00 it’s fully revealed and hangs in your own gallery. <a href=\"{p}guides/getting-started/\">Get started</a>."),
    ("Is Easel free?", "Yes. Easel is free to download and use, with no ads, no subscription and nothing locked. If you’d like to support it, you can leave an optional one-time tip in Settings → Become a Patron. <a href=\"{p}guides/patronage/\">About patronage</a>."),
    ("Which devices does Easel run on?", "iPhone and iPad with iOS or iPadOS 17 or later. Some features need newer versions: the Control Center button needs iOS 18, and Liquid Glass styling appears on iOS 26."),
    ("Which languages does Easel support?", "English, Polish, Spanish, French, Simplified Chinese, Hindi, Japanese, Korean and Brazilian Portuguese. Change it in Settings → Language."),
    ("Do I need an account?", "No. There’s no sign-up, login or account of any kind. Open the app and begin."),
  ]),
  ("The paintings", [
    ("Where do the paintings come from?", "From The Met’s Open Access collection: works in the public domain that the museum shares freely. Easel draws from a hand-picked selection of more than 600, including European paintings, Japanese prints, American landscapes and flowers and birds. Easel is independent and not affiliated with The Met."),
    ("Are the paintings suitable for all ages?", "Easel only ever picks from its own curated selection of celebrated, calm works, never at random from the museum’s whole collection, and the selection is filtered to avoid nudity and violent scenes."),
    ("Can I choose which paintings I see?", "Yes. Tap the card under “Focus with” on the home screen and choose a style (European Paintings, Japanese Prints, American Paintings, Flowers &amp; Birds), an artist or an era. <a href=\"{p}guides/collections/\">How collections work</a>."),
    ("Do I keep the paintings I uncover?", "Yes. Every completed session hangs its painting in your gallery, with its museum label, the date and what you were focusing on. <a href=\"{p}guides/gallery/\">Your gallery</a>."),
    ("Can I learn more about a painting?", "Tap ⓘ on a revealed painting, or open it in your gallery, to read its museum label: artist, date, medium, dimensions, credit line and a link to view it at The Met."),
  ]),
  ("Focusing", [
    ("How long can a session be?", "Choose 5, 15, 25, 45 or 60 minutes, or tap Custom for any length from 5 to 120 minutes."),
    ("Does Easel work as a Pomodoro timer?", "Yes. Pomodoro mode runs four 25-minute focus blocks with 5-minute breaks, and every block reveals its own painting. <a href=\"{p}guides/pomodoro/\">How Pomodoro works</a>."),
    ("Can I leave the app or lock my phone during a session?", "Yes. The timer keeps true time in the background, and a Live Activity shows the countdown on your Lock Screen and in the Dynamic Island. When you come back, the painting is exactly as far along as it should be."),
    ("What happens if I end a session early?", "The painting won’t finish, so it isn’t added to your gallery, and the session doesn’t count towards your time or streak. In Pomodoro, ending early ends the whole set; blocks you finished are kept."),
    ("What is “What will you focus on?”", "An optional intention for each session. Type it on the home screen, or let Easel ask when you tap Begin, with your recent intentions and subjects like Study, Work or Writing. <a href=\"{p}guides/focus-question/\">Setting an intention</a>."),
    ("Does Easel work offline?", "Easel needs a connection to fetch a new painting when you tap Begin; it downloads the whole image before the session starts, so the reveal never waits. Paintings you’ve seen are kept on your device, so your gallery works offline."),
  ]),
  ("Progress", [
    ("How are streaks counted?", "A day counts when you complete at least one session. Your current streak counts consecutive days, and Statistics also keeps your best streak. <a href=\"{p}guides/statistics/\">Statistics and streaks</a>."),
    ("What is Year in Review?", "Every year from 15 December to 2 January, Easel turns your year of focus into a short, self-playing exhibition, with your hours, paintings, favourite artist, longest run and painting of the year, ending with a card to share. <a href=\"{p}guides/year-in-review/\">Year in Review</a>."),
    ("How do I share a painting?", "Tap Share on a revealed painting or a painting in your gallery, choose Story (9:16) or Post (4:5), then Save to Photos or Share to Instagram, TikTok, X, Messages and more. <a href=\"{p}guides/sharing/\">Sharing</a>."),
  ]),
  ("Widgets and notifications", [
    ("Does Easel have widgets?", "Yes: Painting of the Day, which starts each day in fog and clears as you focus until your daily goal reveals it, and Focus &amp; Streak. Both work on the Home Screen, the Lock Screen and in StandBy. <a href=\"{p}guides/widgets-and-live-activities/\">Widgets and Live Activities</a>."),
    ("Can I start a session with Siri or Control Center?", "Yes. Say “Start a focus session in Easel”, use the Start Focus action in Shortcuts, or add Easel’s button to Control Center on iOS 18 and later."),
    ("Why don’t I see the Live Activity?", "In the iPhone Settings app, open Apps → Easel and turn on Live Activities."),
    ("What notifications does Easel send?", "Only ones you’ve allowed: an optional daily reminder at a time you choose, up to three Year in Review notes in December and early January, and a short Saturday note about supporting Easel, which you can turn off in Settings and which stops once you’ve tipped. <a href=\"{p}guides/reminders-and-notifications/\">Reminders and notifications</a>."),
  ]),
  ("Privacy and support", [
    ("Does Easel collect my data?", "Your sessions, gallery and intentions stay on your device. Easel sends anonymous usage statistics and crash reports, never linked to you, to improve the app, and it doesn’t track you or show ads. The <a href=\"{p}privacy/\">privacy policy</a> lists exactly what is sent."),
    ("How do I delete my data?", "Delete Easel from your device; everything it stored is removed with it. For the anonymous statistics, write to " + EMAIL + "."),
    ("Will my gallery move to a new iPhone?", "Yes, with an iPhone backup or a direct transfer to the new iPhone. Easel has no account or server, so your gallery lives only on your devices and their backups."),
    ("I’m lost in the app. How do I get back?", "Every screen has a way home: ‹ at the top left of the gallery, Settings and the focus question; ⌄ on Statistics; Done or a swipe down on sheets; End during a session. <a href=\"{p}guides/troubleshooting/#lost\">Finding your way</a>."),
    ("How can I contact the developer or suggest a feature?", "Write to <a href=\"mailto:" + EMAIL + "\">" + EMAIL + "</a>, or post and vote on ideas on the <a href=\"" + FEEDBACK + "\">feedback board</a>."),
  ]),
]


def strip_tags(s):
    import re
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)


def build_faq():
    def body(p):
        groups = ""
        toc = ""
        for gi, (group, qas) in enumerate(FAQ):
            gid = "q-" + group.lower().replace(" ", "-")
            toc += f'<li><a href="#{gid}"><span class="n">{ROMAN[gi]}</span>{e(group)}</a></li>'
            items = "".join(
                f'<details><summary>{e(q)}</summary><div class="answer"><p>{a.replace("{p}", p)}</p></div></details>'
                for q, a in qas)
            groups += f'<h2 id="{gid}">{e(group)}</h2><div class="qa">{items}</div>'
        return f"""    <div class="wrap">
      <header class="page-head">
        {crumbs(p, [("faq/", "Questions")])}
        <p class="label">Questions &amp; answers</p>
        <h1>Questions about Easel</h1>
        <p class="lede">Everything people ask about the focus timer that reveals a painting: the paintings, sessions, Pomodoro, streaks, widgets, privacy and more. For step-by-step help, see the <a href="{p}guides/">guides</a>.</p>
      </header>
      <div class="doc">
        <aside class="toc"><details open><summary>Topics</summary><nav aria-label="Topics"><p class="label">Topics</p><ol>{toc}</ol></nav></details></aside>
        <div class="prose">{groups}
          {callout("Still wondering?", f'<p>Write to <a href="mailto:{EMAIL}">{EMAIL}</a> or ask on the <a href="{FEEDBACK}">feedback board</a>.</p>')}
        </div>
      </div>
    </div>"""
    ld = [breadcrumb_ld([("faq/", "Questions")]), {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a.replace("{p}", BASE))}}
                       for _, qas in FAQ for q, a in qas]}]
    return page("faq/", "Easel questions & answers: the focus timer that reveals paintings",
                "Answers about Easel, the iPhone and iPad focus timer: is it free, where the paintings come from, Pomodoro, offline use, streaks, widgets, Live Activities, notifications and privacy.",
                body, current="faq", jsonld=ld, og_title="Questions about Easel")


# ───────────────────────── privacy ─────────────────────────

PRIVACY = [
  ("who", "Who we are", f"""
<p>Easel (“the app”, “we”, “us”) is a focus timer for iPhone and iPad made by <strong>Adam</strong>, an independent developer. Adam is the controller of the limited data described here.</p>
<p>Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<p>This policy covers the Easel app (including its widgets, Live Activities, Siri and Control Center features) and this website.</p>
"""),
  ("on-device", "What stays on your device", """
<p>Most of what Easel knows about you never leaves your iPhone or iPad. Easel has no account, no login and no server that stores your data. On your device it keeps:</p>
<ul>
  <li><strong>Your focus history</strong>: for each completed session, the painting, when it started and finished, its length, Single or Pomodoro, and the intention you typed or chose, if any. This powers your gallery, Statistics, streaks, milestones and Year in Review.</li>
  <li><strong>Your recent intentions</strong>, offered again under “Lately”.</li>
  <li><strong>Preferences</strong>: appearance, ambient music, sound effects, haptics, the chosen collection and duration, your daily goal, the daily reminder and its time, the Saturday note, and whether you’ve seen the introduction.</li>
  <li><strong>A cache of painting images</strong>, so your gallery works offline. Older images are removed automatically.</li>
  <li><strong>Widget and Live Activity data</strong>: today’s painting, your focus minutes today, your streak, and small images, kept in a container shared only between Easel and its own widgets.</li>
  <li><strong>Small app records</strong>: which milestones and rating prompts have been shown, and whether you’ve left a tip (so the Saturday note can stop).</li>
</ul>
<p>We can’t see any of this. It’s included in your device backups (iCloud or computer) according to your own Apple settings, and it’s deleted when you delete Easel.</p>
"""),
  ("analytics", "Anonymous usage statistics", """
<p>To understand which features are used and to make Easel better, the App Store version of Easel sends <strong>anonymous usage events</strong> to PostHog, an analytics service, using its <strong>EU cloud</strong>. Events are tied to a random identifier created on your device when Easel is first opened, never to your name, email, Apple ID or advertising identifier. We never call PostHog’s “identify” feature, so no person profile is ever built.</p>
<p>The events Easel sends, and the details they carry:</p>
<div class="table-wrap"><table class="data">
  <tr><th scope="col">Event</th><th scope="col">Details sent with it</th></tr>
  <tr><td>Session started</td><td>Single or Pomodoro, length in minutes, collection name, whether an intention was set (yes/no), and which of the eight fixed subjects was picked, if one was. <strong>Never the text you type.</strong></td></tr>
  <tr><td>Session completed</td><td>Single or Pomodoro, length, the Met object number of the painting</td></tr>
  <tr><td>Session ended early</td><td>Single or Pomodoro, length, how far along it was (or how many blocks were done)</td></tr>
  <tr><td>Pomodoro completed</td><td>Number of blocks</td></tr>
  <tr><td>Introduction finished</td><td>Whether it was skipped or completed, and on which page</td></tr>
  <tr><td>Collection chosen</td><td>The collection’s name</td></tr>
  <tr><td>Share opened · Card saved</td><td>Which card (painting, gallery, year, milestone) and format (Story or Post)</td></tr>
  <tr><td>Reminder turned on/off</td><td>On or off</td></tr>
  <tr><td>Year in Review opened</td><td>The year</td></tr>
  <tr><td>Milestone reached</td><td>The milestone number</td></tr>
  <tr><td>Patronage opened · Tip given</td><td>Which gift and where it was opened from; no payment details</td></tr>
  <tr><td>Rating prompt requested</td><td>Which stage (first, second, third)</td></tr>
  <tr><td>Notification opened</td><td>Which kind (reminder, Year in Review, Saturday note)</td></tr>
  <tr><td>Screen viewed</td><td>Gallery, Statistics, Settings or Painting</td></tr>
  <tr><td>App lifecycle</td><td>Installed, updated, opened, sent to background (sent automatically by PostHog’s SDK)</td></tr>
</table></div>
<p>With each event, PostHog’s SDK also records <strong>technical context</strong>: app version and build, iOS version, device model, screen size, language and region settings, time zone, and the time of the event. Like any internet service, PostHog receives your device’s <strong>IP address</strong> when events are sent and may use it to estimate an approximate location, such as your country. We don’t use it to identify you.</p>
<p><strong>We never collect</strong>: your name, email or contacts; the text of your intentions or anything you type; precise location; photos; health data; the advertising identifier (IDFA); screen recordings or session replays.</p>
<p>Development builds of Easel never send events.</p>
"""),
  ("crashes", "Crash and error reports", """
<p>If Easel crashes, a crash report is prepared on your device and sent to PostHog (EU cloud) the next time you open the app. Easel also reports a small number of unexpected errors, labelled with where they happened (for example, “a painting failed to load”). These reports contain technical details: the error, the code path (stack trace), app and iOS versions and device model, under the same anonymous identifier. Ordinary “no internet” errors are not reported. We use crash reports only to find and fix bugs.</p>
"""),
  ("met", "Paintings from The Met", """
<p>Easel downloads painting images and information from The Metropolitan Museum of Art’s Open Access API (<code>collectionapi.metmuseum.org</code> and <code>images.metmuseum.org</code>). These requests ask only for artworks, by their public object number. They contain nothing about you, but, as with visiting any website, The Met’s servers can see your device’s IP address. The Met’s handling of these connections is governed by its own policies. Easel is independent and is not affiliated with The Met.</p>
"""),
  ("apple", "Apple services", """
<ul>
  <li><strong>Tips</strong> are in-app purchases processed entirely by Apple. We never see your name, payment details or Apple ID; Apple only tells Easel that a purchase completed.</li>
  <li><strong>Rating prompts</strong> use Apple’s standard review request; Apple decides whether it appears, and any rating you leave goes to the App Store.</li>
  <li><strong>Notifications</strong> are scheduled locally on your device. Easel doesn’t use a push server.</li>
  <li><strong>Widgets, Live Activities, Siri, Shortcuts and Control Center</strong> run on your device through Apple’s frameworks. Siri requests are handled by Apple under Apple’s privacy policy.</li>
  <li><strong>App Store</strong> downloads and Apple’s own analytics (if you’ve chosen to share them with developers) are governed by Apple’s privacy policy. Apple may share aggregated, anonymous App Store statistics with us.</li>
</ul>
"""),
  ("permissions", "Permissions Easel asks for", """
<p>Every permission is optional, and Easel works without any of them.</p>
<div class="table-wrap"><table class="data">
  <tr><th scope="col">Permission</th><th scope="col">Why</th><th scope="col">Where to change it</th></tr>
  <tr><td>Notifications</td><td>Daily reminder (if you turn it on), Year in Review notes (15 Dec, 30 Dec, 2 Jan), Saturday note</td><td>Easel Settings, or iPhone Settings → Apps → Easel → Notifications</td></tr>
  <tr><td>Photos (add only)</td><td>Saving a share card to your library. Easel can add images, but can’t see or read your photos.</td><td>iPhone Settings → Apps → Easel → Photos</td></tr>
  <tr><td>Live Activities</td><td>The session countdown on your Lock Screen and in the Dynamic Island</td><td>iPhone Settings → Apps → Easel → Live Activities</td></tr>
</table></div>
<p>Easel never asks for your location, camera, microphone, contacts, calendars, health data or permission to track you.</p>
"""),
  ("sharing", "When you share", """
<p>When you share a card, Easel hands an image (and, where the destination accepts it, a short line with an App Store link) to Apple’s share sheet. Where it goes next is your choice, and the app or service you choose (for example Instagram or Messages) handles it under its own policy. Cards show the painting, how long you focused and, for a single painting, your intention if you set one, so check the preview before you share.</p>
"""),
  ("no-tracking", "No tracking, no ads, no selling", """
<p>Easel shows no advertising, contains no advertising SDKs, and does not track you across apps or websites owned by other companies. That’s why it never shows Apple’s App Tracking Transparency prompt. We do not sell or share personal information, and we don’t use data brokers.</p>
<p>On the App Store, Easel’s privacy label lists <strong>Usage Data</strong> (product interaction) and <strong>Diagnostics</strong> (crash data) as collected and <strong>not linked to you</strong>, and <strong>no tracking</strong>.</p>
"""),
  ("basis", "Why we may use data (legal bases)", """
<p>Where laws such as the EU and UK General Data Protection Regulation apply:</p>
<ul>
  <li><strong>Usage statistics and crash reports</strong>: our legitimate interest in keeping Easel reliable and improving it, with anonymous data and no profiling.</li>
  <li><strong>Notifications and saving to Photos</strong>: your consent, given through iOS permissions, which you can withdraw at any time.</li>
  <li><strong>Tips</strong>: to provide the purchase you asked for, processed by Apple.</li>
</ul>
"""),
  ("retention", "How long data is kept", """
<ul>
  <li><strong>On your device</strong>: until you delete Easel. Cached painting images are trimmed automatically.</li>
  <li><strong>Usage statistics and crash reports</strong>: kept only as long as they’re useful for understanding and fixing Easel, and within PostHog’s retention limits, after which they are deleted.</li>
  <li><strong>Emails you send us</strong>: as long as needed to answer you.</li>
</ul>
"""),
  ("rights", "Your rights and choices", f"""
<p>Depending on where you live, you may have the right to access, correct, delete or receive a copy of your personal data, to object to or restrict its use, and to complain to your local data protection authority.</p>
<ul>
  <li><strong>On-device data</strong>: everything is visible to you in the app, and deleting Easel removes it.</li>
  <li><strong>Usage statistics</strong>: these are anonymous, so we usually can’t link them to you. If you’d like us to try to find and delete them, or to object to them, write to <a href="mailto:{EMAIL}">{EMAIL}</a>. Reinstalling Easel starts a new random identifier.</li>
  <li><strong>Notifications, Photos and Live Activities</strong> can be turned off at any time in Settings.</li>
</ul>
<p>California residents: we don’t sell or share personal information as defined by the CCPA/CPRA, and we don’t use sensitive personal information.</p>
"""),
  ("transfers", "Where data is processed", """
<p>Usage statistics and crash reports are sent to PostHog’s EU cloud and stored in the European Union. PostHog, Inc. is based in the United States; any access from outside the EU is covered by PostHog’s data processing agreement and the European Commission’s Standard Contractual Clauses.</p>
"""),
  ("children", "Children", """
<p>Easel is made for a general audience and is not directed at children under 13 (or the equivalent minimum age where you live). The paintings are curated to be suitable for everyone, and Easel collects no personal information from anyone, including children: no names, contacts or accounts. If you believe a child has sent us personal information, for example by email, contact us and we’ll delete it.</p>
"""),
  ("security", "Security", """
<p>Your Easel data is protected by your device’s own security, including its passcode and data protection. Everything Easel sends over the internet, to PostHog or The Met, is encrypted with HTTPS.</p>
"""),
  ("website", "This website", """
<p>This website uses no cookies, no analytics and no tracking scripts. It’s hosted on GitHub Pages; like any web host, GitHub processes your IP address and basic request information to deliver the pages and keep them secure, under GitHub’s privacy statement. Links to other sites (the App Store, our feedback board on Canny, markockiadam.com, The Met) are governed by their own policies.</p>
"""),
  ("changes", "Changes to this policy", f"""
<p>When Easel’s practices change, we update this page and the date below before the change ships. Significant changes will also be noted here.</p>
<p><strong>What changed on {UPDATED}</strong>: this version replaces the policy of 22 July 2026. It adds anonymous usage statistics and crash reports (PostHog, EU cloud); intentions and the focus question; notifications (daily reminder, Year in Review, Saturday note); saving cards to Photos; Live Activities, widgets, Siri, Shortcuts and Control Center; Year in Review, milestones and rating prompts; patronage tips; the night appearance; and this website.</p>
"""),
  ("contact", "Contact", f"""
<p>Questions or requests about privacy: <a href="mailto:{EMAIL}">{EMAIL}</a>. We’ll reply as soon as we can, and within one month.</p>
"""),
]


def build_privacy():
    def body(p):
        toc = "".join(f'<li><a href="#{sid}"><span class="n">{ROMAN[i]}</span>{e(t)}</a></li>' for i, (sid, t, _) in enumerate(PRIVACY))
        sections = "".join(f'<h2 id="{sid}"><span class="numeral">{ROMAN[i]}</span>&ensp;{e(t)}</h2>{b}' for i, (sid, t, b) in enumerate(PRIVACY))
        summary = """<div class="summary-grid">
          <div class="placard"><h3>No account, no ads</h3><p>No sign-up, no advertising and no tracking across apps or websites.</p></div>
          <div class="placard"><h3>Your gallery stays with you</h3><p>Sessions, paintings and intentions are stored only on your device.</p></div>
          <div class="placard"><h3>Anonymous statistics</h3><p>Usage events and crash reports go to PostHog’s EU cloud, never linked to you.</p></div>
          <div class="placard"><h3>Paintings from The Met</h3><p>Artworks are downloaded from The Met’s public API. Requests contain nothing about you.</p></div>
        </div>"""
        return f"""    <div class="wrap">
      <header class="page-head">
        {crumbs(p, [("privacy/", "Privacy policy")])}
        <p class="label">Privacy, simply stated</p>
        <h1>Privacy policy</h1>
        <p class="lede">Easel is meant to be a quiet place. Here is everything that happens to your data, in plain language.</p>
        <p class="updated">Last updated {UPDATED} · Applies to Easel 1.1 and later, and this website.</p>
      </header>
      {summary}
      <div class="doc">
        <aside class="toc"><details open><summary>Contents</summary><nav aria-label="Contents"><p class="label">Contents</p><ol>{toc}</ol></nav></details></aside>
        <article class="prose">{sections}</article>
      </div>
    </div>"""
    return page("privacy/", "Privacy policy · Easel: Focus Timer & Art",
                "Easel’s privacy policy: your focus history stays on your device; anonymous usage statistics and crash reports (PostHog EU); paintings from The Met; no ads, no tracking, no selling.",
                body, current="privacy", jsonld=[breadcrumb_ld([("privacy/", "Privacy policy")])], og_title="Easel privacy policy")


def build_sitemap(urls):
    rows = "\n".join(f"  <url><loc>{u}</loc><lastmod>{UPDATED_ISO}</lastmod></url>" for u in [BASE] + urls)
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n')


if __name__ == "__main__":
    urls = build_guides()
    urls.append(build_faq())
    urls.append(build_privacy())
    build_sitemap(urls)
    print(f"built {len(urls)} pages")
