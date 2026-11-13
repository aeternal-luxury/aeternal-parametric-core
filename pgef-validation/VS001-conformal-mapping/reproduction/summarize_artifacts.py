#!/usr/bin/env python3
"""Summarise the PUBLISHED VS001 artifacts (what is actually in artifacts/) and optionally redraw figures/.

    python reproduction/summarize_artifacts.py            # print the summary used in the docs
    python reproduction/summarize_artifacts.py --figures  # also regenerate figures/*.png (needs matplotlib)
Every number quoted in README.md / specification.md / manifest.json comes from this script.
"""
import collections, glob, json, re, statistics, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
rs = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(str(HERE / "artifacts" / "result_*.json")))]
ids = {int(r["case_id"]) for r in rs}
ledger = json.load(open(HERE.parent / "trust_ledger.json", encoding="utf-8"))
lids = {int(e["case_id"]) for e in ledger["entries"]}
missing = sorted(set(range(1, 1001)) - ids)
by_date = collections.Counter(r["metadata"]["generated_at"][:10] for r in rs)
grades = collections.Counter(r["grade"] for r in rs)
m = lambda k: [r["metrics"][k] for r in rs]
S = dict(
    published=len(rs), dataset_cases=1000, ledger_entries=len(lids), ledger_without_artifact=len(lids - ids),
    missing_range=(missing[0], missing[-1]) if missing else None, contiguous_gap=missing == list(range(missing[0], missing[-1] + 1)) if missing else True,
    status=dict(collections.Counter(r["status"] for r in rs)), grades=dict(sorted(grades.items())), dates=dict(sorted(by_date.items())),
    mse=(statistics.mean(m("mse")), max(m("mse"))), delta_p=(statistics.mean(m("delta_p")), max(m("delta_p"))),
    area=(statistics.mean(m("area_distortion")), max(m("area_distortion"))),
    embedded_signatures=sum(bool(r.get("signature")) for r in rs), sig_files=len(glob.glob(str(HERE / "artifacts" / "*.sig"))),
)
if __name__ == "__main__":
    print(json.dumps(S, indent=2, ensure_ascii=False))
    if "--figures" in sys.argv:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        out = HERE / "figures"; n = len(rs)
        fig, ax = plt.subplots(figsize=(8, 5), dpi=300); ax.hist(m("mse"), bins=40, color="#2b6cb0")
        ax.set(title=f"VS001 — MSE distribution ({n} published artifacts)", xlabel="MSE", ylabel="cases"); fig.tight_layout(); fig.savefig(out / "mse_distribution.png"); plt.close(fig)
        fig, ax = plt.subplots(figsize=(6, 6), dpi=300); g = sorted(grades.items())
        ax.pie([v for _, v in g], labels=[f"{k}: {v}" for k, v in g], autopct="%1.1f%%", startangle=90)
        ax.set_title(f"VS001 — grade distribution ({n} published artifacts, all PASS)"); fig.tight_layout(); fig.savefig(out / "pass_fail.png"); plt.close(fig)
        fig, axs = plt.subplots(2, 2, figsize=(11, 8), dpi=300)
        axs[0, 0].hist(m("mse"), bins=40, color="#2b6cb0"); axs[0, 0].set_title("MSE")
        axs[0, 1].hist(m("area_distortion"), bins=40, color="#2f855a"); axs[0, 1].set_title("Area distortion")
        axs[1, 0].hist(m("delta_p"), bins=40, color="#b7791f"); axs[1, 0].set_title("ΔP")
        axs[1, 1].bar([k for k, _ in g], [v for _, v in g], color="#4a5568"); axs[1, 1].set_title("Grade distribution")
        fig.suptitle(f"VS001 validation report — {n} published artifacts (dataset: 1000 synthetic cases; ledger: 1000 entries)"); fig.tight_layout(); fig.savefig(out / "validation_report.png"); plt.close(fig)
        print("figures regenerated")
