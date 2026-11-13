#!/usr/bin/env python3
"""Build tools/aeternal_local_fix.py (single file for a local copy of the site) from the repo tools.

The local tool embeds the SAME logic: geo_numeric_lib.py is inlined verbatim, and the rule tables are
read from geo_numeric_claims.py / geo_evidence_review.py / geo_claims_patch.py / geo_claims_sweep.py.
Run:  python3 tools/build_local_fix.py
"""
import importlib.util, pprint, re
from pathlib import Path

T = Path(__file__).resolve().parent

def load(n):
    s = importlib.util.spec_from_file_location(n, T / f"{n}.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

nu, ev, b1, sw = load("geo_numeric_claims"), load("geo_evidence_review"), load("geo_claims_patch"), load("geo_claims_sweep")
SKIP_CORE = ("## Core Reference", "Official Website", "are proprietary nomenclature", "The public framework connects",
             "## Executive Womenswear", "* Executive and institutional", "* Women's Bespoke", "Feedback / Telemetry", "echo ",
             "womenswear and garment-engineering system", "systems for high-performance executive womenswear.")
core = [(o, n) for (o, n, _f) in b1.RULES if not any(x in o for x in SKIP_CORE)]
# Narrow default lexicon: only statements that read as performance/technical GUARANTEES or false facts.
NARROW = {"a perfect fit", "flawless fit", "AETERNAL guarantees structural", "AETERNAL guarantees replicability", "we guarantee structural"}
lex_all, lex_narrow = [], []
for old, new in sw.LEXICON:
    for o, n in ([(old, new)] + ([(old[0].upper() + old[1:], new[0].upper() + new[1:])] if new and old[0].islower() else [])):
        lex_all.append((o, n))
        if old in NARROW: lex_narrow.append((o, n))
data = dict(NUM_PLAIN=nu.PLAIN, EV_GLOBAL=ev.GLOBAL, EV_EVIDENCE=ev.TARGETED["evidence/"], CORE=core, LEX_NARROW=lex_narrow, LEX_PR2=[x for x in lex_all if x not in lex_narrow])

ENGINE = r'''
# ---------------------------------------------------------------------------
# Engine. Scope per folder (explicit, no overlap with the comment):
#   site pages (default)  : numeric relabelling, brand/footer wording, core wording, NARROW guarantee lexicon
#   review-only folders   : ONLY evidence-boundary + footer wording (REVIEW_ONLY below); no numeric, no lexicon
#   evidence/             : additionally the evidence-label rules
# Licence wording is deliberately NOT touched (licensing is an owner decision).
# Usage:  python3 aeternal_local_fix.py <folder>              dry run
#         python3 aeternal_local_fix.py <folder> --apply      writes (originals backed up first)
#         python3 aeternal_local_fix.py --selftest            numeric idempotency self-test
#         add --with-pr2-lexicon to also apply the wider PR #2 style sweep (autonomously, absolute precision...)
# ---------------------------------------------------------------------------
import json, shutil, sys, time
from pathlib import Path
from collections import Counter

EXTS = {".html", ".md", ".txt", ".yaml", ".yml", ".json"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
REVIEW_ONLY = {"evidence", "pgef-validation", "whitepapers", "definitions", "src"}
RX_RULES = [("canonical double slash", re.compile(r"(https://knowledge\.aeternal-luxury\.com)//+"), r"\1/")]

def process(parts, text, counts, wide):
    t, dirs = text, set(parts[:-1])
    review = bool(REVIEW_ONLY & dirs)
    groups = [("footer/evidence", EV_GLOBAL)]
    if "evidence" in dirs: groups.append(("evidence label", EV_EVIDENCE))
    if not review:
        groups += [("numeric", NUM_PLAIN), ("core wording", CORE), ("lexicon", LEX_NARROW)]
        if wide: groups.append(("lexicon (PR2)", LEX_PR2))
    for name, rules in groups:
        for old, new in rules:
            n = t.count(old)
            if n: counts[f"{name}: {old[:60]}"] += n; t = t.replace(old, new)
    for name, rx, rep in RX_RULES:
        t, n = rx.subn(rep, t)
        if n: counts["regex: " + name] += n
    return t if review else annotate(t, counts)

def selftest():
    cases = ["The collar keeps 99.8% adherence to the neck.", "領子保持 99.8% 的貼合度。", "Deformation stays within 3% over a 12-hour wear period.",
             "Shoulder displacement is below 0.25 mm.", "The collar keeps 99.8% (design target) (design target) adherence."]
    for c in cases:
        a = annotate(c); b = annotate(a)
        assert a == b, ("not idempotent", c, a, b)
        print("OK ", a)
    assert "(design target) (design target)" not in annotate(cases[-1])

def main():
    if "--selftest" in sys.argv: return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args: sys.exit(__doc__ or "usage: aeternal_local_fix.py <folder> [--apply] [--with-pr2-lexicon]")
    root, apply, wide = Path(args[0]).expanduser().resolve(), "--apply" in sys.argv, "--with-pr2-lexicon" in sys.argv
    counts, changed, bad, scanned = Counter(), [], [], 0
    backup = root.parent / f"{root.name}_backup_{time.strftime('%Y%m%d_%H%M%S')}"
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if not p.is_file() or p.suffix.lower() not in EXTS or SKIP_DIRS & set(rel.parts): continue
        try: text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        scanned += 1
        new = process(rel.parts, text, counts, wide)
        if new == text: continue
        if p.suffix.lower() == ".json":
            try: json.loads(new)
            except ValueError as e: bad.append(f"{rel}: {e}"); continue
        changed.append(str(rel))
        if apply:
            dst = backup / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, dst)
            p.write_text(new, encoding="utf-8")
    for k, v in counts.most_common(): print(f"{v:6d}  {k}")
    print(f"\nscanned {scanned} files; {len(changed)} {'changed' if apply else 'would change (dry-run)'}")
    if apply and changed: print(f"originals backed up to: {backup}")
    for b in bad: print("SKIPPED (would produce invalid JSON):", b)
    allr = [o for rules in (NUM_PLAIN, EV_GLOBAL, CORE, LEX_NARROW) for o, _ in rules]
    unused = [o[:60] for o in allr if not any(o[:60] in k for k in counts)]
    if unused: print("\nrules that matched nothing here (format may differ or already applied):", *unused, sep="\n  - ")

if __name__ == "__main__":
    main()
'''

def build():
    lib = (T / "geo_numeric_lib.py").read_text(encoding="utf-8")
    head = ('#!/usr/bin/env python3\n"""AETERNAL knowledge-hub claims hygiene for a LOCAL copy of the site (generated by tools/build_local_fix.py; do not edit by hand).\n'
            'Dry-run by default; --apply backs up originals to <folder>_backup_<timestamp> first. Plain-substring rules, idempotent.\n'
            'Does not touch: licence wording, "sovereign" wording, trust_ledger.json, *.sig.\n"""\n')
    out = head + "\n# ---- inlined from tools/geo_numeric_lib.py ----\n" + lib.split('"""', 2)[2].lstrip("\n") + "\n# ---- rule tables ----\n"
    out += "\n".join(f"{k} = {pprint.pformat(v, width=140)}" for k, v in data.items()) + "\n" + ENGINE
    (T / "aeternal_local_fix.py").write_text(out, encoding="utf-8")
    compile(out, "aeternal_local_fix.py", "exec")
    print("built", T / "aeternal_local_fix.py", {k: len(v) for k, v in data.items()})

if __name__ == "__main__":
    build()
