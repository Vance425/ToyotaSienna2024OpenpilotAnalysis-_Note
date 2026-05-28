<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?CodexCliAgent Sim

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：codexcliagent-sim-review；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[control_simulator.py](/D:/Codex/toyota-sienna-tsk-analysis/CodexCliAgent/ToyotaSienna2024OpenpilotAnalysis/sim/control_simulator.py)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[extract_real_slew.py](/D:/Codex/toyota-sienna-tsk-analysis/CodexCliAgent/ToyotaSienna2024OpenpilotAnalysis/sim/extract_real_slew.py)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[simulation_report.md](/D:/Codex/toyota-sienna-tsk-analysis/CodexCliAgent/ToyotaSienna2024OpenpilotAnalysis/sim/simulation_report.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`sim/`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：Overall Judgment；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`sim/`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What Is Useful；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. It encodes a clear experimental hypothesis；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`289`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`-760`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`7981`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：2. It separates mapping from slew limiting；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. `extract_real_slew.py` is directionally useful；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What Is Too Strong or Too Early；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. The direct `[-1, 1] -> raw setpoint` mapping is still a working assumption；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`control_simulator.py`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`[289, 7981]`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`[-760, 289]`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：2. `slew_limit = 50` is not yet justified as a validated operational limit；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`slew_limit = 50`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ACU；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. `extract_real_slew.py` uses an over-strong decode rule；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`return res if b1 == 0 else -res`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`B2/B3 + signed(B5)`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`B1`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：4. The simulation report overclaims；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[simulation_report.md](/D:/Codex/toyota-sienna-tsk-analysis/CodexCliAgent/ToyotaSienna2024OpenpilotAnalysis/sim/simulation_report.md)?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Concrete Technical Weaknesses；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`control_simulator.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：PNG?`/home/vance/...`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`extract_real_slew.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`20260312_190101_000`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b1 == 0 else negative`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`simulation_report.md`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`integration_mapping_report.md`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Best  Use；此項說明其條件、角色或判斷，技術名詞保留原文。
- 步驟：依本文件脈絡完成此項檢查或判斷。
- 重點：Recommended Next Step；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`190101`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`171414`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`184921`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`20260418`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`20260426`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Bottom Line；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
