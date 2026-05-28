<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?Replay-Backed Transition / Settle Shaping Hypothesis

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：Purpose；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：`decode_mode = no_b1_flip`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`mode = identity`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`slew ~= 175`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[replay-backed-simulation-round6.md](./replay-backed-simulation-round6.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[replay-backed-simulation-round6-regime-read.md](./replay-backed-simulation-round6-regime-read.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[replay-backed-city-late-stop-triad.md](./replay-backed-city-late-stop-triad.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Problem Statement；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What Makes Transition / Settle Hard；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`transition / settle`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 步驟：依本文件脈絡完成此項檢查或判斷。
- 重點：Main Hypothesis；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`legacy_ff_negative`?`no_b1_flip`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`bounded`?`identity`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Shaping Hypotheses；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Hypothesis A: Deep-negative compression needs a different effective response；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Hypothesis B: Low-amplitude settle needs a softer local response；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Hypothesis C: Transition windows may need two-phase shaping；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What I Do Not Think Is The Main Hypothesis；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Not primarily a final-hold problem；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Not primarily a bounded-vs-identity problem；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`identity`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Not primarily a legacy decode problem；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`no_b1_flip`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Recommended Experiment Order；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 1；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`no_b1_flip`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`identity`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 2；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 3；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 4；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Acceptance Standard；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：MAE；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`p95`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Bottom Line；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
