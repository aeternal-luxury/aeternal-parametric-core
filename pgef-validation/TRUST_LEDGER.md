# Trust Ledger

Trust Ledger 是一份公開的信任帳本，記錄所有工程工件 (Artifact) 的關鍵資訊：
- 每個 Artifact 的 Hash
- 每個 Artifact 的簽名
- 引擎版本、數據集版本、驗證器版本

使用方式：
cd VS001-conformal-mapping
python validator.py --verify-ledger
