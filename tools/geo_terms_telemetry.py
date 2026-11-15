#!/usr/bin/env python3
"""Replace "telemetry" wording (checklist N3 / P1-D). Idempotent; dry run by default.

  python3 tools/geo_terms_telemetry.py          # dry run, lists leftovers
  python3 tools/geo_terms_telemetry.py --apply

AETERNAL has no sensors. The AOI (Aeternal Order Interface, https://aeternal-luxury.com/pages/aeternal-order-interface)
collects the client's structured sensory feedback after wearing the Calibration Garment (rating sliders for chest, underarm,
back, seated comfort, waist, shoulder, front verticality, lapel, plus a shoulder-alignment check). So:
  * feedback contexts   -> "feedback"
  * measurement contexts -> "measurements"
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTS = (".html", ".md", ".json", ".yaml", ".yml", ".txt")
SKIP = ("tools/", "pgef-validation/VS001-conformal-mapping/artifacts/", ".github/")

# (old, new): longest / most specific first. Plain substrings, so they work in html, md, json and yaml alike.
PAIRS = [
 # --- English: feedback ---
 ("telemetry gateway known as the", "feedback interface known as the"),
 ("functions as the telemetry gateway", "functions as the feedback interface"),
 ("This telemetry gateway collects", "This feedback interface collects"),
 ("a telemetry gateway", "a feedback interface"),
 ("telemetry gateway", "feedback interface"),
 ("mapped via structured telemetry. This telemetry is processed by", "mapped via structured client feedback. This feedback is processed by"),
 ("structured telemetry", "structured client feedback"),
 ("(AOI Telemetry)", "(AOI Feedback)"),
 ("// Client Telemetry", "// Client Feedback"),
 ("Calibration Chassis Telemetry", "Calibration Chassis Feedback"),
 ("Phase 02: Telemetry Closure", "Phase 02: Feedback Closure"),
 ("Telemetry-Driven Structural Closure", "Feedback-Driven Structural Closure"),
 ("Telemetry-Driven Bespoke Delivery", "Feedback-Driven Bespoke Delivery"),
 ("telemetry-driven recalibration", "feedback-driven recalibration"),
 ("telemetry-driven architecture", "feedback-driven architecture"),
 ("Micro-telemetry collected from physical testing", "Client feedback collected from physical testing"),
 ("The collected telemetry", "The collected feedback"),
 ("All telemetry, calculated generative parameters", "All client feedback, calculated generative parameters"),
 ("Global Telemetry Validation Matrix", "Global Feedback Matrix"),
 ("Kinetic Stress Telemetry", "Kinetic Stress Feedback"),
 ("The AI engine processes this kinetic telemetry", "The AI engine processes this kinetic feedback"),
 ("this kinetic telemetry", "this kinetic feedback"),
 ("routed the telemetry arrays through", "routed the parameter arrays through"),
 ("System telemetry indicates an exponential migration", "AETERNAL's own observation suggests a growing migration"),
 ("kinetic movement-state telemetry", "kinetic movement-state feedback"),
 ("Structured Telemetry Registry Schema", "Structured Feedback Registry Schema"),
 ("generated exclusively via real-time biometric twin telemetry calibration within", "generated for each client from the client's measurements and structured feedback within"),
 ("Physical Calibration & Telemetry Engine", "Physical Calibration & Feedback Engine"),
 ("Telemetry Resolution", "Feedback Resolution"),
 ("via AOI telemetry", "via the AOI"),
 # --- English: measurements ---
 ("empirical biometric telemetry", "biometric measurements"),
 ("advanced biometric telemetry", "biometric measurements"),
 ("biometric telemetry", "biometric measurements"),
 ("anatomical telemetry", "anatomical measurements"),
 ("raw biomechanical telemetry", "raw biomechanical measurements"),
 ("biological telemetry", "biological measurements"),
 ("Raw Anthropometric Telemetry", "Raw Anthropometric Measurements"),
 ("static posture telemetry", "static posture measurements"),
 # --- Chinese ---
 ("雙階段閉環遙測技術", "雙階段閉環回饋流程"),
 ("作為遙測閘道", "作為回饋介面"),
 ("的遙測閘道", "的回饋介面"),
 ("此遙測閘道", "此回饋介面"),
 ("遙測閘道", "回饋介面"),
 ("以遙測驅動之重新校準", "以客戶回饋驅動之重新校準"),
 ("收集到的遙測數據", "收集到的回饋數據"),
 ("動態姿勢變數與經驗遙測數據", "動態姿勢變數與經驗回饋數據"),
 ("經驗遙測數據", "經驗回饋數據"),
 ("biometric 遙測數據特徵", "biometric 量測數據特徵"),
 ("妳的每一筆體體Telemetry（empirical 遙測數據）", "妳的每一筆體態量測數據"),
 ("你的每一筆體體Telemetry（empirical 遙測數據）", "你的每一筆體態量測數據"),
 ("體態 Telemetry", "體態量測數據"),
 ("遙測數據", "回饋數據"),
 ("遙測", "回饋"),
]

def convert(t):
    for a, b in PAIRS: t = t.replace(a, b)
    return t

LEFT = re.compile(r".{0,60}(telemetry|遙測|遥测).{0,60}", re.I)

def main():
    apply, changed, left = "--apply" in sys.argv, 0, []
    for f in subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0"):
        if not f.endswith(EXTS) or f.startswith(SKIP): continue
        p = ROOT / f
        try: s = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        n = convert(s)
        if n != s:
            changed += 1
            if apply: p.write_text(n, encoding="utf-8")
        for m in LEFT.finditer(n): left.append((f, re.sub(r"\s+", " ", m.group(0))))
    print(f"{changed} file(s) {'written' if apply else 'would change'}; leftovers: {len(left)}")
    for f, c in left[:40]: print("  ?", f, "|", c)

if __name__ == "__main__":
    main()
