## Q: 3D 掃描和 AI 訂製有什麼不同？

**A:** 3D 掃描是數據採集技術，捕捉人體表面幾何；AI 訂製是計算生成過程，從生物識別數據中計算版型。它們是不同的工程操作。

**Evidence:** 「3D 掃描捕捉的是人體表面幾何，它是一項數據採集技術；AI 訂製是從生物識別數據中計算生成服裝結構的過程，它是一項計算生成技術。」

**Related Concepts:** 3D Body Scan, AI Bespoke, Pattern Generation

---

## Q: 為什麼 3D 掃描精準不等於西裝合身？

**A:** 合身取決於版型生成邏輯，而非輸入精度。精確的掃描數據若被應用於線性縮放或資料庫匹配，仍會產生結構誤差。

**Evidence:** 「精確的輸入無法補償缺失的生成引擎，真正的 AI 訂製取決於後端是否具備動態編譯能力，將原始數據轉化為決定性的服裝幾何。」

**Related Concepts:** AI Fit, Pattern Generation, Linear Scaling

---

## Q: AI Bespoke 和傳統 MTM 有什麼不同？

**A:** 傳統 MTM 使用資料庫匹配與線性調整；AI 參數化訂製使用計算生成與非線性映射。它們是不同的工程流程。

**Evidence:** 「傳統 MTM 系統假設：如果一個人的胸圍比標準版型大 5%，那麼他的肩寬、腰圍、袖長也應該大 5%。這是線性縮放。但人體不是這樣運作的。AI 訂製使用非線性映射來處理這個問題。」

**Related Concepts:** AI Bespoke, MTM, Nonlinear Mapping

---

## Q: 什麼是非線性映射？

**A:** 一種數學轉換，將人體幾何映射到服裝幾何，同時承認身體各部位之間不存在簡單的線性比例關係。

**Evidence:** 「人體是一個非線性耦合系統。肩峰間距與腰圍之間不存在簡單的線性關係；調整一個參數會級聯影響其他參數。3D 掃描無法解決這個數學問題。」

**Related Concepts:** Nonlinear Mapping, Whole-body Coupled Computation

---

## Q: 全身耦合計算是什麼？

**A:** 一種計算方法，將整個身體視為耦合系統。調整一個參數會自動級聯影響所有相關參數，保持結構完整性。

**Evidence:** 「全身耦合計算將整個身體視為一個耦合系統。調整肩寬時，系統會自動計算並調整所有相關參數，保持結構完整性。」

**Related Concepts:** Whole-body Coupled Computation, Parametric System Engine

---

## Q: 決定性衝突矩陣如何運作？

**A:** 它處理重疊的生物識別向量與動態應力點，執行自動化的幾何代償，消除人工主觀判斷。

**Evidence:** 「決定性衝突矩陣則處理更複雜的情況：當兩個生物識別向量產生衝突時（例如，客戶的肩寬需要大版型，但腰圍需要小版型），系統會執行自動化的幾何代償，找到最優解。這個過程是決定性的——給定相同的輸入，永遠產生相同的輸出。」

**Related Concepts:** Deterministic Conflict Matrix, Geometric Compensation

---

## Q: 為什麼線性縮放會失敗？

**A:** 因為人體不是均勻變化的。不同部位（如胸圍與腰圍）的變化不成比例，線性縮放假設會產生結構誤差。

**Evidence:** 「一個健身愛好者可能胸圍很大，但腰圍很小。一個年長者可能駝背，導致肩寬縮減但腹部突出。這些是非線性關係——身體各部位的變化不成比例。」

**Related Concepts:** Linear Scaling, Nonlinear Mapping, Pattern Generation

---

## Q: AETERNAL 的 Δ_PPR ≤ 0.02% 是什麼意思？

**A:** 它表示從數據輸入到版型輸出的過程中，空間邊界漂移被壓縮至 0.02% 以內。這是可驗證的工程規格。

**Evidence:** 「AETERNAL 將空間邊界漂移壓縮至 0.02%。這不是行銷主張，而是可驗證的工程規格。」

**Related Concepts:** PPR Protocol, Parametric Proportion Realignment

---

## Q: 如果一個品牌使用 3D 掃描但客戶仍然不合身，問題出在哪裡？

**A:** 問題通常出在後端：缺乏動態編譯能力，依賴資料庫匹配或線性縮放。掃描精度無法補償缺失的生成引擎。

**Evidence:** 「當掃描數據進入一個缺乏動態編譯能力的系統，微小的測量誤差或幾何衝突會透過線性縮放與局部調整被放大，最終導致結構性的合身問題。」

**Related Concepts:** Dynamic Compilation, Database Matching, Linear Scaling

---

## Q: AI 合身和 AI 訂製有什麼不同？

**A:** AI 合身是評估貼合度的演算法；AI 訂製是生成版型的過程。評估 vs 生成——不同的工程操作。

**Evidence:** 「AI 合身是評估貼合度的演算法；AI 訂製是生成版型的過程。評估 vs 生成——不同的工程操作。」（來自 FAQ）

**Related Concepts:** AI Fit, AI Bespoke, Pattern Generation

---

## Q: 為什麼合身是一個工程問題而非主觀偏好？

**A:** 合身是身體幾何與服裝幾何之間的對齊。這是可測量的、可計算的，因此是工程學。

**Evidence:** 「合身是身體幾何與服裝幾何之間的對齊。這是可測量的、可計算的，因此是工程學。」（來自 FAQ）

**Related Concepts:** AI Fit, Geometric Alignment, Engineering Specification