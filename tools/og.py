#!/usr/bin/env python3
"""Renders the link-preview image (Open Graph / X card) for every language.

    python3 tools/og.py            # needs Google Chrome; writes assets/img/og/<lang>.jpg

The card is plain HTML rendered at 2x by headless Chrome, then scaled to 1200×630.
Text comes from each language's home page (label, headline, og_description), so
a link shared in Polish previews in Polish.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

LANGS = [("en", "en-us"), ("pl", "pl-pl"), ("es", "es-es"), ("fr", "fr-fr"), ("zh-Hans", "zh-cn"),
         ("hi", "en-us"), ("ja", "ja-jp"), ("ko", "ko-kr"), ("pt-BR", "pt-br")]

FONTS = {
    "ja": ('"Hiragino Mincho ProN", serif', '"Hiragino Sans", sans-serif'),
    "zh-Hans": ('"Songti SC", serif', '"PingFang SC", sans-serif'),
    "ko": ('"AppleMyungjo", serif', '"Apple SD Gothic Neo", sans-serif'),
    "hi": ('"Devanagari Sangam MN", "Kohinoor Devanagari", serif', '"Kohinoor Devanagari", sans-serif'),
}
LATIN = ('"Iowan Old Style", "Palatino", Georgia, serif', '-apple-system, "Helvetica Neue", sans-serif')

TEMPLATE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>
:root {{ --wall:#F5F2EC; --ink:#2A2622; --soft:#6B645A; --line:#D9D2C6; --mat:#FBF8F1; --serif:{serif}; --sans:{sans}; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ width:1200px; height:630px; overflow:hidden; }}
body {{
  background:
    radial-gradient(ellipse 70% 90% at 78% 52%, #FFFDF8 0%, rgba(255,253,248,0) 70%),
    linear-gradient(180deg, #F7F4EE 0%, #F1EDE5 100%);
  color:var(--ink); font-family:var(--sans); position:relative;
  -webkit-font-smoothing:antialiased;
}}
/* a hairline "picture rail" across the wall */
.rail {{ position:absolute; left:0; right:0; top:46px; height:1px; background:linear-gradient(90deg, transparent, var(--line) 12%, var(--line) 88%, transparent); }}

.copy {{ position:absolute; left:76px; top:92px; width:478px; }}
.brand {{ display:flex; align-items:center; gap:16px; }}
.brand img {{ width:64px; height:64px; border-radius:15px; box-shadow:0 0 0 1px rgba(42,38,34,.12), 0 8px 18px -10px rgba(42,38,34,.45); }}
.brand b {{ font:400 40px/1 var(--serif); letter-spacing:-.01em; }}
.label {{ margin-top:38px; font:600 14px/1.3 var(--sans); letter-spacing:{track}; text-transform:uppercase; color:#7E5F2A; }}
h1 {{ margin-top:14px; font:400 {h1}px/1.08 var(--serif); letter-spacing:-.015em; }}
h1 em {{ font-style:{italic}; }}
p.sub {{ margin-top:22px; font:400 {sub}px/1.42 var(--sans); color:var(--soft); max-width:440px; }}
.cta {{ position:absolute; left:76px; bottom:58px; display:flex; align-items:center; gap:18px; }}
.cta img {{ height:52px; width:auto; }}
.cta span {{ font:500 15px/1.3 var(--sans); color:var(--soft); }}

/* three frames: the same painting at 25:00, 12:30 and 0:00 */
.gallery {{ position:absolute; right:56px; top:0; bottom:0; width:580px; display:flex; align-items:flex-end; justify-content:flex-end; gap:18px; padding-bottom:96px; }}
.piece {{ display:flex; flex-direction:column; align-items:center; }}
.frame {{
  padding:9px; border-radius:2px;
  background:linear-gradient(135deg,#EDD9A0 0%,#C9A35A 24%,#7E5F2A 50%,#C9A35A 72%,#E6CD8E 100%);
  box-shadow:0 1px 0 rgba(255,255,255,.4) inset, 0 0 0 1px rgba(42,38,34,.18), 0 22px 40px -18px rgba(42,38,34,.55), 0 40px 70px -40px rgba(42,38,34,.4);
  position:relative;
}}
.frame::after {{ content:""; position:absolute; inset:9px; box-shadow:0 0 0 1px rgba(0,0,0,.25), 0 0 0 3px rgba(255,255,255,.18); }}
.mat {{ background:#FBF8F1; padding:var(--matp); }}
.art {{ position:relative; overflow:hidden; background:#FBF8F1; }}
.art img {{ display:block; width:100%; height:100%; object-fit:cover;
  -webkit-mask:url(../assets/img/fog-mask.png) center / var(--m) var(--m) no-repeat; mask:url(../assets/img/fog-mask.png) center / var(--m) var(--m) no-repeat; }}
.art .mist {{ position:absolute; inset:-20%; background:#FBF8F1; opacity:var(--mist);
  -webkit-mask:url(../assets/img/fog-cloud.png) 0 0 / 70% 70% repeat; mask:url(../assets/img/fog-cloud.png) 0 0 / 70% 70% repeat; }}
.done .art img {{ -webkit-mask:none; mask:none; }}
.time {{ margin-top:16px; font:300 22px/1 var(--sans); font-variant-numeric:tabular-nums; color:var(--soft); letter-spacing:.02em; }}
.done .time {{ color:var(--ink); font-weight:500; }}
.dot {{ display:inline-block; width:6px; height:6px; margin:0 8px 3px 0; transform:rotate(45deg); background:#C9A35A; }}

.p1 .art {{ width:100px; height:124px; }} .p1 {{ --matp:9px; --m:140px; --mist:.55; }}
.p2 .art {{ width:128px; height:159px; }} .p2 {{ --matp:11px; --m:330px; --mist:.4; }}
.p3 .art {{ width:176px; height:219px; }} .p3 {{ --matp:15px; }}
</style></head><body>
<div class="rail"></div>
<div class="copy">
  <div class="brand"><img src="../assets/img/icon.jpg" alt=""><b>Easel</b></div>
  <div class="label">{label}</div>
  <h1>{h1text}</h1>
  <p class="sub">{subtext}</p>
</div>
<div class="cta"><img src="../assets/img/badges/{badge}-black.svg" alt=""><span>easelfocus.app</span></div>
<div class="gallery">
  <div class="piece p1"><div class="frame"><div class="mat"><div class="art"><img src="../assets/img/van-gogh.jpg" alt=""><div class="mist"></div></div></div></div><div class="time">25:00</div></div>
  <div class="piece p2"><div class="frame"><div class="mat"><div class="art"><img src="../assets/img/van-gogh.jpg" alt=""><div class="mist"></div></div></div></div><div class="time">12:30</div></div>
  <div class="piece p3 done"><div class="frame"><div class="mat"><div class="art"><img src="../assets/img/van-gogh.jpg" alt=""></div></div></div><div class="time"><span class="dot"></span>0:00</div></div>
</div>
<script>
// Shrink the headline (then the subtitle) until the copy clears the App Store badge.
(function () {{
  var copy = document.querySelector('.copy'), cta = document.querySelector('.cta');
  var h = document.querySelector('h1'), sub = document.querySelector('p.sub');
  var hs = parseFloat(getComputedStyle(h).fontSize), ss = parseFloat(getComputedStyle(sub).fontSize);
  function fits() {{ return copy.getBoundingClientRect().bottom <= cta.getBoundingClientRect().top - 30; }}
  while (!fits() && hs > 40) {{ hs -= 2; h.style.fontSize = hs + 'px'; }}
  while (!fits() && ss > 16) {{ ss -= 1; sub.style.fontSize = ss + 'px'; }}
}})();
</script>
</body></html>"""


