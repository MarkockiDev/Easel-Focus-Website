#!/usr/bin/env python3
"""Checks a translation in content/<lang>/ against content/en/.

    python3 tools/check_i18n.py pl

For every string it checks: same JSON shape and keys; same {placeholders}; the same
HTML tags in the same order; identical href/src/id/class/data-* attribute values
(only text, alt, title and aria-label may change); nothing left empty. It also warns
when a longer string is still identical to the English.
Exit code 0 = passes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ("ui", "home", "guides", "faq", "privacy")
FIXED_KEYS = {"slug", "id"}                       # must stay identical
OPTIONAL_EMPTY = {"privacy_translation_note"}     # empty in English, filled in translations
TAG = re.compile(r"<(/?)([a-zA-Z0-9]+)([^>]*)>")
ATTR = re.compile(r'([a-zA-Z:-]+)="([^"]*)"')
FREE_ATTRS = {"alt", "title", "aria-label"}
PH = re.compile(r"\{[a-z_]+\}")


def tags(s):
    out = []
    for close, name, attrs in TAG.findall(s):
        kept = tuple(sorted((k, v) for k, v in ATTR.findall(attrs) if k not in FREE_ATTRS))
        out.append((close, name.lower(), kept))
    return out


def walk(en, tr, path, errors, warnings, lang):
    if isinstance(en, dict):
        if not isinstance(tr, dict):
            errors.append(f"{path}: expected an object"); return
        missing = set(en) - set(tr); extra = set(tr) - set(en)
        if missing: errors.append(f"{path}: missing keys {sorted(missing)}")
        if extra: errors.append(f"{path}: unexpected keys {sorted(extra)}")
        for k in en:
            if k in tr:
                if k in FIXED_KEYS and en[k] != tr[k]:
                    errors.append(f"{path}.{k}: must stay '{en[k]}'")
                walk(en[k], tr[k], f"{path}.{k}", errors, warnings, lang)
    elif isinstance(en, list):
        if not isinstance(tr, list) or len(tr) != len(en):
            errors.append(f"{path}: expected a list of {len(en)} items"); return
        for i, (a, b) in enumerate(zip(en, tr)):
            walk(a, b, f"{path}[{i}]", errors, warnings, lang)
    elif isinstance(en, str):
        if not isinstance(tr, str):
            errors.append(f"{path}: expected a string"); return
        key = path.rsplit(".", 1)[-1]
        if not tr.strip() and key not in OPTIONAL_EMPTY and en.strip():
            errors.append(f"{path}: empty")
        if key in OPTIONAL_EMPTY:
            if lang != "en" and not tr.strip():
                errors.append(f"{path}: should be filled in a translation")
            return
        if sorted(PH.findall(en)) != sorted(PH.findall(tr)):
            errors.append(f"{path}: placeholders differ {sorted(PH.findall(en))} vs {sorted(PH.findall(tr))}")
        te, tt = tags(en), tags(tr)
        if te != tt:
            # find first difference for a useful message
            for i, (a, b) in enumerate(zip(te, tt)):
                if a != b:
                    errors.append(f"{path}: HTML differs at tag #{i}: {a} vs {b}"); break
            else:
                errors.append(f"{path}: HTML tag count differs ({len(te)} vs {len(tt)})")
        if lang != "en" and en == tr and len(strip(en)) > 25 and key not in FIXED_KEYS:
            warnings.append(f"{path}: identical to English")


def strip(s):
    return re.sub(r"<[^>]+>", "", s)


def main(lang):
    errors, warnings = [], []
    for f in FILES:
        en = json.load(open(os.path.join(ROOT, "content/en", f + ".json")))
        p = os.path.join(ROOT, "content", lang, f + ".json")
        if not os.path.exists(p):
            errors.append(f"{f}.json: missing file"); continue
        try:
            tr = json.load(open(p))
        except Exception as ex:
            errors.append(f"{f}.json: invalid JSON: {ex}"); continue
        walk(en, tr, f, errors, warnings, lang)
    for w in warnings:
        print("warning:", w)
    for x in errors:
        print("ERROR:", x)
    print(f"{lang}: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
