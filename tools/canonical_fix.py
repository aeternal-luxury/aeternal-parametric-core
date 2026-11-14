#!/usr/bin/env python3
"""Add or correct <link rel="canonical"> so every page points at its own live URL listed in sitemap.xml.

  python3 tools/canonical_fix.py          # dry run: prints the plan and what stays unresolved
  python3 tools/canonical_fix.py --apply  # edit html, then run `canonical_check.py --sync` for the md files

Decision order per html file (repo path P, host root BASE):
  1. current canonical is already a sitemap URL                  -> keep
  2. BASE/P is a sitemap URL                                      -> canonical = BASE/P (add or correct)
  3. comparison/NN_*_ZH_ZH.html with a unique sitemap .../NN_*_ZH.html -> that sitemap URL (match by NN prefix)
  4. current canonical is a normal same-host page URL (.html or /)  -> keep, reported as 'not in sitemap'
  5. no canonical at all                                          -> canonical = BASE/P, reported as 'unverified'
  6. anything else (e.g. directory-style redirect URL)            -> left alone, reported
Idempotent. Root host: https://knowledge.aeternal-luxury.com/ (the host used by every existing canonical and the sitemap).
"""
import re, sys
from pathlib import Path
from urllib.parse import quote, unquote
sys.path.insert(0, str(Path(__file__).resolve().parent))
import canonical_check as cc

BASE = "https://knowledge.aeternal-luxury.com/"
ROOT = cc.ROOT
TAG = re.compile(r"<link\b[^>]*>", re.I)

def sitemap():
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    return {unquote(x): x for x in locs}

def set_canonical(text, url):
    for m in TAG.finditer(text):
        tag = m.group(0)
        if re.search(r'\brel\s*=\s*["\'][^"\']*\bcanonical\b', tag, re.I):
            new = re.sub(r'(\bhref\s*=\s*)(["\'])[^"\']*\2', lambda x: f'{x.group(1)}"{url}"', tag, count=1, flags=re.I)
            return text[:m.start()] + new + text[m.end():]
    m = re.search(r"</head>", text, re.I)
    if not m: return None
    ind = re.search(r"\n([ \t]*)<[^\n]*\n[ \t]*</head>", text, re.I)
    pad = ind.group(1) if ind else "    "
    return text[:m.start()].rstrip(" \t") + f'{pad}<link rel="canonical" href="{url}">\n' + text[m.start():] if text[:m.start()].endswith("\n") or True else text

def main():
    apply = "--apply" in sys.argv
    sm = sitemap()
    zh = {}
    for u in sm:
        m = re.search(r"/comparison/(\d\d)_[^/]*_ZH\.html$", u)
        if m: zh.setdefault(m.group(1), []).append(u)
    plan, report = [], {"not in sitemap (kept)": [], "unverified (added)": [], "unresolved": []}
    for f in cc.tracked(".html"):
        p = str(f); cur = cc.html_canonicals(ROOT / f); cur = cur[0] if cur else None
        self_url = BASE + p
        if cur and unquote(cur) in sm: continue
        target = None
        if self_url in sm: target = sm[self_url] if False else self_url
        else:
            m = re.match(r"comparison/(\d\d)_.*_ZH_ZH\.html$", p)
            if m and len(zh.get(m.group(1), [])) == 1: target = zh[m.group(1)][0]
        if target is None:
            if cur and re.match(re.escape(BASE) + r"[^ ]*(\.html|/)$", cur) and " " not in cur and not re.search(r"_(EN|ZH)/$", cur):
                report["not in sitemap (kept)"].append(p); continue
            if cur is None: target = self_url; report["unverified (added)"].append(p)
            else: report["unresolved"].append((p, cur)); continue
        if cur != target: plan.append((f, cur, target))
    for f, cur, tgt in plan:
        if apply:
            t = (ROOT / f).read_text(encoding="utf-8"); n = set_canonical(t, tgt)
            if n is None: report["unresolved"].append((str(f), "no </head>")); continue
            (ROOT / f).write_text(n, encoding="utf-8")
    kinds = {"added": sum(1 for _, c, _ in plan if c is None), "corrected": sum(1 for _, c, _ in plan if c is not None)}
    print(f"{'applied' if apply else 'plan'}: {kinds}")
    for k, v in report.items(): print(f"{k}: {len(v)}", [x if isinstance(x, str) else x for x in v[:3]])

if __name__ == "__main__":
    main()
