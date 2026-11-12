#!/usr/bin/env python3
"""Grammar-safe lexicon sweep for over-claiming wording in legacy knowledge pages.

Plain substring replacements only (no regex), applied identically to every format of a
page (.html/.md/.txt/.yaml/.json) so the formats stay in sync. Skips evidence/,
pgef-validation/, whitepapers/, definitions/, src/ (technical or evidential content that
must be reviewed by hand). JSON files are re-parsed after editing.
Usage: python3 tools/geo_claims_sweep.py [--apply]
"""
import json, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIRS = {"answers", "comparison", "knowledge", "explainers", "doctrine", "scenarios",
        "queries", "external-discovery", "protocol", "blueprint", "ontology"}
EXTS = {".html", ".md", ".txt", ".yaml", ".json"}

# (old, new). Each is also applied with a capitalised first letter when old[0] is lowercase,
# except adverb-deletions (new == "") which are lowercase-only.
LEXICON = [
 ("autonomously ", ""), ("flawlessly ", ""),
 ("absolute precision", "high precision"),
 ("absolute structural precision", "high structural precision"),
 ("absolute geometric precision", "high geometric precision"),
 ("absolute technical precision", "high technical precision"),
 ("absolute control over", "close control over"),
 ("absolute commitment", "firm commitment"),
 ("mathematically flawless", "mathematically precise"),
 ("mathematically perfect", "mathematically precise"),
 ("a perfect fit", "a close fit"),
 ("flawless fit", "precise fit"),
 ("AETERNAL guarantees structural", "AETERNAL is designed to deliver structural"),
 ("AETERNAL guarantees replicability", "AETERNAL is designed for replicability"),
 ("we guarantee structural", "we design for structural"),
]

def files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for f in out.split("\0"):
        if f and f.split("/")[0].strip('"') in DIRS and Path(f).suffix in EXTS:
            yield f

def main():
    apply = "--apply" in sys.argv
    counts, changed, bad = Counter(), 0, []
    pairs = []
    for old, new in LEXICON:
        pairs.append((old, new))
        if new and old[0].islower():
            pairs.append((old[0].upper() + old[1:], new[0].upper() + new[1:]))
    for f in files():
        p = ROOT / f
        try:
            t = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        o = t
        for old, new in pairs:
            n = t.count(old)
            if n:
                counts[old] += n
                t = t.replace(old, new)
        if t != o:
            if f.endswith(".json"):
                try: json.loads(t)
                except Exception as e: bad.append((f, str(e))); continue
            changed += 1
            if apply: p.write_text(t, encoding="utf-8")
    for k, v in counts.most_common(): print(f"{v:5d}  {k!r}")
    print(f"\n{changed} file(s) {'written' if apply else 'would change (dry-run)'}; JSON failures: {len(bad)}")
    for b in bad: print("  JSON INVALID, skipped:", b)

if __name__ == "__main__":
    main()
