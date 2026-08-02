# AETERNAL Engineering Trust Framework

> **Cryptographically Verifiable Engineering Trust** — 密碼學可驗證的工程信任框架

## 概述

本仓库是 AETERNAL PGEF v15.0 的官方信任框架，定位为 **工程信任框架 (Engineering Trust Framework)**。

**核心设计原则**：
- 每个输出是一个**不可变的工程工件 (Artifact)**
- 每个 Artifact 包含 Input + Output + Metrics + Hash + Signature
- **生产引擎 PGEF v15.0 为专有技术，不对外公开**
- 任何人可用公開金鑰驗證 Artifact 的真實性與完整性
- Trust Ledger 記錄所有 Artifact 的審計鏈條

## 五层信任架构 (Five-Layer Trust Architecture)
- Layer 5: Trust Ledger (TRUST_LEDGER.md / trust_ledger.json)
- Layer 4: Attestation (public_key.pem + validator.py 簽名驗證)
- Layer 3: Artifacts (artifacts/result_XXXX.json + .sig)
- Layer 2: Validator (validator.py)
- Layer 1: Specification (specification.md)

## 快速开始

```bash
git clone https://github.com/aeternal-luxury/aeternal-parametric-core
cd aeternal-parametric-core/pgef-validation
cd VS001-conformal-mapping
# 验证所有 Artifact
python validator.py
# 验证 Trust Ledger
python validator.py --verify-ledger
```
