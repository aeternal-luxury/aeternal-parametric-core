
# VS001-conformal-mapping: Conformal Mapping Validation

> **紀錄核對（以 repo 現存檔案為準）**：本 VS 的資料集為 1000 組合成（synthetic）體型參數（`dataset/synthetic_1000.json`）。repo 公開的 artifacts 共 900 個（案例 0601–0700 的 100 個未公開），全數通過 `validator.py` 的雜湊、簽章、結構與指標一致性檢查（900/900）；等級分布為 A+ 54、A 180、B 666；產生日期為 2026-08-01（818 個）與 2026-08-02（82 個）。`trust_ledger.json` 記錄 1000 筆，其中 100 筆（案例 0601–0700）沒有對應的公開 artifact，因此 `python validator.py --verify-ledger` 目前會回報 FAIL。PASS 依下方「工程決策品質」分級判定，並非依數值誤差門檻。本驗證檢查的是引擎輸出與其自身規格的內部一致性，並非實體成衣驗證，亦非獨立第三方驗證。

> **Evidence / Trust README** — 本 VS 的信任證據摘要


## Architecture

```
PGEF Engine (Proprietary)
        ↓
Artifacts (result_XXXX.json)
        ↓
ECDSA Signature (private key)
        ↓
Trust Ledger (all hashes + signatures)
        ↓
Validator (public verification)
        ↓
Anyone can verify
```

**The production engine remains proprietary.**
Instead of revealing the production algorithm, every Artifact is cryptographically signed.
The signature proves that the published outputs originated from the genuine production engine.
Therefore the validation layer verifies:

- **Metric correctness** (MSE, ΔP, area distortion are self-consistent)
- **Production authenticity** (outputs came from PGEF, not hand-crafted)

**without disclosing any proprietary algorithms.**


## Trust Ledger

The root `trust_ledger.json` (in `pgef-validation/`) records all Artifacts in a single, immutable ledger. It serves as the **bridge between A (correct metric computation) and B (genuine engine output)**.

- Anyone can verify the ledger: `python validator.py --verify-ledger`
- The ledger records: case_id → artifact_hash → signature → status → grade
- If any Artifact is replaced or modified, the hash will mismatch and the ledger check will fail.


## Purpose

This validation verifies that the PGEF v15.0 engine produces garment dimensions that are **mathematically consistent** with its own engineering specifications, across a diverse range of synthetic body types.

Specifically, it validates:

- **Proportional consistency**: The relationship between key garment dimensions (waist and shoulder) falls within the brand's defined aesthetic tolerance, unless constrained by physical limits.
- **Physical boundary compliance**: Garment dimensions respect anatomical and structural limits defined in the engineering specification.
- **Formula adherence**: All derived garment dimensions (length, sleeve, chest ease, etc.) match the values computed from the specification-defined formulas.
- **Adaptive logic**: The engine correctly detects and activates specialized compensation modes for extreme body types.
- **Inverse fitting**: When dimensional relationships deviate from targets, the engine attempts corrective adjustments (expanding shoulder width, reducing waist) within the limits of the physical boundary.

**This is a mathematical consistency check, not a product quality evaluation.** It tests whether the engine's outputs match its own definitions—regardless of whether those definitions are aesthetically or commercially desirable.


## Validation Grading (Engineering Decision Quality)

The grades below describe **engineering decision quality**, not product quality. All PASS grades (A++, A+, A, B) represent valid engineering outcomes under different physical constraints.

| Grade | Status | Meaning |
|---|---|---|
| **A++** | PASS | The engine achieved a result **beyond** the ideal target. This occurs when the body geometry naturally exceeds the aesthetic standard, or when the final output surpasses the defined tolerance. |
| **A+** | PASS | The engine precisely achieved its ideal mathematical target without structural compromise. |
| **A** | PASS | A structural boundary was encountered; the engine made a conservative, safe adjustment. Minor deviation from the ideal target is accepted. |
| **B** | PASS | A structural boundary was reached; the engine made a conservative adjustment, but the input body geometry is extreme, causing a larger deviation from the ideal target. **This is a documented compromise, not a failure.** |
| **C** | PASS | Reserved for edge cases requiring manual review (not expected in normal operation). |
| **F** | FAIL | The engine identified that an adjustment was needed but did not execute it. This is a process/decision failure, not a product quality issue. |
| **F-** | FAIL | The engine attempted an aggressive adjustment that requires special authorization, but no such authorization was present. This is a safety/process violation, not a product quality issue. |

**Important:** These grades measure whether the engine made the **correct engineering decision** given the input data and physical constraints—not whether the resulting garment is comfortable, attractive, or commercially viable. A 'B' grade means the system successfully handled an extreme body type by making a safe, documented trade-off within physical limits.


## Execution Notes

- The dataset has 1000 synthetic cases; the repository publishes 900 result artifacts (case IDs 0001–0600 and 0701–1000).
- Artifacts carry two generation dates: 2026-08-01 (818) and 2026-08-02 (82). The repository contains no per-run logs, so how many cases were re-run, and why, cannot be derived from it.
- Signatures are embedded in each artifact (`signature` field); there are no separate `.sig` files.
- `trust_ledger.json` lists 1000 entries; the 100 entries for cases 0601–0700 have no published artifact, so `--verify-ledger` reports FAIL until those artifacts are published.
- Observed metrics over the 900 artifacts: MSE mean 47.6 (max 169.0); ΔP mean 0.092 (max 0.161); area distortion mean 0.146 (max 0.242). Grades are decided by the decision-quality rules above, not by a numeric error threshold.

## Artifacts

- `artifacts/result_XXXX.json` — Complete Artifact (includes `artifact_hash` + `signature`)

All Artifacts are cryptographically signed by the PGEF engine and can be checked for signature validity and internal metric consistency using the public key in the parent directory. This does not constitute independent validation of physical garment performance.


## Validator

- `validator.py` — Four-layer independent validator (Hash + Signature + Schema + Metrics)
  - `python validator.py` — validates all Artifacts
  - `python validator.py --verify-ledger` — validates the Trust Ledger

The validator requires only standard Python libraries (`numpy`, `cryptography`) and does not access any proprietary engine.


## Cryptographic Authenticity

Each Artifact is signed by the PGEF engine's private key. Anyone can verify the signature using the public key:

```bash
python validator.py
```


## Production Engine Status

**PGEF v15.0 is proprietary and not publicly disclosed.**

This repository provides an **independent verification layer**—it allows anyone to verify the authenticity and consistency of published results without access to the proprietary engine.


