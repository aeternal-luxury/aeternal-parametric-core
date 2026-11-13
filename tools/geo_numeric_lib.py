"""Shared, idempotent logic for relabelling unverified numeric PERFORMANCE claims as design targets.

Used by tools/geo_numeric_claims.py (repo) and inlined into tools/aeternal_local_fix.py (local) by
tools/build_local_fix.py, so both tools always behave identically.

What is annotated: 99.8% / 99.9% / "within 3%" / "below 0.25 mm" when the surrounding sentence is a
physical-performance statement (fit, adherence, retention, deformation, wear...) and the sentence does
not already carry a qualifier (design target / goal / aim / internal metric / not independently verified).
What is NOT touched: LaTeX/maths (`$..$`, `\\ge 99.8\\%`), sentences that define internal parameters
(K =, SAR / PPR definitions), and anything already qualified.
"""
import re

SUFFIX_EN, SUFFIX_ZH = " (design target)", "（設計目標）"
ANY_SUFFIX = r"(?:\(design target\)|（設計目標）)"
CJK = re.compile(r"[　-〿㐀-鿿＀-￯]")
TOKEN = re.compile(r"(99\.[89]%|within 3%|below 0\.25 mm)")
SENT_END = re.compile(r"[.。!?！？\n]")
PERF = re.compile(
    r"adheren|adhesion|collar|retention|invarian|wear|silhouette|displacement|deformation|deviation|"
    r"drift|lift|shoulder|fit\b|contact|rigidity|贴合|貼合|廓形|形變|變形|位移|穿著|穿戴|領|肩|咬合|維持|保持|小時|hour", re.I)
QUALIFIED = re.compile(
    r"design[- ](?:target|goal|aim|intent)|internal (?:metric|target)|target(?:s|ing)?\b|aims? (?:to|for)|"
    r"not (?:yet )?independently verified|設計目標|設計目的|設計指標|目標|尚待獨立驗證|内部指標|內部指標", re.I)
MATHISH = re.compile(r"\$|\\ge|\\le|\\text|\\mathrm|\bK\s*=|κ")

def _sentence(t, a, b):
    s = max((m.end() for m in SENT_END.finditer(t, max(0, a - 260), a)), default=max(0, a - 260))
    m = SENT_END.search(t, b, b + 260)
    return s, (m.start() if m else min(len(t), b + 260))

def normalise(t):
    """Collapse duplicated markers: '(design target) (design target)' -> one."""
    return re.sub(rf"({ANY_SUFFIX})(?:\s*{ANY_SUFFIX})+", r"\1", t)

def annotate(t, counts=None):
    """Return text with markers added/removed so the result is a fixed point (running twice == once)."""
    t = normalise(t)
    out, pos = [], 0
    for m in TOKEN.finditer(t):
        a, b = m.span()
        mk = re.match(rf"\s*({ANY_SUFFIX})", t[b:b + 24])
        end = b + (mk.end() if mk else 0)
        s, e = _sentence(t, a, end)
        sent_wo = t[s:a] + t[end:e]               # sentence without the token and its marker
        qualified = bool(QUALIFIED.search(sent_wo))
        perf = bool(PERF.search(t[s:e])) and not MATHISH.search(t[s:e])
        if mk and qualified:                      # repair: marker is redundant
            out.append(t[pos:b]); pos = end
            if counts is not None: counts["removed redundant marker"] = counts.get("removed redundant marker", 0) + 1
        elif not mk and perf and not qualified:   # first-time annotation
            nxt = t[b:b + 14].lstrip()[:1] or t[a - 1:a]
            nxt = t[b:e].lstrip()[:1] or nxt
            out.append(t[pos:b] + (SUFFIX_ZH if CJK.match(nxt) else SUFFIX_EN)); pos = b
            if counts is not None: counts["added marker"] = counts.get("added marker", 0) + 1
    out.append(t[pos:])
    return "".join(out)
