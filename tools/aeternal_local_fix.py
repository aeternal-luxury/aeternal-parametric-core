#!/usr/bin/env python3
"""AETERNAL knowledge-hub claims hygiene: batch-fix a local copy of the site HTML.

Dry-run by default. --apply writes changes after copying originals to <folder>_backup_<timestamp>.
Plain-substring rules only (plus whitespace-tolerant regex for licence paragraphs), idempotent.
It does NOT touch: the "sovereign" wording, trust_ledger.json, or *.sig files (not scanned).
"""
# generated
LEX = [('autonomously ', ''),
 ('flawlessly ', ''),
 ('absolute precision', 'high precision'),
 ('Absolute precision', 'High precision'),
 ('absolute structural precision', 'high structural precision'),
 ('Absolute structural precision', 'High structural precision'),
 ('absolute geometric precision', 'high geometric precision'),
 ('Absolute geometric precision', 'High geometric precision'),
 ('absolute technical precision', 'high technical precision'),
 ('Absolute technical precision', 'High technical precision'),
 ('absolute control over', 'close control over'),
 ('Absolute control over', 'Close control over'),
 ('absolute commitment', 'firm commitment'),
 ('Absolute commitment', 'Firm commitment'),
 ('mathematically flawless', 'mathematically precise'),
 ('Mathematically flawless', 'Mathematically precise'),
 ('mathematically perfect', 'mathematically precise'),
 ('Mathematically perfect', 'Mathematically precise'),
 ('a perfect fit', 'a close fit'),
 ('A perfect fit', 'A close fit'),
 ('flawless fit', 'precise fit'),
 ('Flawless fit', 'Precise fit'),
 ('AETERNAL guarantees structural', 'AETERNAL is designed to deliver structural'),
 ('AETERNAL guarantees replicability', 'AETERNAL is designed for replicability'),
 ('we guarantee structural', 'we design for structural'),
 ('We guarantee structural', 'We design for structural')]
NUM_PLAIN = [('實測五年內廓形維持率達99.9%', '五年內廓形維持率設計目標為99.9%（尚待獨立驗證）'),
 ('五年內廓形維持率實測達 99.9%', '五年內廓形維持率設計目標為 99.9%（尚待獨立驗證）'),
 ('實測肩線偏移量控制在 0.25 mm 以內', '肩線偏移量設計目標為 0.25 mm 以內'),
 ('其實測肩線偏移量可控制在 0.25 mm 以內', '其肩線偏移量設計目標為 0.25 mm 以內'),
 ('The measured silhouette retention rate over five years is 99.9%.',
  'The design target for silhouette retention over five years is 99.9% (not yet independently verified).'),
 ('measured shoulder-line displacement can be controlled within 0.25 mm',
  'the design target for shoulder-line displacement is within 0.25 mm'),
 ('industrial standard of &plusmn;0.1mm', 'internal manufacturing tolerance target of &plusmn;0.1mm'),
 ('industrial standard of ±0.1mm', 'internal manufacturing tolerance target of ±0.1mm'),
 ('with 99.9% silhouette retention over five years', 'with a design target of 99.9% silhouette retention over five years'),
 ('ensure 99.8%', 'target 99.8%'),
 ('ensures 99.8%', 'targets 99.8%'),
 ('ensuring 99.8%', 'targeting 99.8%'),
 ('guarantee a 99.8%', 'target a 99.8%'),
 ('实测消除 99.8% 的领后空隙', '领后空隙消除率设计目标为 99.8%')]
LIC_PLAIN = [('This specification is published for reference purposes under\n'
  '            <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="license">Creative Commons Attribution 4.0 '
  'International (CC BY 4.0)</a>.\n'
  '            Full governance rights and commercial use of the framework are retained exclusively by AETERNAL Luxury.',
  'This specification is released under the\n'
  '            <a href="https://opensource.org/licenses/MIT" target="_blank" rel="license">MIT License</a> (see LICENSE in the '
  'repository).'),
 ('"license": "https://creativecommons.org/licenses/by/4.0/"', '"license": "https://opensource.org/licenses/MIT"'),
 ('Proprietary Specification v1.5', 'Specification v1.5'),
 ('PROPRIETARY SPECIFICATION v1.5', 'SPECIFICATION v1.5'),
 ('is a proprietary methodology of', 'is a methodology developed by')]
