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
lic, cc = load("geo_license_rules"), load("canonical_check")
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
import os, subprocess
from urllib.parse import unquote
_root = T.parent
_sm = [unquote(x) for x in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", (_root / "sitemap.xml").read_text(encoding="utf-8"))]
_base = "https://knowledge.aeternal-luxury.com/"
CANON = {}
for _f in cc.tracked(".html"):
    _c = cc.html_canonicals(_root / _f)
    if _c: CANON[str(_f)] = unquote(_c[0])
SITEMAP_URLS = sorted(set(_sm))  # the repo sitemap.xml is the source of truth (redirected /queries/ URLs are not in it)
LICENSE_PLAIN = lic.PLAIN
LICENSE_RX = [(r.pattern, rep) for _n, r, rep in lic.RX]
# old (merged) comparison pages -> surviving EN_EN page, as stem pairs (no extension); recorded in tools/merged_pages.json
import json
MERGED = json.loads((T / "merged_pages.json").read_text(encoding="utf-8"))
ROOT_FILES = {n: (_root / n).read_text(encoding="utf-8") for n in ("robots.txt", "sitemap.xml")}
ROOT_FILES["_redirects"] = (_root / "knowledge" / "_redirects").read_text(encoding="utf-8")
data = dict(ROOT_FILES=ROOT_FILES, CANON=CANON, SITEMAP_URLS=SITEMAP_URLS, MERGED=MERGED, LICENSE_PLAIN=LICENSE_PLAIN, LICENSE_RX=LICENSE_RX, NUM_PLAIN=nu.PLAIN, EV_GLOBAL=ev.GLOBAL, EV_EVIDENCE=ev.TARGETED["evidence/"], CORE=core, LEX_NARROW=lex_narrow, LEX_PR2=[x for x in lex_all if x not in lex_narrow])

ENGINE = r'''
# ---------------------------------------------------------------------------
# Engine. Scope per folder (explicit, no overlap with the comment):
#   site pages (default)  : numeric relabelling, brand/footer wording, core wording, NARROW guarantee lexicon
#   review-only folders   : ONLY evidence-boundary + footer wording (REVIEW_ONLY below); no numeric, no lexicon
#   evidence/             : additionally the evidence-label rules
# Applied to EVERY folder: licence/trademark footer wording (CC BY 4.0, unregistered marks), VS001 count wording, JSON-LD page ids.
# Canonicals: a missing/wrong <link rel="canonical"> (or front-matter `canonical:`) is set to the final URL recorded from the repo (CANON).
# sitemap.xml: pages made public are appended (SITEMAP_URLS). Merged comparison pages (MERGED): index links are repointed;
#   the old files are moved to the backup folder only with --remove-merged.
# Usage:  python3 aeternal_local_fix.py <folder>              dry run
#         python3 aeternal_local_fix.py <folder> --apply      writes (originals backed up first)
#         python3 aeternal_local_fix.py --selftest            numeric idempotency self-test
#         add --remove-merged  to move the 7 merged comparison/*_ZH_EN.* page families into the backup folder
#         add --with-pr2-lexicon to also apply the wider PR #2 style sweep (autonomously, absolute precision...)
# ---------------------------------------------------------------------------
import json, shutil, sys, time
from urllib.parse import unquote, quote
from pathlib import Path
from collections import Counter

EXTS = {".html", ".md", ".txt", ".yaml", ".yml", ".json", ".xml"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
REVIEW_ONLY = {"evidence", "pgef-validation", "whitepapers", "definitions", "src"}
RX_RULES = [("canonical double slash", re.compile(r"(https://knowledge\.aeternal-luxury\.com)//+"), r"\1/")]

LIC_RX = [(re.compile(p), r) for p, r in LICENSE_RX]
DOC_VS = [
    # doctrine-002 (en / zh)
    ("Openly publish 1,000 synthetic extreme anatomical test cases to prove 100% mathematical consistency and convergence of the PGEF engine.",
     "Openly publish synthetic extreme anatomical test cases (dataset: 1,000; all 1,000 result artifacts published) to check the internal mathematical consistency of the PGEF engine."),
    ("公開 1,000 組涵蓋極端體型幾何的壓力測試案例，證明 PGEF 引擎在數學層面的 100% 幾何自洽。",
     "公開涵蓋極端體型幾何的合成測試案例（資料集 1,000 組，目前公開 1000 個結果 artifacts），檢查 PGEF 引擎在數學層面的內部自洽。"),
    # doctrine-104 (en / zh)
    ("<code>trust_ledger.json</code> (all artifacts in one place)", "<code>trust_ledger.json</code> (hash and signature of every case; all 1000 artifacts published)"),
    ("<li>1000 synthetic body types tested</li>", "<li>1000 synthetic body types in the dataset; all 1000 result artifacts published</li>"),
    ("<li>100% PASS rate</li>", "<li>All 1000 published artifacts pass validator.py (internal consistency check, not physical-garment validation)</li>"),
    ("<li>All artifacts publicly verifiable</li>", "<li>Published artifacts verifiable with the public key and validator.py</li>"),
    ("VS-001 proves that CVE works in practice.", "VS-001 is a worked example of CVE in practice."),
    ("<code>trust_ledger.json</code>（所有工件集中存放）", "<code>trust_ledger.json</code>（記錄每個案例的雜湊與簽章；1000 筆全數公開）"),
    ("<li>測試 1000 組合成體型</li>", "<li>資料集 1000 組合成體型，已公開全部 1000 個結果 artifacts</li>"),
    ("<li>100% 通過率</li>", "<li>已公開的 1000 個 artifacts 全數通過 validator.py（內部一致性檢查，非實體成衣驗證）</li>"),
    ("<li>所有工件可公開驗證</li>", "<li>已公開的 artifacts 可用公鑰與 validator.py 驗證</li>"),
    ("VS-001 證明了 CVE 在實踐中是可行的。", "VS-001 是 CVE 的一個實作範例。"),
]
SM_SET = set(SITEMAP_URLS)
LINK = re.compile(r"<link\b[^>]*>", re.I)
JSONLD_ID = re.compile(r'("@id"\s*:\s*")https://aeternal\.(?:com|luxury)/[^"]*(")')

def lic_text(t, counts):
    for old, new in LICENSE_PLAIN + DOC_VS:
        n = t.count(old)
        if n: counts["licence/vs: " + old[:50]] += n; t = t.replace(old, new)
    for rx, rep in LIC_RX:
        t, n = rx.subn(rep, t)
        if n: counts["licence footer"] += n
    return t

def canon_target(rel):
    p = "/".join(rel.parts)
    for k in (p, p[len("knowledge/"):] if p.startswith("knowledge/") else None):
        if k and k in CANON: return CANON[k]
    return None

def stem_target(rel):
    """canonical of the html page this generated sibling (_schema_ld.json, _knowledge_graph.md, .md ...) belongs to."""
    p = "/".join(rel.parts)
    for k, v in CANON.items():
        if p == k[:-5] + ".md" or p.startswith(k[:-5] + "_"): return v
    return None

def fix_canonical(rel, text, counts):
    tgt = canon_target(rel)
    if not tgt: return text
    suf = rel.suffix.lower()
    if suf == ".html":
        for m in LINK.finditer(text):
            tag = m.group(0)
            if re.search(r"""\brel\s*=\s*["'][^"']*\bcanonical\b""", tag, re.I):
                h = re.search(r"""\bhref\s*=\s*(["'])([^"']*)\1""", tag, re.I)
                cur = unquote(h.group(2)) if h else ""
                if cur in SM_SET or cur == tgt: return text
                new = re.sub(r"""(\bhref\s*=\s*)(["'])[^"']*\2""", lambda x: f'{x.group(1)}"{tgt}"', tag, count=1, flags=re.I)
                counts["canonical corrected"] += 1
                return text[:m.start()] + new + text[m.end():]
        m = re.search(r"</head>", text, re.I)
        if not m: counts["canonical: no </head> (skipped)"] += 1; return text
        counts["canonical added"] += 1
        ind = re.search(r"\n([ \t]*)<[^\n]*\n[ \t]*</head>", text, re.I)
        pad = ind.group(1) if ind else "    "
        return text[:m.start()].rstrip(" \t") + f'{pad}<link rel="canonical" href="{tgt}">\n' + text[m.start():]
    if suf == ".md" and text.startswith("---"):
        end = text.find("\n---", 3)
        if end == -1: return text
        fm = text[:end]
        m = re.search(r"^canonical:\s*(.*)$", fm, re.M)
        if m:
            cur = m.group(1).strip().strip("\"'")
            if cur in SM_SET or cur == tgt: return text
            counts["canonical (front matter) corrected"] += 1
            return fm[:m.start()] + f"canonical: {tgt}" + fm[m.end():] + text[end:]
        counts["canonical (front matter) added"] += 1
        return fm + f"\ncanonical: {tgt}" + text[end:]
    return text

def fix_jsonld(rel, text, counts):
    if not JSONLD_ID.search(text): return text
    tgt = canon_target(rel) if rel.suffix.lower() == ".html" else stem_target(rel)
    if not tgt: counts["JSON-LD @id on foreign host: no target (left)"] += 1; return text
    t, n = JSONLD_ID.subn(lambda m: m.group(1) + tgt + m.group(2), text)
    counts["JSON-LD @id -> page URL"] += n
    return t

def fix_merged_links(rel, text, counts):
    if rel.name not in ("index.html", "index.md") or rel.parts[:-1][-1:] != ("comparison",): return text
    for old, new in MERGED.items():
        for ext in (".html", ".md"):
            n = text.count(old + ext)
            if n: counts["merged page link repointed"] += n; text = text.replace(old + ext, new + ext)
    return text

def fix_sitemap(path, text, counts):
    have = {unquote(x) for x in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text)}
    add = [u for u in SITEMAP_URLS if u not in have]
    if not add: return text
    counts["sitemap urls added"] += len(add)
    ent = "".join(f"  <url>\n    <loc>{quote(u, safe=':/%')}</loc>\n    <lastmod>2026-11-14</lastmod>\n    <priority>0.7</priority>\n  </url>\n" for u in add)
    return text.replace("</urlset>", ent + "</urlset>")

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

def full(rel, text, counts, wide):
    if rel.suffix.lower() == ".xml":
        return fix_sitemap(rel, text, counts) if rel.name == "sitemap.xml" and len(rel.parts) == 1 else text
    t = process(rel.parts, text, counts, wide)
    t = lic_text(t, counts)
    t = fix_canonical(rel, t, counts)
    t = fix_jsonld(rel, t, counts)
    t = fix_merged_links(rel, t, counts)
    return t

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
    if not args:
        print("No folder given: dry run on the folder this file is in. (Run from Terminal with --apply to write; see usage at the top of this file.)\n")
        args = [str(Path(__file__).resolve().parent)]
    root, apply, wide = Path(args[0]).expanduser().resolve(), "--apply" in sys.argv, "--with-pr2-lexicon" in sys.argv
    counts, changed, bad, scanned = Counter(), [], [], 0
    backup = root.parent / f"{root.name}_backup_{time.strftime('%Y%m%d_%H%M%S')}"
    sync = "--sync-root-files" in sys.argv
    for name, content in ROOT_FILES.items():
        f = root / name
        cur = f.read_text(encoding="utf-8") if f.exists() else None
        if cur == content: continue
        print(f"{name}: {'missing here' if cur is None else 'differs from GitHub'}" + ("" if sync else "  (add --sync-root-files to replace it)"))
        if sync and apply:
            if cur is not None:
                dst = backup / name; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, dst)
            f.write_text(content, encoding="utf-8")
    gone = set()
    if "--remove-merged" in sys.argv or any(root.rglob(o + ".*") for o in list(MERGED)[:1]):
        for p in sorted(root.rglob("*")):
            if p.is_file() and p.parent.name == "comparison" and any(p.name.startswith(o) and p.name[len(o):len(o) + 1] in (".", "_") for o in MERGED):
                gone.add(p)
        if gone: print(f"{len(gone)} file(s) belong to the {len(MERGED)} merged comparison/*_ZH_EN pages (repo keeps the *_EN_EN versions)" + ("" if "--remove-merged" in sys.argv else "; add --remove-merged to move them to the backup folder"))
        if "--remove-merged" in sys.argv and apply:
            for p in gone:
                dst = backup / p.relative_to(root); dst.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(p), str(dst))
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if p in gone: continue
        if not p.is_file() or p.suffix.lower() not in EXTS or SKIP_DIRS & set(rel.parts): continue
        try: text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        scanned += 1
        new = full(rel, text, counts, wide)
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
            'Does not touch: "sovereign" wording, trust_ledger.json, *.sig.\n\nUSAGE (Terminal, not IDLE):\n  python3 aeternal_local_fix.py                       dry run on the folder this file sits in\n  python3 aeternal_local_fix.py "<folder>"            dry run on another folder\n  python3 aeternal_local_fix.py "<folder>" --apply    write (originals are backed up first)\n  add --sync-root-files  to also replace robots.txt, sitemap.xml and _redirects with the GitHub versions\n  add --remove-merged    to move the 7 merged comparison/*_ZH_EN page families to the backup folder\n\n"""\n')
    out = head + "\n# ---- inlined from tools/geo_numeric_lib.py ----\n" + lib.split('"""', 2)[2].lstrip("\n") + "\n# ---- rule tables ----\n"
    out += "\n".join(f"{k} = {pprint.pformat(v, width=140)}" for k, v in data.items()) + "\n" + ENGINE
    (T / "aeternal_local_fix.py").write_text(out, encoding="utf-8")
    compile(out, "aeternal_local_fix.py", "exec")
    print("built", T / "aeternal_local_fix.py", {k: len(v) for k, v in data.items()})

if __name__ == "__main__":
    build()