def parts(code):
    home = json.load(open(os.path.join(ROOT, "content", code, "home.json")))
    body = home["body"]
    label = re.search(r'<p class="label">(.*?)</p>', body).group(1)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body).group(1)
    sub = home["og_description"]
    return label, h1, sub


def render(code, badge, tmpdir):
    label, h1, sub = parts(code)
    serif, sans = FONTS.get(code, LATIN)
    cjk = code in ("ja", "zh-Hans", "ko")
    long_h1 = len(re.sub(r"<[^>]+>", "", h1)) > 34
    html = TEMPLATE.format(
        lang=code, serif=serif, sans=sans, label=label, h1text=h1, subtext=sub, badge=badge,
        h1=(50 if cjk else (52 if long_h1 else 60)), sub=(20 if len(sub) > 120 else 21),
        italic=("normal" if cjk or code == "hi" else "italic"), track=(".06em" if cjk or code == "hi" else ".16em"))
    page = os.path.join(ROOT, "_og", f"{code}.html")
    open(page, "w").write(html)
    png = os.path.join(tmpdir, f"{code}.png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmpdir}/prof",
                    "--window-size=1200,630", "--force-device-scale-factor=2", "--virtual-time-budget=3000",
                    f"--screenshot={png}", f"http://127.0.0.1:8642/_og/{code}.html"],
                   check=True, capture_output=True)
    out = os.path.join(ROOT, "assets/img/og", f"{code}.jpg")
    subprocess.run(["magick", png, "-resize", "1200x630!", "-strip", "-quality", "88", "-sampling-factor", "4:4:4", out], check=True)
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "_og"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets/img/og"), exist_ok=True)
    tmp = tempfile.mkdtemp()
    only = set(sys.argv[1:])
    try:
        for code, badge in LANGS:
            if only and code not in only:
                continue
            print(render(code, badge, tmp))
    finally:
        shutil.rmtree(os.path.join(ROOT, "_og"), ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)
