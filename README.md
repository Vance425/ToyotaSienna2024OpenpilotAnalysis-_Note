# Toyota Sienna openpilot 整合研究筆記

本份文件是為了整理 `2024 Toyota Sienna + comma 3X` 使用 openpilot / sunnypilot 所需的研究筆記、驗證紀錄與實作依據。內容重點是把 `TSK / SecOC`、steering frame、control-side behavior、log analysis workflow 與後續 validation steps 收斂成可追溯、可重跑、可交接的技術資料，作為後續讓車輛穩定使用 openpilot 類系統的基礎。

本文件以中文說明專案脈絡，保留必要英文技術名詞。這樣做是為了避免把 `CAN ID`、`DBC signal`、`SecOCKey`、`sendcan`、檔名與 script 名稱翻譯後造成比對錯誤。閱讀時請把英文技術詞視為資料欄位或程式介面，而不是未完成翻譯。

內容包含：

- 目前研究結論與狀態報告
- 重要 frame / lifecycle / control-side 解讀 memo
- 專案使用的分析 scripts
- CAN log spec、C3X raw CAN logger、收集流程與分析輸出
- simulation / replay-backed 分析產物

## 這是什麼

這個專案目前有兩條主線：

1. **Passive `TSK-nearest` modeling**
   - 從 raw CAN logs 中找出最接近 protected / key-bound lifecycle 的 sessions 與 windows。
   - 目前主 backbone 集中在 `0x116 / 0x131 / 0x2E4`。

2. **Control / companion interpretation**
   - 解讀 `0x260 / 0x191` 在 city、freeway、mixed samples 裡的 regime 行為。
   - `0x260` 目前仍是最穩的 control-side anchor。

重要限制：

- 早期 passive 分析本身不宣稱能從 logs 直接 derive 出完整 `TSK`。
- 2026-05-22 的 steering SecOC 分支已驗證 `0x2E4 / STEERING_LKA` 與 `0x131 / STEERING_LTA_2` 的 key path；目前結論停在 key 已生效。
- 本 repo 只保留 validation result、workflow-level 說明與已遮罩的 key 相關資訊，不保存實際 `SecOCKey`。

## 建議先讀

如果你是第一次看這個 repo，建議照這個順序：

1. [Project Status](./PROJECT_STATUS.md)
2. [Openpilot Integration Progress Report](./OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)
3. [中文閱讀順序](./docs/READING_ORDER_ZH.md)
4. [Current Conclusion 2026-05-25](./docs/current-conclusion-20260525-zh.md)
5. [Research Update 2026-05-25](./docs/research-update-20260525-zh.md)
6. [Current Findings Summary](./docs/current-findings-summary-v2.md)
7. [SecOC Steering LKA Key Validation Full Report](./docs/secoc-20260522-steering-lka-key-validation-full-zh.md)
8. [DATAFLASH Direct Dump Summary](./docs/secoc-20260510/dataflash-direct-dump-summary-zh.md)
9. [Passive TSK-Nearest Overview](./docs/passive-tsk-nearest-overview-zh.md)
10. [TSK-Nearest Ladder](./docs/tsk-nearest-ladder-entry-to-anchor.md)
11. [Final Frame Role Map](./docs/final-frame-role-map.md)

## 代表性 logs

代表性 logs 放在：

```text
./logs
```

這不是完整 raw-log archive，而是精選資料集，用來代表：

- top-tier joined lifecycle anchor
- partial-ramp / bridge-side samples
- freeway / mixed companion behavior
- city active-core / hold / late-stop references

本 Note repo 不放 raw `.ndjson` logs；原始 CAN logs 保留在本機 archive，需要時依文件中的 log spec 與 analysis workflow 重跑。

## 目前狀態摘要

目前這份筆記的主結論是：`2024 Toyota Sienna + comma 3X` 的 openpilot / sunnypilot 整合重點，已從「找出可能的 TSK / SecOC 路徑」推進到「整理已驗證路徑，並準備 live validation」。

已整理出的主線：

- `0x2E4 / STEERING_LKA` 已確認是 Toyota steering command frame。
- `0x131 / STEERING_LTA_2` 是同一 steering SecOC 線上的 companion frame。
- steering SecOC key path 已完成 passive log 驗證，並已在 C3X `SecOCKey` 路徑生效。
- `0x116 / 0x131 / 0x2E4` 仍是理解 protected lifecycle 的主要 backbone。
- `0x260 / 0x191` 是目前最重要的 control-side / companion 解讀線。

後續重點：

- 驗證 live `sendcan` 是否穩定產生正確 SecOC tail。
- 確認 freshness / synchronization 在實車流程中持續一致。
- 驗證 ECU acceptance、fault recovery 與低速 validation 是否可重複通過。
- 保持 raw key、private key file 與 raw CAN logs 不進入本 Note repo。

## Direct SecOC 分支更新

截至 2026-05-22，steering SecOC branch 已完成重大驗證：

- `0x2E4` 已確認是 Toyota `STEERING_LKA`，也就是 LKA steering torque command frame。
- Toyota steering frames 的 SecOC AES-CMAC construction 已用 passive logs 驗證。
- key path 已生效並可驗證：
  - `0x2E4 / STEERING_LKA`
  - `0x131 / STEERING_LTA_2`
- 下一階段重點是 live `sendcan`、freshness / synchronization、ECU acceptance、fault recovery 與低速 validation。
- 實際 `SecOCKey` 不保存於本 repo。

詳見：

- [2026-05-22 SecOC Steering LKA Key Validation Full Report](./docs/secoc-20260522-steering-lka-key-validation-full-zh.md)

截至 2026-05-10，direct EPS DATAFLASH dump branch 也已重新啟用為 dump-only research path：

- DATAFLASH range：`0xff200000:0xff208000`
- 五次 useful partial runs 合併 coverage：`31916 / 32768` bytes，約 `97.4%`
- raw dump binaries 保留 local-only

詳見：

- [2026-05-10 SecOC DATAFLASH Direct Dump Summary](./docs/secoc-20260510/dataflash-direct-dump-summary-zh.md)

## 公開分享原則

- 不公開 raw `SecOCKey`。
- 不公開 private key file。
- candidate 僅公開 fingerprint / validation result。
- `program`、`script`、`log spec`、`CAN ID`、`DBC signal`、檔名、指令、表格欄位保留英文原文。
- active ECU / programming / payload path 只做風險說明，不做無保護的操作推廣。

詳細規則見：

- [Public Redaction Policy](./docs/public-redaction-policy-zh.md)
