<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?v22 Feedback Modeling

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：Purpose；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`v17-v21`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`control`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x191`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`s16be_b6_7`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Script；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[control_model_v22.py](../scripts/control_model_v22.py)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Inputs；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`<LOCAL_TEMP>\toyota_v1\_control_model_v21_safe`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`*_control_rows.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`control_feedback_overlay.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`*_feedback_rows.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`report.md`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`selected_summary.json`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`control_feedback_overlay.csv`?`--feedback-signal`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`v22`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`*_lag_scores.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：What The Script Produces；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`<input_dir>/v22_out`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`aligned_feedback_rows.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`state_conditioned_feedback_regression.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_value ~ control`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b5_s8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b1`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`domain`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_deadband_bins.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`abs(control)`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_deadband_bins_by_regime.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_deadband_regime_summary.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_ar_baseline_coefficients.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_arx_coefficients.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ARX；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_model_comparison.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`??.json`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What To Look For；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. State-conditioned regression；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b5`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：2. Response deadband；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`static_ratio`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`null`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b5`?`domain`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. ARX-style model；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`feedback_t ~ control_lag_0..k + feedback_lag_1..m`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`control_lag_0`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ARX?`R^2`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Recommended  Run；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Regime / Band-Scoped Run；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--control-index-min`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--control-index-max`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--domain`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--b5-s8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--b1`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`--label`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Why This Is Better Than The Earlier v2.1 Draft；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Bottom Line；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`v22`?`0x260 -> 0x191`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
