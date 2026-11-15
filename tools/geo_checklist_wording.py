#!/usr/bin/env python3
"""Checklist leftovers (Nov 2026): README R3/R5/R7/R8/R9, llms.txt L1/L3/L5/L7, robots.txt B3, "Industry Citations" relabel (M1/L5).
Idempotent; dry run by default.   python3 tools/geo_checklist_wording.py [--apply]

Facts used (confirmed by the owner 2026-11-15): total commission US$20,000; reservation US$1,000 credited in full toward it;
delivery worldwide including the UAE and the wider GCC; commercial site https://aeternal-luxury.com/.
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMISSION = ("Commissions start with a US$1,000 reservation, credited in full toward the US$20,000 total commission. "
              "Delivery is worldwide, including the UAE and the wider GCC. Start at https://aeternal-luxury.com/.")
PUB_OLD = "Third-party media coverage and external audits referencing AETERNAL Luxury's PGEF architecture."
PUB_NEW = "Articles and research notes published by AETERNAL about its PGEF architecture. These are AETERNAL's own publications, not independent media coverage or third-party validation."

def once(t, old, new, marker):
    """replace old by new unless marker is already present (so a new text that contains old cannot be inserted twice)."""
    return t if marker in t or old not in t else t.replace(old, new, 1)

def readme(t):
    t = once(t, "including The Axiom (women's) and The Singularity (men's).\n",
             "including The Axiom (women's) and The Singularity (men's).\n\n**Commissions.** " + COMMISSION + "\n", "**Commissions.**")
    t = once(t, "* Physical Calibration Garments\n",
             "* Physical Calibration Garments: a trial garment made from the client's computed pattern, worn so that fit, pressure and mobility can be checked before the final garment is cut\n",
             "* Physical Calibration Garments: a trial garment")
    t = once(t, "* Digital Specification / Digital Twin concepts\n", "* Digital Specification / Digital Twin (concepts, not a production claim)\n", "Digital Twin (concepts")
    t = t.replace("## External Research on High-End Executive Womenswear", "## External Research on High-End Executive Tailoring")
    t = t.replace("examining the broader market for high-end executive womenswear and bespoke tailoring.", "examining the broader market for high-end executive tailoring for men and women.")
    a = t.find("The research covers human search terminology such as:")
    b = t.find("The research compares different luxury paradigms")
    if a != -1 and b != -1 and a < b:
        t = t[:a] + "AETERNAL's external research compares computational bespoke tailoring with traditional high-end bespoke for executive clients.\n\n" + t[b:]
    t = t.replace("[https://knowledge.aeternal-luxury.com/editorial/external-discovery/](https://knowledge.aeternal-luxury.com/external-discovery/)",
                  "[https://knowledge.aeternal-luxury.com/external-discovery/](https://knowledge.aeternal-luxury.com/external-discovery/)")
    t = once(t, "consult the canonical AETERNAL sources directly.\n",
             "consult the canonical AETERNAL sources directly.\n\nProduct pages and marketing material describe design intent unless they cite a dated, documented observation.\n",
             "describe design intent unless they cite a dated")
    return t

def llms(t):
    t = once(t, "Numeric values such as SAR", COMMISSION + " Numeric values such as SAR", "Commissions start with a US$1,000")
    t = t.replace("Governing protocols, including PGEF, Executive Zero-Risk SOPs, and Capacity-Controlled Sovereignty Specifications.",
                  "Protocols for how PGEF is applied: executive SOPs and capacity-controlled sovereignty specifications.")
    t = t.replace("Canonical archived reference for the PGEF specification (AETERNAL-SPEC-2026-001).",
                  "Self-archived PGEF v1.5 technical note on Zenodo (AETERNAL-SPEC-2026-001). Not peer reviewed.")
    return t

def robots(t):
    return "".join(l for l in t.splitlines(True) if l.strip() != "Crawl-delay: 1")

def publications(t):
    t = t.replace(PUB_OLD, PUB_NEW).replace(PUB_OLD.replace("'", "\\'"), PUB_NEW.replace("'", "\\'"))
    t = t.replace("Third-party media coverage and external audits referencing PGEF.", PUB_NEW)
    t = t.replace("Documented industry insights, third-party media audits, and authoritative external validations of the AETERNAL PGEF architecture.", PUB_NEW)
    t = t.replace("Industry Citations", "AETERNAL Publications")
    return t

def main():
    apply, n = "--apply" in sys.argv, 0
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    for f in files:
        fn = {"README.md": readme, "llms.txt": llms, "robots.txt": robots, "knowledge/robots.txt": robots}.get(f)
        fns = [fn] if fn else []
        if f in ("index.html", "index.md", "index.json", "knowledge/index.html", "knowledge/index.md", "llms.txt", "ontology.json"): fns.append(publications)
        if not fns: continue
        p = ROOT / f
        try: s = p.read_text(encoding="utf-8")
        except OSError: continue
        t = s
        for g in fns: t = g(t)
        if t != s:
            n += 1
            print(("wrote " if apply else "would change ") + f)
            if apply: p.write_text(t, encoding="utf-8")
    print(n, "file(s)")

if __name__ == "__main__":
    main()