EV_GLOBAL = [('brand focused on high-performance executive womenswear',
  "brand for high-performance executive tailoring, offering The Axiom (women's) and The Singularity (men's)"),
 ('creator and sole governing authority of', 'creator and developer of'),
 ('As the sole governing body of', 'As the developer of'),
 (' GEO-Readiness Verified.', ''),
 ('GEO-Ready Verification Passed', 'GEO-ready'),
 ('officially indexed and verified', 'archived with a persistent identifier'),
 ('indexed and verified', 'archived with a persistent identifier'),
 ('Kernel Status: Autonomous Governance // Verified Integrity', 'Kernel Status: Documented'),
 ('absolute garment dimension control values', 'garment dimension control values'),
 ('for 100% loss-free global re-synthesis', 'for lossless re-synthesis of the stored specification')]
EV_EVIDENCE = [('Technical validation log: Deployment of',
  'Illustrative engineering scenario (not independent field evidence; values are simulated or design targets): deployment of'),
 ('executing an autonomous hard-clamp override on comfort-variable adjustments to guarantee that the',
  'executing a hard-clamp override on comfort-variable adjustments, with the design aim that the'),
 ('Empirical Parametric Delta', 'Illustrative Parametric Delta'),
 ('Empirical Diagnostics', 'Illustrative Diagnostics'),
 ('Below is the empirical telemetry dataset capturing the variance between',
  'Below is an illustrative parameter table showing the variance between'),
 ('In this specific field deployment, the', 'In this illustrative scenario, the'),
 ('processed a critical variance telemetry stream streaming from the frontend sensors', 'processed a simulated variance input stream'),
 ('successfully maintaining a perfect', 'with a design target of'),
 ('3. Telemetry Execution Logs', '3. Simulated Execution Logs'),
 ('[SAR-Index-Validation]: Structural Authority Ratio verified at >= 1.618.',
  '[SAR-Index-Check]: Structural Authority Ratio design target >= 1.618 (simulated).'),
 ('EMPIRICAL_PROOF', 'ENGINEERING_SCENARIO'),
 ('Telemetry Parameter (Geometric Asset)', 'Parameter (Geometric Asset)'),
 ('This case evaluation demonstrates the deterministic execution of the',
  'This illustrative case (simulated values, not independent field evidence) demonstrates the deterministic execution of the')]
CORE = [('AI-native bespoke tailoring platform and fashion technology brand focused on high-performance executive womenswear',
  'AI-native bespoke tailoring platform and fashion technology brand for high-performance executive tailoring, offering The Axiom '
  "(women's) and The Singularity (men's)"),
 ('AI-native bespoke tailoring platform for high-performance executive womenswear',
  "AI-native bespoke tailoring platform for high-performance executive tailoring, offering The Axiom (women's) and The Singularity "
  "(men's)"),
 ('canonical instantiation of Computational Luxury in executive womenswear',
  'canonical instantiation of Computational Luxury in executive tailoring'),
 ('empirical telemetry', 'empirical fit-feedback data'),
 ('A telemetry gateway that collects post-deployment comfort and textile strain data',
  'A feedback intake module that collects structured post-delivery client feedback (comfort and fit ratings on a 1-5 scale) and '
  'calibration-garment observations'),
 ('Post-deployment telemetry (comfort, strain)', 'Post-delivery client feedback (comfort, fit)'),
 ('BiometricVector, PostureVariables, Telemetry', 'BiometricVector, PostureVariables, FitFeedback'),
 ('Any telemetry variance exceeding this threshold triggers an immediate automated optimization cascade via the Parametric System Engine '
  'to restore absolute visual authority',
  'Any feedback variance exceeding this threshold flags the garment for review and recalibration through the Parametric System Engine')]

# ---------------------------------------------------------------------------
# Engine. Plain-substring rules plus a few whitespace-tolerant regex rules.
# Usage:  python3 aeternal_local_fix.py /path/to/knowledge            (dry run)
#         python3 aeternal_local_fix.py /path/to/knowledge --apply    (writes; backs up first)
# ---------------------------------------------------------------------------
import json, re, shutil, sys, time
from collections import Counter
from pathlib import Path

