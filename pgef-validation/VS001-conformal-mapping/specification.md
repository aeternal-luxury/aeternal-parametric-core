# VS001-conformal-mapping: Conformal Mapping Validation


## Evidence Tree

> **How do you verify geometric convergence?**
>
> **How do you verify that published engineering results were genuinely produced by the production engine?**


## Claims Covered

This validation standard verifies the following claims:

| Claim | Description |
|---|---|
| **Claim A** | **Proportional consistency**: The relationship between key garment dimensions (waist and shoulder) falls within the brand's defined aesthetic tolerance, unless constrained by physical limits. |
| **Claim B** | **Physical boundary compliance**: Garment dimensions respect anatomical and structural limits defined in the engineering specification. |
| **Claim C** | **Formula adherence**: All derived garment dimensions (length, sleeve, chest ease, etc.) match the values computed from the specification-defined formulas. |
| **Claim D** | **Adaptive logic**: The engine correctly detects and activates specialized compensation modes for extreme body types. |
| **Claim E** | **Inverse fitting**: When dimensional relationships deviate from targets, the engine attempts corrective adjustments (expanding shoulder width, reducing waist) within the limits of the physical boundary. |


## Evidence Matrix

| Claim | Evidence Artifact | Validation Method |
|---|---|---|
| **Claim A** | `result_XXXX.json` → `garment_waist`, `garment_shoulder` | `validator.py` Layer 3 (Engineering Consistency) |
| **Claim B** | `result_XXXX.json` → `garment_shoulder`, `input.height` | `validator.py` Layer 3 (Engineering Consistency) |
| **Claim C** | `result_XXXX.json` → all `garment_*` fields | `validator.py` Layer 3 (Engineering Consistency) |
| **Claim D** | `result_XXXX.json` → `status`, `grade` | `determine_pass_fail` logic |
| **Claim E** | `result_XXXX.json` → `garment_shoulder`, `garment_waist` | `validator.py` Layer 3 (Engineering Consistency) |


## Validation Methodology

This validation standard employs a **Cryptographically Verifiable Engineering Evidence Framework**:

1. **Artifact Integrity**: Each Artifact (`result_XXXX.json`) contains an `artifact_hash` (SHA-256), ensuring the content has not been tampered with.
2. **Cryptographic Signature**: Each Artifact is signed by the PGEF engine's private key (ECDSA-secp256k1). Anyone can verify its authenticity using the public key.
3. **Schema Verification**: Ensures all Artifacts have complete JSON structure with required fields: input, garment, metrics, metadata.
4. **Engineering Consistency**: Recomputes MSE, ΔP, and area distortion from input and garment, then compares against recorded values to ensure self-consistency.


## Validator Logic

`validator.py` executes four layers of validation:

- **Layer 0 (Artifact Integrity)**: Verifies `artifact_hash` matches Artifact content
- **Layer 1 (Cryptographic Verification)**: Verifies ECDSA signature, confirming Artifact came from PGEF Engine
- **Layer 2 (Schema Verification)**: Checks JSON format and field completeness
- **Layer 3 (Engineering Consistency)**: Recomputes metrics (MSE, ΔP, area distortion) and compares with recorded values

The validator depends only on standard Python libraries (`numpy`, `cryptography`) and does not access any proprietary engine.


## PASS/FAIL Grade Definitions

| Grade | Status | Condition | Meaning |
|---|---|---|---|
| **A++** | PASS | Exceeds target (raw ratio already ≤ 0.720, or garment ratio ≤ 0.718) | Beyond brand aesthetic standard — natural advantage or system excellence |
| **A+** | PASS | Garment waist-to-shoulder ratio precisely achieves target (within tolerance) and no physical boundary was reached | System precisely achieved the aesthetic target |
| **A** | PASS | Physical boundary reached, safe path executed, minor compromise | System made a safe decision at physical limits |
| **B** | PASS | Physical boundary reached, safe path executed, significant compromise | Extreme body type, physical limits caused significant deviation |
| **F** | FAIL | Waist-to-shoulder ratio out of range, but physical boundary was not reached | System should have executed inverse fitting but did not — process/decision failure |
| **F-** | FAIL | Aggressive path executed without authorization | System executed a safety-critical operation without consent |


## Validation Results Summary

The dataset contains 1000 synthetic body-type records. The repository publishes 900 result artifacts (case IDs 0001–0600 and 0701–1000).

- **Published artifacts**: 900
- **PASS**: 900 (100.0%)
- **FAIL**: 0 (0.0%)
- **Grade distribution**:
  - A++: 0 (0.0%)
  - A+: 54 (6.0%)
  - A: 180 (20.0%)
  - B: 666 (74.0%)
  - F: 0 (0.0%)
  - F-: 0 (0.0%)

`trust_ledger.json` lists 1000 entries (A+ 61, A 202, B 737). The 100 entries for cases 0601–0700 have no published artifact, so they cannot be checked from this repository and `validator.py --verify-ledger` reports FAIL.

**Scope**: the published artifacts pass `validator.py` (hash, signature, schema, metric consistency: 900/900). This is an internal-consistency check of engine output against its own specification on synthetic data. It is not physical-garment validation and not independent third-party validation.

## Execution Notes

- The dataset has 1000 synthetic cases; the repository publishes 900 result artifacts (case IDs 0001–0600 and 0701–1000).
- Artifacts carry two generation dates: 2026-08-01 (818) and 2026-08-02 (82). The repository contains no per-run logs, so how many cases were re-run, and why, cannot be derived from it.
- Signatures are embedded in each artifact (`signature` field); there are no separate `.sig` files.
- `trust_ledger.json` lists 1000 entries; the 100 entries for cases 0601–0700 have no published artifact, so `--verify-ledger` reports FAIL until those artifacts are published.
- Observed metrics over the 900 artifacts: MSE mean 47.6 (max 169.0); ΔP mean 0.092 (max 0.161); area distortion mean 0.146 (max 0.242). Grades are decided by the decision-quality rules above, not by a numeric error threshold.

## Dependencies

- No external dependencies (`validator.py` only uses standard libraries)
- Public key `public_key.pem` is in the root directory
- Trust Ledger `trust_ledger.json` is in the root directory


