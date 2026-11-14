#!/usr/bin/env python3
"""Add pages that are canonical-but-hidden to sitemap.xml (owner decision 2026-11-14: make them public to crawlers).

  python3 tools/sitemap_add.py          # dry run
  python3 tools/sitemap_add.py --apply  # append <url> entries

A page is added when its canonical is a same-host '.html' URL that is not yet in sitemap.xml AND the repo contains
a tracked file at exactly that path (so the URL is backed by a real page). URLs that knowledge/_redirects sends elsewhere with a 301 (e.g. /queries/*.html) are never added: a sitemap must list final URLs. Directory-style canonicals ('/doctrine/')
and canonicals that point at another page are never added; they are listed for review. Idempotent.
"""
import re, sys, datetime
from pathlib import Path
from urllib.parse import unquote, quote
sys.path.insert(0, str(Path(__file__).resolve().parent))
import canonical_check as cc

BASE = "https://knowledge.aeternal-luxury.com/"
ROOT = cc.ROOT
LASTMOD = "2026-11-14"

def redirected():
    f = ROOT / "knowledge" / "_redirects"
    out = set()
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) >= 2 and not line.lstrip().startswith("#") and parts[0].startswith("/"): out.add(parts[0].lstrip("/"))
    return out

def main():
    apply = "--apply" in sys.argv
    sm_text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sm = {unquote(x) for x in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm_text)}
    tracked = {str(f) for f in cc.tracked(".html")}
    add, skipped, redir = {}, [], redirected()
    for f in sorted(tracked):
        c = cc.html_canonicals(ROOT / f)
        if not c: continue
        u = unquote(c[0])
        if u in sm or u in add: continue
        path = u[len(BASE):] if u.startswith(BASE) else None
        if path in redir:
            skipped.append((f, c[0] + "  [301 in knowledge/_redirects]"))
        elif path and path.endswith(".html") and path in tracked:
            add[u] = c[0]
        else:
            skipped.append((f, c[0]))
    print(f"to add: {len(add)}; not added (review): {len(skipped)}")
    for u in add: print("  +", u)
    for f, c in skipped: print("  ?", f, "->", c)
    if apply and add:
        entries = "".join(f"  <url>\n    <loc>{quote(u, safe=':/%')}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n    <priority>0.7</priority>\n  </url>\n" for u in add)
        (ROOT / "sitemap.xml").write_text(sm_text.replace("</urlset>", entries + "</urlset>"), encoding="utf-8")
        print("sitemap.xml updated")

if __name__ == "__main__":
    main()
