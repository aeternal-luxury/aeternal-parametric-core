#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validator.py — Independent Validator for VS001-conformal-mapping (v6.0)

四層驗證：
- Layer 0: Artifact Integrity (hash)
- Layer 1: Cryptographic Verification (signature)
- Layer 2: Schema Verification (fields)
- Layer 3: Engineering Consistency (metrics)
支援 --verify-ledger
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

TOLERANCE = 1e-12

def verify_artifact_hash(artifact: dict) -> Tuple[bool, str]:
    """验证 artifact_hash 是否与 Artifact 内容一致"""
    data_to_hash = {k: v for k, v in artifact.items() if k not in ["artifact_hash", "signature"]}
    json_str = json.dumps(data_to_hash, sort_keys=True, separators=(",", ":"))
    computed_hash = hashlib.sha256(json_str.encode()).hexdigest()
    recorded_hash = artifact.get("artifact_hash", "")
    if computed_hash != recorded_hash:
        return False, "Hash mismatch"
    return True, "Hash OK"

def verify_signature(artifact: dict, public_key_path: Path) -> Tuple[bool, str]:
    """验证 signature（如果 cryptography 可用）"""
    if not CRYPTO_AVAILABLE:
        return False, "cryptography not available"
    if not public_key_path.exists():
        return False, "public key not found"
    try:
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())
        data_to_sign = {k: v for k, v in artifact.items() if k != "signature"}
        json_str = json.dumps(data_to_sign, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(json_str.encode()).digest()
        signature_hex = artifact.get("signature", "")
        signature = bytes.fromhex(signature_hex)
        public_key.verify(signature, digest, ec.ECDSA(hashes.SHA256()))
        return True, "Signature OK"
    except Exception as e:
        return False, f"Signature verification failed: {e}"

def verify_schema(artifact: dict) -> Tuple[bool, str]:
    required_fields = ["artifact_type", "artifact_version", "case_id", "input", "garment", "metrics", "status", "metadata", "artifact_hash", "signature"]
    for field in required_fields:
        if field not in artifact:
            return False, f"Missing field: {field}"
    if artifact.get("artifact_type") != "PGEF_Validation_Result":
        return False, "artifact_type invalid"
    if artifact.get("status") not in ["PASS", "FAIL"]:
        return False, "status invalid"
    return True, "Schema OK"

def recompute_metrics(input_data: dict, garment_data: dict) -> dict:
    input_vector = np.array([
        float(input_data.get("shoulder_width", 0.0)),
        float(input_data.get("chest", 0.0)),
        float(input_data.get("waist", 0.0)),
        float(input_data.get("arm_length", 65.0))
    ], dtype=float)
    output_vector = np.array([
        float(garment_data.get("garment_shoulder", input_data.get("shoulder_width", 0.0))),
        float(garment_data.get("garment_chest", input_data.get("chest", 0.0))),
        float(garment_data.get("garment_waist", input_data.get("waist", 0.0))),
        float(garment_data.get("garment_arm", input_data.get("arm_length", 65.0)))
    ], dtype=float)
    mse = float(np.mean((input_vector - output_vector) ** 2))
    norm_input = np.linalg.norm(input_vector)
    delta_p = 0.0 if norm_input < 1e-10 else float(np.linalg.norm(input_vector - output_vector) / norm_input)
    input_area = float(input_data.get("chest", 0.0)) * float(input_data.get("waist", 0.0)) * 0.5
    output_area = float(garment_data.get("garment_chest", input_data.get("chest", 0.0))) * float(garment_data.get("garment_waist", input_data.get("waist", 0.0))) * 0.5
    area_distortion = 0.0 if input_area < 1e-10 else abs(output_area - input_area) / input_area
    return {"mse": mse, "delta_p": delta_p, "area_distortion": area_distortion}

def verify_metrics(artifact: dict) -> Tuple[bool, str]:
    recomputed = recompute_metrics(artifact["input"], artifact["garment"])
    recorded = artifact["metrics"]
    mismatches = []
    for key in ["mse", "delta_p", "area_distortion"]:
        if abs(recomputed.get(key, 0.0) - float(recorded.get(key, 0.0))) > TOLERANCE:
            mismatches.append(f"{key}: recorded {recorded.get(key):.2e}, recomputed {recomputed.get(key):.2e}")
    if mismatches:
        return False, "; ".join(mismatches)
    return True, "Metrics OK"

def verify_trust_ledger(ledger_path: Path, artifacts_dir: Path) -> Tuple[bool, str]:
    if not ledger_path.exists():
        return False, "Trust Ledger not found"
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    entries = ledger.get("entries", [])
    if not entries:
        return False, "No entries in ledger"
    mismatches = []
    for entry in entries:
        case_id = entry.get("case_id")
        rec_hash = entry.get("artifact_hash", "")
        artifact_path = artifacts_dir / f"result_{case_id}.json"
        if not artifact_path.exists():
            mismatches.append(f"Case {case_id}: artifact missing")
            continue
        with open(artifact_path, "r", encoding="utf-8") as af:
            artifact = json.load(af)
        if artifact.get("artifact_hash", "") != rec_hash:
            mismatches.append(f"Case {case_id}: hash mismatch")
    if mismatches:
        limit = 3
        preview = "; ".join(mismatches[:limit])
        rest = max(0, len(mismatches) - limit)
        return False, preview + (f" ... and {rest} more" if rest else "")
    return True, f"Ledger OK ({len(entries)} artifacts)"

def main():
    args = sys.argv[1:]
    if "--verify-ledger" in args:
        ledger_path = Path(__file__).parent.parent / "trust_ledger.json"
        artifacts_dir = Path(__file__).parent / "artifacts"
        ok, msg = verify_trust_ledger(ledger_path, artifacts_dir)
        print(f"Trust Ledger verification: {'OK' if ok else 'FAIL'} — {msg}")
        sys.exit(0 if ok else 1)

    # load public key if available
    public_key_path = Path(__file__).parent.parent / "public_key.pem"
    has_pub = public_key_path.exists()
    # iterate artifacts
    artifacts_dir = Path(__file__).parent / "artifacts"
    if not artifacts_dir.exists():
        print(f"Artifacts directory not found: {artifacts_dir}")
        sys.exit(1)
    files = sorted(artifacts_dir.glob("result_*.json"))
    if not files:
        print("No artifacts found")
        sys.exit(1)

    passed = 0
    failed = 0
    for p in files:
        with open(p, "r", encoding="utf-8") as f:
            artifact = json.load(f)
        case_id = artifact.get("case_id", p.stem.replace("result_", ""))
        ok_hash, msg_hash = verify_artifact_hash(artifact)
        ok_sig, msg_sig = verify_signature(artifact, public_key_path) if has_pub and CRYPTO_AVAILABLE else (False, "signature check skipped")
        ok_schema, msg_schema = verify_schema(artifact)
        ok_metrics, msg_metrics = verify_metrics(artifact)
        all_ok = ok_hash and ok_sig and ok_schema and ok_metrics
        if all_ok:
            passed += 1
            print(f"✅ {p.name}: OK")
        else:
            failed += 1
            reasons = [m for m in (msg_hash if not ok_hash else None, msg_sig if not ok_sig else None, msg_schema if not ok_schema else None, msg_metrics if not ok_metrics else None) if m]
            print(f"❌ {p.name}: {'; '.join(reasons)}")
    print(f"Summary: total={len(files)} pass={passed} fail={failed}")
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
