<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?v12 Toolkit

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：`<LOCAL_TEMP>\20260312\tools\toyota_reverse_toolkit_v12.zip`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Executive；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`v12`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`v11`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：LKAS；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CAN；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：NDJSON；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What It Can Do；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. Build/inject candidate frames；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：2. Active scan for candidate steering/LKAS frames；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`scanner/steering_frame_scanner.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. Fuzz selected bytes；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`cli/fuzz_can.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`fuzzer/toyota_can_fuzzer.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：4. Offline SecOC heuristics on NDJSON logs；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`cli/secoc_detect.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`secoc/secoc_detector.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What Is Actually Useful For Your Project；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`secoc_detect`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`fuzz_can`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`scan_lkas`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What Is Weak Or Limited；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：README quality；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`README.md`?`v11`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：README；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`secoc_detect` is heuristic, not deep reverse logic；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`scan_lkas` is very brute-force；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Main；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Best Practical Use Order；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`build_frame`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`torque_sweep_test --backend dryrun`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 步驟：依本文件脈絡完成此項檢查或判斷。
- 重點：Bottom Line；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`v12`?`v11`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
