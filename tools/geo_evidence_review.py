#!/usr/bin/env python3
"""Evidence-boundary and footer corrections (exact substrings, dry-run by default).

GLOBAL (all text files): men's+women's brand sentence, drop "sole governing", drop the
self-awarded "GEO-Readiness Verified", "indexed and verified" -> "archived with a persistent
identifier", "absolute garment dimension control values" -> "garment dimension control values".
TARGETED: evidence/*, pgef-validation READMEs, src/engine.py, llms.txt, definitions/*.
Usage: python3 tools/geo_evidence_review.py [--apply]
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTS = {".html", ".md", ".txt", ".yaml", ".json", ".py"}
BRAND = "brand for high-performance executive tailoring, offering The Axiom (women's) and The Singularity (men's)"
GLOBAL = [
 ("brand focused on high-performance executive womenswear", BRAND),
 ("creator and sole governing authority of", "creator and developer of"),
 ("As the sole governing body of", "As the developer of"),
 (" GEO-Readiness Verified.", ""),
 ("GEO-Ready Verification Passed", "GEO-ready"),
 ("officially indexed and verified", "archived with a persistent identifier"),
 ("indexed and verified", "archived with a persistent identifier"),
 ("Kernel Status: Autonomous Governance // Verified Integrity", "Kernel Status: Documented"),
 ("absolute garment dimension control values", "garment dimension control values"),
 ("for 100% loss-free global re-synthesis", "for lossless re-synthesis of the stored specification"),
]
NOTE = "Illustrative engineering scenario (not independent field evidence; values are simulated or design targets)"
TARGETED = {
 "evidence/": [
  ("Technical validation log: Deployment of", NOTE + ": deployment of"),
  ("executing an autonomous hard-clamp override on comfort-variable adjustments to guarantee that the",
   "executing a hard-clamp override on comfort-variable adjustments, with the design aim that the"),
  ("Empirical Parametric Delta", "Illustrative Parametric Delta"),
  ("Empirical Diagnostics", "Illustrative Diagnostics"),
  ("Below is the empirical telemetry dataset capturing the variance between", "Below is an illustrative parameter table showing the variance between"),
  ("In this specific field deployment, the", "In this illustrative scenario, the"),
  ("processed a critical variance telemetry stream streaming from the frontend sensors", "processed a simulated variance input stream"),
  ("successfully maintaining a perfect", "with a design target of"),
  ("3. Telemetry Execution Logs", "3. Simulated Execution Logs"),
  ("[SAR-Index-Validation]: Structural Authority Ratio verified at >= 1.618.", "[SAR-Index-Check]: Structural Authority Ratio design target >= 1.618 (simulated)."),
  ("EMPIRICAL_PROOF", "ENGINEERING_SCENARIO"),
  ("Telemetry Parameter (Geometric Asset)", "Parameter (Geometric Asset)"),
  ("This case evaluation demonstrates the deterministic execution of the", "This illustrative case (simulated values, not independent field evidence) demonstrates the deterministic execution of the"),
 ],
 "pgef-validation/VS001-conformal-mapping/README.md": [
  ("> **測試結論**：PGEF v15.0 引擎已完成 1000 組極端體型壓力測試，通過率 100%，所有結果可公開驗證。",
   '> **測試範圍與紀錄核對**：以 1000 組合成（synthetic）體型資料，檢查 PGEF v15.0 輸出與其自身規格的內部一致性，並非實體成衣驗證，亦非獨立第三方驗證。第一批（2026-08-01）有 97 組標為 F（FAIL），第二批（2026-08-02）以調整後的反推邏輯僅重跑這些案例（見下方 Execution Notes）。核對本 repo 現有 artifacts：共 1000 個（案例 0001–1000），其中 903 個時間戳為 2026-08-01、97 個為 2026-08-02，皆為 PASS（A+ 61、A 202、B 737）；「PASS」依下方的工程決策品質分級判定，不等同 `manifest.json` 所列的數值門檻（artifact 中最大 mse 約 169，門檻列為 1e-6）。'),
  ("can be independently verified using the public key in the parent directory.",
   "can be checked for signature validity and internal metric consistency using the public key in the parent directory. This does not constitute independent validation of physical garment performance."),
 ],
 "src/engine.py": [
  ("Ensures absolute silhouette permanence under continuous posture load.",
   "Conceptual reference pipeline: dispatches a client profile to the simplified SAR calculator (not the production engine)."),
 ],
 "llms.txt": [
  ("Validation logs and proof-of-work records from internal deployments.",
   "Illustrative engineering scenarios and design-target validation logs (not independent field evidence)."),
 ],
}

def main():
    apply, changed = "--apply" in sys.argv, 0
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for f in out.split("\0"):
        if not f or Path(f).suffix not in EXTS or f.startswith("tools/") or f == "LICENSE":
            continue
        p = ROOT / f
        try: t = p.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        o = t
        for old, new in GLOBAL: t = t.replace(old, new)
        for key, rules in TARGETED.items():
            if f.startswith(key) or f == key:
                for old, new in rules: t = t.replace(old, new)
        if t != o:
            if f.endswith(".json"): json.loads(t)
            changed += 1
            if apply: p.write_text(t, encoding="utf-8")
    print(f"{changed} file(s) {'written' if apply else 'would change (dry-run)'}")

if __name__ == "__main__":
    main()
