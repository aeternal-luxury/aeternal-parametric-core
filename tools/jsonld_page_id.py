#!/usr/bin/env python3
"""Point JSON-LD mainEntityOfPage @id at the page's own canonical URL (comparison/ pages carried
https://aeternal.com/... or https://aeternal.luxury/... ids that belong to no live site). Idempotent.

  python3 tools/jsonld_page_id.py [--apply]
Edits NN_*.html and its generated siblings (_schema_ld.json, _knowledge_graph.md, ...) that share the file stem.
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import canonical_check as cc

ROOT = cc.ROOT
RX = re.compile(r'("@id"\s*:\s*")https://aeternal\.(?:com|luxury)/[^"]*(")')

def main():
    apply = "--apply" in sys.argv
    n = 0
    files = [str(f) for f in cc.tracked("") ] if False else None
    import subprocess
    allf = [f for f in subprocess.check_output(["git", "ls-files", "-z", "comparison"], cwd=ROOT).decode().split("\0") if f]
    for h in (f for f in allf if f.endswith(".html")):
        c = cc.html_canonicals(ROOT / h)
        if not c: continue
        stem = h[:-5]
        for f in allf:
            if f == h or (f.startswith(stem + "_") or f == stem + ".md"):
                s = (ROOT / f).read_text(encoding="utf-8")
                new = RX.sub(lambda m: m.group(1) + c[0] + m.group(2), s)
                if new != s:
                    n += 1
                    if apply: (ROOT / f).write_text(new, encoding="utf-8")
    print(("updated" if apply else "would update"), n, "files")

if __name__ == "__main__":
    main()
