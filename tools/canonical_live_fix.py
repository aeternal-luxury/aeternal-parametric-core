#!/usr/bin/env python3
"""Replace URLs that the live site does not serve as written with the URL it really serves (tools/live_url_map.json,
recorded from a Claims Hygiene run with http_check on 2026-11-15). Idempotent.

  python3 tools/canonical_live_fix.py          # dry run
  python3 tools/canonical_live_fix.py --apply
Replaces each absolute URL (raw and percent-encoded form) in tracked text files, including sitemap.xml, so that
canonical tags, sitemap entries, JSON-LD urls and in-text links all name the final URL. Run
`python3 tools/canonical_check.py --sync` afterwards to refresh md front matter.
"""
import json, subprocess, sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
EXTS = (".html", ".md", ".json", ".xml", ".txt", ".yaml", ".yml")

def main():
    apply = "--apply" in sys.argv
    m = json.loads((ROOT / "tools" / "live_url_map.json").read_text(encoding="utf-8"))["map"]
    pairs = []
    for a, b in m.items():
        pairs += [(a, b), (quote(a, safe=":/%"), quote(b, safe=":/%"))]
    pairs = sorted(set(pairs), key=lambda p: -len(p[0]))
    n = hits = 0
    for f in subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0"):
        if not f.endswith(EXTS) or f.startswith(("tools/", "pgef-validation/VS001-conformal-mapping/artifacts/")): continue
        p = ROOT / f
        try: s = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        t = s
        for a, b in pairs:
            if a in t and b not in a:   # b is never a substring-extension of a; guards double replacement
                hits += t.count(a); t = t.replace(a, b)
        if t != s:
            n += 1
            if apply: p.write_text(t, encoding="utf-8")
    print(f"{n} file(s), {hits} URL occurrence(s) {'rewritten' if apply else 'would be rewritten'}")

if __name__ == "__main__":
    main()
