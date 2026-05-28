<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?SecOC / TSK

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：[secoc](/D:/Codex/secoc)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Short Version；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CAN?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：EPS?UDS；此項說明其條件、角色或判斷，技術名詞保留原文。
- 步驟：依本文件脈絡完成此項檢查或判斷。
- 重點：ECU?RAM；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：TSK?ECU；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Main Entry；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[secoc/README.md](/D:/Codex/secoc/secoc/README.md)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[secoc/extract_keys.py](/D:/Codex/secoc/secoc/extract_keys.py)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[extract_keys_main.py](/D:/Codex/secoc/extract_keys_main.py)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[secoc/shellcode/main.c](/D:/Codex/secoc/secoc/shellcode/main.c)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：[secoc/build_payload.py](/D:/Codex/secoc/secoc/build_payload.py)；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What Vehicle / ECU It Targets；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU?`0x7A1`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x7A9`?`0x7A1 + 8`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：EPS?ECU?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What The  Assumes；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：1. A known seed-key secret exists；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`SEED_KEY_SECRET = xxxxxx`；公開版不保存舊方法中的 seed secret。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：2. The firmware / application version is known；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：APP?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：RAV4；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：3. Programming-session access works；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：: What It Actually Does；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 1. Read ECU version IDs；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：ECU；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 2. Enter programming session；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：UDS?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 3. Perform Security Access；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x27`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`SEED_KEY_SECRET`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：AES；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 4. Write prerequisites for download；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：DID?`0x201`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：DID?`0x202`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：DID?`0x203`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 5. Upload a payload into RAM；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`RequestDownload`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`TransferData`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`RequestTransferExit`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：RAM?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0xFEBF0000`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x1000`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 6. Verify / arm the payload；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x10F0`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0xFF00`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 7. Payload dumps memory over CAN；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0xFEBE6E34`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0xFEBE6FF4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CAN；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CAN?`0x7A9`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Step 8. Parse dumped key structures；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x20`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x0C`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`ECU_MASTER_KEY`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`SecOC Key (KEY_4)`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：What `build_payload.py` Is Doing；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CRC；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CMAC；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：AES-CBC；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Why This  Was Attractive；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：old-secoc-tsk-method-explained；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：EPS；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：README?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Why It May Not Work For The  Project；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Relation To Our  Work；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Practical；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`secoc`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：EPS?UDS?ECU?RAM?CAN?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
