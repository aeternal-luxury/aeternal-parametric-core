#!/usr/bin/env python3
"""Apply the licence/trademark wording rules (tools/geo_license_rules.py) to the repo. Idempotent.

  python3 tools/geo_license_apply.py          # dry run
  python3 tools/geo_license_apply.py --apply
Decision 2026-11-14: code MIT, documentation CC BY 4.0, trademarks unregistered (no (R)), proprietary engine not published.
"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import geo_license_rules as L

ROOT = Path(__file__).resolve().parent.parent
EXTS = (".html", ".md", ".txt", ".yaml", ".yml", ".json")
SKIP = ("LICENSE", "LICENSE-DOCS.md", "NOTICE.md", "TRADEMARKS.md", "tools/", "pgef-validation/VS001-conformal-mapping/artifacts/")

def convert(t):
    for old, new in L.PLAIN: t = t.replace(old, new)
    for _n, rx, rep in L.RX: t = rx.sub(rep, t)
    return t

def main():
    apply = "--apply" in sys.argv
    changed = 0
    for f in subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0"):
        if not f.endswith(EXTS) or f.startswith(SKIP) or f in SKIP: continue
        p = ROOT / f
        try: s = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        n = convert(s)
        if n != s:
            changed += 1
            if apply: p.write_text(n, encoding="utf-8")
    print(f"{changed} file(s) {'written' if apply else 'would change'}")

if __name__ == "__main__":
    main()
