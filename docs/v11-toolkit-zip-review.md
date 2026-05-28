<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?v11 Toolkit ZIP

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：`<LOCAL_USER_HOME>\Downloads\toyota_reverse_toolkit_v11.zip`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What It Contains；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ZIP?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`core/`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`validation/`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`backends/`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`cli/`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`core/frame_types.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`core/counters.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`core/checksums.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`validation/lkas_builder.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`validation/torque_sweep.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`backends/dryrun_backend.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`backends/socketcan_backend.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`backends/panda_backend.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`cli/build_frame.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`cli/inject_socketcan.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`cli/inject_panda.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`cli/torque_sweep_test.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What It Can Do；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. Build candidate frames；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CAN；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：2. Increment a simple counter；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`CounterEngine`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. Apply simple checksums；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`ChecksumEngine`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`sum8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`sum8_inv`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`xor8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`sum_low_nibble`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CRC8?`crc8.py`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：4. Send frames by backend；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：5. Run torque sweep experiments；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CLI?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What It Is Good For；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：LKAS；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260 / 0x2E4 / 0x115 / 0xD8 / 0x131`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What It Cannot Do Yet；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Why It Is Not Enough By Itself；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Best Practical Use；此項說明其條件、角色或判斷，技術名詞保留原文。
- 步驟：依本文件脈絡完成此項檢查或判斷。
- 重點：Recommendation；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