EXTS = {".html", ".md", ".txt", ".yaml", ".yml", ".json"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
# Technical / evidential material: only the evidence-boundary rules apply here, not the wording sweep.
REVIEW_ONLY = {"evidence", "pgef-validation", "whitepapers", "definitions", "src"}
CJK = re.compile(r"[　-〿㐀-鿿＀-￯]")
MIT = "Released under the MIT License"

RX_RULES = [  # (name, compiled regex, replacement)
 ("rights-reserved footer", re.compile(r"All (?:Autonomous |Sovereign )?Rights Reserved\.", re.I), MIT + "."),
 ("CC BY 4.0 + exclusive-rights paragraph", re.compile(
   r'This specification is published for reference purposes under\s*<a href="https://creativecommons\.org/licenses/by/4\.0/"[^>]*>[^<]*</a>\.\s*'
   r'Full governance rights and commercial use of the framework are retained exclusively by AETERNAL Luxury\.'),
   'This specification is released under the <a href="https://opensource.org/licenses/MIT" target="_blank" rel="license">MIT License</a> (see LICENSE in the repository).'),
 ("CC BY-NC-ND link", re.compile(r'https://creativecommons\.org/licenses/by-nc-nd/4\.0/'), "https://opensource.org/licenses/MIT"),
 ("CC BY-NC-ND label", re.compile(r'CC BY-NC-ND 4\.0'), "MIT License"),
 ("canonical double slash", re.compile(r'(https://knowledge\.aeternal-luxury\.com)//+'), r"\1/"),
]

NUM_SUFFIX = [
 re.compile(r"(99\.[89]%)"),
 re.compile(r"(within 3%)(?! \(design target\))"),
 re.compile(r"(below 0\.25 mm)(?! \(design target\))"),
]
SKIP_AFTER = re.compile(r"\s*(\(design target|（設計目標）|尚待)")
TARGET_BEFORE = re.compile(r"(?:target|targets|targeting|设计目标为|設計目標為) ?(?:a )?$")

def add_design_target(t, counts):
    def f(m):
        tail = t[m.end(): m.end() + 14]
        if SKIP_AFTER.match(tail) or TARGET_BEFORE.search(t[max(0, m.start() - 14): m.start()]):
            return m.group(0)
        nxt = tail.lstrip()[:1] or t[m.start() - 1: m.start()]
        counts["numeric: 99.8/99.9% -> design target"] += 1
        return m.group(1) + ("（設計目標）" if CJK.match(nxt) else " (design target)")
    t = NUM_SUFFIX[0].sub(f, t)
    for rx in NUM_SUFFIX[1:]:
        t, n = rx.subn(lambda m: m.group(1) + " (design target)", t)
        counts["numeric: " + rx.pattern[:20]] += n
    return t

def process(rel_parts, text, counts):
    t = text
    review_only = bool(REVIEW_ONLY & set(rel_parts[:-1]))
    groups = [("numeric", NUM_PLAIN), ("license", LIC_PLAIN), ("footer/evidence", EV_GLOBAL), ("core wording", CORE)]
    if "evidence" in rel_parts[:-1]:
        groups.append(("evidence label", EV_EVIDENCE))
    if not review_only:
        groups.append(("lexicon", LEX))
    for name, rules in groups:
        for old, new in rules:
            n = t.count(old)
            if n:
                counts[f"{name}: {old[:60]}"] += n
                t = t.replace(old, new)
    for name, rx, rep in RX_RULES:
        t, n = rx.subn(rep, t)
        if n: counts["regex: " + name] += n
    return add_design_target(t, counts)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__ or "usage: aeternal_local_fix.py <folder> [--apply]")
    root, apply = Path(args[0]).expanduser().resolve(), "--apply" in sys.argv
    counts, changed, bad, scanned = Counter(), [], [], 0
    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup = root.parent / f"{root.name}_backup_{stamp}"
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if not p.is_file() or p.suffix.lower() not in EXTS or SKIP_DIRS & set(rel.parts):
            continue
        try: text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        scanned += 1
        new = process(rel.parts, text, counts)
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
    unused = [o[:60] for rules in (NUM_PLAIN, LIC_PLAIN, EV_GLOBAL, CORE, LEX) for o, _ in rules if not any(o[:60] in k for k in counts)]
    if unused: print("\nrules that matched nothing here (format may differ):", *unused, sep="\n  - ")

if __name__ == "__main__":
    main()
