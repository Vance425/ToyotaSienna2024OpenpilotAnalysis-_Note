<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?`0x260` vs `0xD8` Decision Note

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：[0x260-byte-role-memo.md](./0x260-byte-role-memo.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[0xD8-nibble-checksum-memo.md](./0xD8-nibble-checksum-memo.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[current-findings-summary-v2.md](./current-findings-summary-v2.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Question；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0xD8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Short Answer；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Why `0x260` Stays Primary；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. It still looks more like the main command family；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b1-b2`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：2. It is more tightly aligned with earlier lifecycle work；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x131`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x116`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0xD8`?`0x260`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. The current problem with `0x260` is layout, not role；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：Why `0xD8` Does Not Replace It；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. `0xD8` is cleaner, but cleaner is not the same as primary；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b7`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：2. `0xD8` looks more like an auxiliary structured-control line；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b2-b3`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`b5-b6`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. It is better used as a reference than as a replacement；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0xD8`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Practical Split Going Forward；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Main reverse target；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Main structural reference；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Protected-family；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x2E4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Decision；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
