# Validation Verification Guide: VS001-conformal-mapping

验证步骤:
1) 安装依赖: pip install numpy cryptography
2) 运行验证器: python validator.py
3) 验证 Trust Ledger: python validator.py --verify-ledger

预期:
- 所有 Artifact 通過驗證
- Trust Ledger 與 Artifact Hash 一致
