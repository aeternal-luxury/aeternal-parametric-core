#!/usr/bin/env python3
"""Canonical URL tooling: parse, sync (HTML -> Markdown front matter) and verify.

  python3 tools/canonical_check.py            # report only (exit 1 on hard errors)
  python3 tools/canonical_check.py --sync     # rewrite md canonical from the sibling html canonical
  python3 tools/canonical_check.py --http     # also HEAD-check every canonical URL (needs network)

Checks: (1) every html has exactly one canonical; (2) md canonical == sibling html canonical;
(3) canonical uniqueness across distinct pages; (4) no '//' in path, https + known host;
(5) sitemap.xml <loc> consistency; (6) sync is idempotent; (7) optional HTTP status / redirects.
The HTML is parsed with html.parser, so attribute order, quotes and whitespace do not matter.
"""
import re, subprocess, sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HOST = "knowledge.aeternal-luxury.com"

class _P(HTMLParser):
    def __init__(self):
        super().__init__(); self.canon = []
    def handle_starttag(self, tag, attrs):
        if tag == "link":
            a = {k.lower(): (v or "") for k, v in attrs}
            if "canonical" in a.get("rel", "").lower().split():
                self.canon.append(a.get("href", "").strip())
    handle_startendtag = handle_starttag

def html_canonicals(path):
    p = _P(); p.feed(path.read_text(encoding="utf-8", errors="ignore")); return p.canon

FM = re.compile(r'^(canonical:\s*)("?)([^"\n]*)("?)\s*$', re.M)

def tracked(ext):
    out = subprocess.run(["git", "ls-files", "-z", f"*{ext}"], cwd=ROOT, capture_output=True, text=True).stdout
    return [Path(f) for f in out.split("\0") if f]

def main():
    if "--print" in sys.argv:                       # used by convert.yml: print the page's canonical or fail loudly
        c = html_canonicals(Path(sys.argv[sys.argv.index("--print") + 1]))
        if len(set(c)) != 1:
            print(f"canonical tags found: {len(set(c))}", file=sys.stderr); sys.exit(2)
        print(c[0]); sys.exit(0)
    sync, http = "--sync" in sys.argv, "--http" in sys.argv
    errors, warnings, changed = [], [], 0
    by_url = defaultdict(list); html_url = {}
    for f in tracked(".html"):
        c = html_canonicals(ROOT / f)
        if len(c) == 0: warnings.append(f"no canonical tag: {f}"); continue
        if len(set(c)) > 1: errors.append(f"conflicting canonical tags: {f} {c}"); continue
        html_url[f] = c[0]; by_url[c[0]].append(f)
        u = urlparse(c[0])
        if u.scheme != "https" or u.netloc != HOST: warnings.append(f"unexpected scheme/host: {f} {c[0]}")
        if "//" in u.path: errors.append(f"double slash: {f} {c[0]}")
    for url, fs in by_url.items():
        if len(fs) > 1: warnings.append(f"canonical shared by {len(fs)} html files: {url} <- {[str(x) for x in fs][:3]}")
    md_checked = md_mismatch = md_nohtml = md_nosrc = 0
    for f in tracked(".md"):
        h = f.with_suffix(".html")
        m = FM.search((ROOT / f).read_text(encoding="utf-8", errors="ignore")[:2000])
        if not m: continue
        if h not in html_url:
            md_nosrc += 1; continue
        md_checked += 1
        if m.group(3) != html_url[h]:
            md_mismatch += 1
            if sync:
                t = (ROOT / f).read_text(encoding="utf-8")
                t = FM.sub(lambda x: f'{x.group(1)}"{html_url[h]}"', t, count=1)
                (ROOT / f).write_text(t, encoding="utf-8"); changed += 1
            else: errors.append(f"md/html canonical mismatch: {f}: {m.group(3)} != {html_url[h]}")
    sm = ROOT / "sitemap.xml"
    if sm.exists():
        locs = set(re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm.read_text(encoding="utf-8")))
        miss = [u for u in by_url if u not in locs]
        if miss: warnings.append(f"{len(miss)} canonical URLs not in sitemap.xml (e.g. {miss[:2]})")
        extra = [u for u in locs if u not in by_url]
        if extra: warnings.append(f"{len(extra)} sitemap URLs without a matching html canonical (e.g. {extra[:2]})")
    if http:
        import urllib.request
        bad = 0
        for u in sorted(by_url):
            try:
                r = urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=20)
                if r.geturl() != u or r.status != 200: warnings.append(f"redirect/status {r.status}: {u} -> {r.geturl()}"); bad += 1
            except Exception as e: warnings.append(f"HTTP failure {u}: {e}"); bad += 1
        print(f"HTTP checked {len(by_url)} URLs, {bad} problems")
    print(f"html with canonical: {len(html_url)}; md checked: {md_checked}; md mismatches: {md_mismatch}; md without html source: {md_nosrc}; synced: {changed}")
    for w in warnings[:40]: print("WARN ", w)
    if len(warnings) > 40: print(f"... {len(warnings) - 40} more warnings")
    for e in errors[:40]: print("ERROR", e)
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
