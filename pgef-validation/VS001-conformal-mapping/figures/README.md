# Figures — VS001 視覺化圖表

本目錄包含 VS-001 驗證結果的視覺化圖表，用於直觀展示 repo 公開的 1000 個 artifacts 的分佈（資料集 1000 組、帳本 1000 筆）。圖表由 `reproduction/summarize_artifacts.py --figures` 重新產生。

## 圖表清單

| 檔名 | 描述 |
|---|---|
| `validation_report.png` | 驗證報告總圖（包含多個子圖的合併圖表） |
| `mse_distribution.png` | MSE（均方誤差）分佈直方圖 |
| `pass_fail.png` | PASS/FAIL 分佈餅圖 |

## 圖表用途

- **validation_report.png**：一頁總結，方便快速瀏覽整體驗證結果（MSE 分佈、面積畸變率分佈、PASS/FAIL 比例、ΔP 分佈等）。
- **mse_distribution.png**：展示所有案例的 MSE 分佈，用於判斷數值收斂是否穩定。
- **pass_fail.png**：顯示公開 artifacts 的等級分布（全部為 PASS）。

## 規範

- 所有圖表解析度 ≥ 300 DPI
- 格式：PNG
- 圖表標題、軸標籤、圖例完整