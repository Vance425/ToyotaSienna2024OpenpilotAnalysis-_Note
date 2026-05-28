<!-- 中文化說明：本文件已轉為中文閱讀版；技術名詞保留原文。 -->
# 中文文件?2026-05-22 Toyota Sienna SecOC Steering  Milestone

## 文件定位
本文件屬於研究庫，用於記錄分析、判斷與後續整理。

## 關鍵重點
- 重點：Purpose；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`LKAS Failure`?`0x2E4 / STEERING_LKA`?`0x131 / STEERING_LTA_2`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Executive；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x2E4`?`STEERING_LKA`?LKA?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x2E4`?CAN?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：DATAFLASH?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：C3X?`SecOCKey`?`sendcan`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Timeline And Milestones；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 1 - LKAS Failure Symptom；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`carState`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`latActive=False`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`longActive=False`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`actuators.torqueOutputCan=0`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：此項描述分析條件、觀察結果或後續動作，已整理為中文。
- 重點：`steerFaultTemporary`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`steerFaultPermanent=True`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`canValid=True`?`canErrorCounter=0`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：CAN?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 2 - `carControl` Showed No Active Steering；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`carControl`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`enabled=False`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`actuators.torque=-0.0`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`actuators.torqueOutputCan=0.0`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：C3X?`0x2E4`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 3 - `0x2E4` Identified As `STEERING_LKA`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：DBC；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x2E4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`toyotacan.create_steer_command(...)`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`secoc.add_mac(...)`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x2E4`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 4 - Raw Log Shape Matched SecOC `STEERING_LKA`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：DLC；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`SET_ME_1`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`LKA_STATE`?`0x00`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`bus0`?`bus2`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 5 - Dangerous Experimental Layout Found；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x116`?`0x131`?`0x2E4`?`0x260`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：WSL?C3X?`/data/openpilot`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 6 - SecOC Formula Confirmed From Openpilot；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`opendbc/car/secoc.py`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`TRIP_CNT`?`RESET_CNT`?`0x0F / SECOC_SYNCHRONIZATION`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 7 -  Key Validated Against `0x2E4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 8 -  Also Validated Against `0x131`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：DBC?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 9 - Example MAC Comparisons；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x131`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 10 - C3X Key Installation；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：C3X?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：C3X；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`controlsd`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Milestone 11 - C3X Code Path Checked；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`/data/openpilot`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Remaining Caveats；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x0F / SECOC_SYNCHRONIZATION`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：MAC?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x0F`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：MAC；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`TRIP_CNT`?`RESET_CNT`?`0x0F`?`0x2E4`?`0x131`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Live `sendcan` Still Required；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：C3X?`sendcan`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Stationary Live Test Gate；此項說明其條件、角色或判斷，技術名詞保留原文。
- 步驟：依本文件脈絡完成此項檢查或判斷。
- 重點：LKAS；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`sendcan`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`STEERING_LKA`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x260`?`0x2E4`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：LKAS?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x2E4`?MAC；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`SecOCKey`?`CC.secoc_key`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`sendcan`?`carState.steerFaultTemporary`?`steerFaultPermanent`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：WSL Full-Log Verification；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：WSL?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：Reports And Tools；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：secoc-20260522-steering-lka-key-validation-zh；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：LKAS?C3X?`0x2E4 / STEERING_LKA`?`SecOCKey`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x2E4`?`STEERING_LKA`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：AES-CMAC；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`0x131 / STEERING_LTA_2`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：C3X?`STEERING_LKA + add_mac(...)`；此項說明其條件、角色或判斷，技術名詞保留原文。
- 重點：`sendcan`?TSK；此項說明其條件、角色或判斷，技術名詞保留原文。

## 保留的技術名詞與資料
- program / script / log spec / CAN ID / DBC signal / file path / command 保留原文。
- 表格中的欄位名、檔名、 frame ID 與數值保留原文，以避免誤譯分析結果。

## 後續整理
後續可再依原始 log 與表格人工精修。
