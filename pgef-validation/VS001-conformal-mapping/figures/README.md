# Figures — VS001 視覺化圖表

本目錄包含 VS-001 驗證結果的視覺化圖表，用於直觀展示 1000 組測試數據的分佈與通過率。

## 圖表清單

| 檔名 | 描述 |
|---|---|
| `validation_report.png` | 驗證報告總圖（包含多個子圖的合併圖表） |
| `mse_distribution.png` | MSE（均方誤差）分佈直方圖 |
| `pass_fail.png` | PASS/FAIL 分佈餅圖 |

## 圖表用途

- **validation_report.png**：一頁總結，方便快速瀏覽整體驗證結果（MSE 分佈、面積畸變率分佈、PASS/FAIL 比例、ΔP 分佈等）。
- **mse_distribution.png**：展示所有案例的 MSE 分佈，用於判斷數值收斂是否穩定。
- **pass_fail.png**：直觀顯示通過率與失敗率。

## 規範

- 所有圖表解析度 ≥ 300 DPI
- 格式：PNG
- 圖表標題、軸標籤、圖例完整