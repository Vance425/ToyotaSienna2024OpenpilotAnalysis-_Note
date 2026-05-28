<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?Replay-backed simulation

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：Purpose；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`CodexCliAgent/.../sim`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：`TSK`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Inputs；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Hypothesis source；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[control_simulator.py](/D:/Codex/toyota-sienna-tsk-analysis/CodexCliAgent/ToyotaSienna2024OpenpilotAnalysis/sim/control_simulator.py)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[extract_real_slew.py](/D:/Codex/toyota-sienna-tsk-analysis/CodexCliAgent/ToyotaSienna2024OpenpilotAnalysis/sim/extract_real_slew.py)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[codexcliagent-sim-review.md](./codexcliagent-sim-review.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Core working assumptions to test；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`289`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`7981`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`-760`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Representative Replay Set；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Backbone / anchor-side；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[toyota_seg_IGN_ON_20260315_171414_000.ndjson](../logs/toyota_seg_IGN_ON_20260315_171414_000.ndjson)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[toyota_seg_IGN_ON_20260311_184921_000.ndjson](../logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：City / control-side；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[toyota_all_20260418_163135_000.ndjson](../logs/toyota_all_20260418_163135_000.ndjson)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[toyota_all_20260418_175240_000.ndjson](../logs/toyota_all_20260418_175240_000.ndjson)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Entry-side / partial-seed follow-up；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Phase 1: Decode and Window Extraction；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：replay-backed-simulation-plan；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Required outputs；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Important caution；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`B1`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Phase 2: Mapping Replay；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Experiment；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`[-1, 1]`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Metrics；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Desired；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Phase 3: Slew Replay；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`10`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`25`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`50`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`75`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`100`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Phase 4: Regime Split；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：by class；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`20260426`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Questions；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Phase 5: Decision Output；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. Promising but still hypothesis-grade；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：2. Stable enough for continued offline integration work；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. Invalid as current formulation；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Deliverables；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`mapping_replay_summary.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`slew_replay_summary.csv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`regime_split_simulation_report.md`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What Counts as Success；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Bottom Line；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`sim/`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
