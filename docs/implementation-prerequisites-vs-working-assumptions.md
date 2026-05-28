<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?implementation-prerequisites-vs-working-assumptions

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：Purpose；此項說明其條件、角色或判斷，技術名詞保留原文。
- 步驟：依本文件脈絡完成此項檢查或判斷。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：[openpilot-control-side-working-note.md](./openpilot-control-side-working-note.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[OPENPILOT_INTEGRATION_PROGRESS_REPORT.md](../OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[current-findings-summary-v2.md](./current-findings-summary-v2.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. Strong Enough To Treat As  Prerequisites；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：A. The passive backbone must remain primary；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x116 / 0x131 / 0x2E4`?`TSK-nearest`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：B. `0x260` is the control-side anchor；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x191`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x371`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：C. The current best replay branch is the default comparison branch；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`decode_mode = no_b1_flip`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`mode = identity`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`higher slew`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`bounded`?`legacy_ff_negative`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：D. City transition/settle is a special regime；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`transition / settle`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：E. The city-side local working rule is real enough to retain；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`low-band catch-up 5.5x`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`deeper-negative helper 2.5x`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：2. Still Only Replay-Backed；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：A.  normalized control mapping；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：B.  slew limits；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`175`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：C. Operational use of `0x2E4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x2E4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：D.  universality；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：E. Injection readiness；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. What Is Strong Enough For Planning, But Not For；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`VIRTUAL_TSK_SPEC_v2`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：4. Practical Rule For Future Work；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Level 1: backbone / prerequisite；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x116 / 0x131 / 0x2E4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Level 2: replay-backed working assumption；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Level 3: implementation-grade claim；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：5.  Short Read；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Bottom Line；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`no_b1_flip + identity + higher slew`；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
