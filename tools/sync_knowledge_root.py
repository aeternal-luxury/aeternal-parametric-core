#!/usr/bin/env python3
"""Keep knowledge/robots.txt and knowledge/sitemap.xml identical to the repo-root copies (single source of truth),
and check that every knowledge/_redirects rule is sound. Idempotent.

  python3 tools/sync_knowledge_root.py          # report
  python3 tools/sync_knowledge_root.py --apply  # copy root -> knowledge/
Checks on _redirects: each destination exists under knowledge/, no destination is itself a redirect source,
and no redirected source URL is listed in sitemap.xml.
"""
import re, shutil, sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
K = ROOT / "knowledge"

def rules():
    out = []
    for line in (K / "_redirects").read_text(encoding="utf-8").splitlines():
        p = line.split()
        if p and not line.lstrip().startswith("#") and len(p) >= 2: out.append((p[0], p[1]))
    return out

def main():
    apply, bad = "--apply" in sys.argv, 0
    for name in ("robots.txt", "sitemap.xml"):
        a, b = ROOT / name, K / name
        same = b.exists() and a.read_bytes() == b.read_bytes()
        print(f"{name}: {'in sync' if same else 'DIFFERS from knowledge/' + name}")
        if not same:
            if apply: shutil.copyfile(a, b); print("  copied root -> knowledge/")
            else: bad += 1
    r = rules(); srcs = {s for s, _ in r}
    sm = {unquote(x) for x in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))}
    for s, d in r:
        if not (K / d.lstrip("/")).exists(): print("  _redirects destination missing:", d); bad += 1
        if d in srcs: print("  _redirects chain:", s, "->", d); bad += 1
        if "https://knowledge.aeternal-luxury.com" + s in sm: print("  redirected URL listed in sitemap:", s); bad += 1
    print(f"_redirects: {len(r)} rules checked")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
