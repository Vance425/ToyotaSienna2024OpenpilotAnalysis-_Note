<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?SecOC

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：TSK?[secoc](/D:/Codex/secoc)?`2024 Sienna`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：Short Answer；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：UDS?`SecurityAccess`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`SEED_KEY_SECRET`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 步驟：依本文件脈絡完成此項檢查或判斷。
- 重點：Assessment；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. ECU address / target assumption (`0x7A1`)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU?`0x7A1`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU?EPS；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`EPS`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`2024 Sienna`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：2. APP / bootloader version gate；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：APP；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`2024 Sienna`?APP；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. Direct diagnostic session path (`default -> extended -> programming`)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ISO-TP?UDS?`seed/key`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[toolkit-v5-v10-final-summary.md](./toolkit-v5-v10-final-summary.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[tsk-nearest-evidence-summary.md](./tsk-nearest-evidence-summary.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：4. Hardcoded `SEED_KEY_SECRET`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：5. DID writes (`0x201`, `0x202`, `0x203`) and download prerequisites；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：6. `RequestDownload / TransferData / RequestTransferExit` path；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU?RAM；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：7. Payload verification / routine control (`0x10F0`, `0xFF00`)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：8. Payload shellcode compatibility；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CAN；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：9. Dump memory range (`0xFEBE6E34 -> 0xFEBE6FF4`)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：10. Key structure parsing (`KEY_1`, `KEY_4`, offsets, checksum)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x20`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`KEY_4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What Probably Still Has Value；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：A. It identifies the old target area of interest；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：EPS-?ECU；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：RAM；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：B. It shows what a successful direct path would need；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：C. It tells us what kind of  would be needed to revive it；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What This Means For The  Project；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Ranking；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Most likely still usable only as hypothesis；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU?`0x7A1`?EPS；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Most likely already broken；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：DID；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Bottom line；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：EPS?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
