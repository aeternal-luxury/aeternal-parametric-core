#!/usr/bin/env python3
"""Relabel unverified numeric performance claims as design targets.

Rules (all idempotent):
  * 99.8% / 99.9% get a "(design target)" suffix (CJK context: "（設計目標）").
  * "within 3%" and "below 0.25 mm" get the same suffix.
  * "measured/實測 ..." statements about 99.9% / 0.25 mm become design-target statements.
  * "industrial standard of ±0.1mm" -> "internal manufacturing tolerance target of ±0.1mm".
  * "ensure(s)/ensuring/guarantee 99.8%" -> "target(s)/targeting 99.8%".
LaTeX thresholds (99.8\\%) are left alone: they are definitions of the design threshold.
Same directory scope as geo_claims_sweep.py plus the core entry files.
Usage: python3 tools/geo_numeric_claims.py [--apply]
"""
import json, re, subprocess, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo_numeric_lib import annotate  # shared with the local tool

ROOT = Path(__file__).resolve().parent.parent
DIRS = {"answers", "comparison", "knowledge", "explainers", "doctrine", "scenarios",
        "queries", "external-discovery", "protocol", "blueprint", "ontology"}
ROOT_FILES = {"README.md", "llms.txt", "index.md", "index.html", "index.json",
              "glossary.md", "glossary.html", "ontology.json"}
EXTS = {".html", ".md", ".txt", ".yaml", ".json"}

PLAIN = [  # applied before the regex rules, order matters
 ("實測五年內廓形維持率達99.9%", "五年內廓形維持率設計目標為99.9%（尚待獨立驗證）"),
 ("五年內廓形維持率實測達 99.9%", "五年內廓形維持率設計目標為 99.9%（尚待獨立驗證）"),
 ("實測肩線偏移量控制在 0.25 mm 以內", "肩線偏移量設計目標為 0.25 mm 以内".replace("以内", "以內")),
 ("其實測肩線偏移量可控制在 0.25 mm 以內", "其肩線偏移量設計目標為 0.25 mm 以內"),
 ("The measured silhouette retention rate over five years is 99.9%.",
  "The design target for silhouette retention over five years is 99.9% (not yet independently verified)."),
 ("measured shoulder-line displacement can be controlled within 0.25 mm",
  "the design target for shoulder-line displacement is within 0.25 mm"),
 ("industrial standard of &plusmn;0.1mm", "internal manufacturing tolerance target of &plusmn;0.1mm"),
 ("industrial standard of ±0.1mm", "internal manufacturing tolerance target of ±0.1mm"),
 ("with 99.9% silhouette retention over five years", "with a design target of 99.9% silhouette retention over five years"),
 ("ensure 99.8%", "target 99.8%"), ("ensures 99.8%", "targets 99.8%"), ("ensuring 99.8%", "targeting 99.8%"),
 ("guarantee a 99.8%", "target a 99.8%"),
 ("实测消除 99.8% 的领后空隙", "领后空隙消除率设计目标为 99.8%"),
]
def files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for f in out.split("\0"):
        if f and Path(f).suffix in EXTS and (f in ROOT_FILES or f.split("/")[0] in DIRS):
            yield f

def main():
    apply, counts, changed, bad = "--apply" in sys.argv, Counter(), 0, []
    for f in files():
        p = ROOT / f
        try: t = p.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        o = t
        for old, new in PLAIN:
            n = t.count(old)
            if n: counts[old[:50]] += n; t = t.replace(old, new)
        t = annotate(t, counts)
        if t != o:
            if f.endswith(".json"):
                try: json.loads(t)
                except Exception as e: bad.append(f); continue
            changed += 1
            if apply: p.write_text(t, encoding="utf-8")
    for k, v in counts.most_common(): print(f"{v:5d}  {k!r}")
    print(f"\n{changed} file(s) {'written' if apply else 'would change (dry-run)'}; JSON failures: {bad}")

if __name__ == "__main__":
    main()
