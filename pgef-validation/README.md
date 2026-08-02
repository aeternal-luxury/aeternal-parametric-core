# VS001-conformal-mapping: Conformal Mapping Validation

> **測試結論**：PGEF v15.0 引擎已完成 1000 組極端體型壓力測試，通過率 100%，所有結果可公開驗證。

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

## Artifacts

- `artifacts/result_XXXX.json` — Complete Artifact (includes `artifact_hash` + `signature`)
- `artifacts/result_XXXX.json.sig` — Detached signature file

All Artifacts are cryptographically signed by the PGEF engine and can be independently verified using the public key in the parent directory.


## Validator

- `validator.py` — Four-layer independent validator (Hash + Signature + Schema + Metrics)
  - `python validator.py` — validates all Artifacts
  - `python validator.py --verify-ledger` — validates the Trust Ledger

The validator requires only standard Python libraries (`numpy`, `cryptography`) and does not access any proprietary engine.


## Trust Ledger

The root `trust_ledger.json` (in `pgef-validation/`) records all Artifacts in a single, immutable ledger. The `--verify-ledger` flag checks consistency across all entries.


## Cryptographic Authenticity

Each Artifact is signed by the PGEF engine's private key. Anyone can verify the signature using the public key:

```bash
python validator.py
```


## Production Engine Status

**PGEF v15.0 is proprietary and not publicly disclosed.**

This repository provides an **independent verification layer**—it allows anyone to verify the authenticity and consistency of published results without access to the proprietary engine.

