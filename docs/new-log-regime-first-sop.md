<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?New Log Regime- SOP

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：[current-findings-summary-v2.md](./current-findings-summary-v2.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[final-frame-role-map.md](./final-frame-role-map.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[log-phenomenon-map-template.md](./log-phenomenon-map-template.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[v22-band-filter-presets.md](./v22-band-filter-presets.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Purpose；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：SOP?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 1: Identify Session Type；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：ADAS；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 2: Build A Phenomenon；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`seed-heavy`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`plateau-heavy`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`boundary-rich`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`ADAS-on stable`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`ADAS-off stable`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`mixed`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`invalid`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 3: Read The Core Frames；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x131`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x116`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0xD8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x191`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 4: Choose The `0x191` Field By Regime；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x191`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0311`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x191.b6-b7`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0316`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x191.b4-b5`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 5: Exclude Mixed Bands；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x131 / 0x116 / 0xD8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ACC；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[20260312-190101-disengage-suspect-bands.md](./20260312-190101-disengage-suspect-bands.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[20260314-175006-second-disengage-suspect.md](./20260314-175006-second-disengage-suspect.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260.b5_s8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260.b4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`disengage suspect`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`lane-change transition`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[20260314-175006-lane-change-transition-candidate.md](./20260314-175006-lane-change-transition-candidate.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[20260315-175912-lane-change-transition-secondary.md](./20260315-175912-lane-change-transition-secondary.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[20260315-171414-lane-change-transition-third-support.md](./20260315-171414-lane-change-transition-third-support.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 6: Run Local `v22`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[run_v22_band_presets.ps1](../scripts/run_v22_band_presets.ps1)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[run_v22_band_presets.sh](../scripts/run_v22_band_presets.sh)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`control_model_v22.py`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--control-index-min`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--control-index-max`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--domain`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--b5-s8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--b1`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--label`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 7: Evaluate The Output Correctly；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`??.json`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`state_conditioned_feedback_regression.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_model_comparison.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_deadband_regime_summary.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 8: Update The Log；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Concrete City Example；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`2026-04-18`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[session-review-20260418-two-city-runs.md](./session-review-20260418-two-city-runs.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[session-review-20260418-active-slice-local-bands.md](./session-review-20260418-active-slice-local-bands.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[session-review-20260418-band4-core-read.md](./session-review-20260418-band4-core-read.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[session-review-20260418-late-stop-local-bands.md](./session-review-20260418-late-stop-local-bands.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`16:33:06`?`16:33:36`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`18:10:11`?`18:10:41`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`18:11:11`?`18:11:41`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b6-b7`?`0311`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b6-b7`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Default Rule；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Bottom Line；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
