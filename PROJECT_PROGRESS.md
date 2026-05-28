# Toyota Sienna 2024 Openpilot Project Progress

## 目標

本文件記錄 `2024 Toyota Sienna + comma 3X` 的 openpilot integration progress。

目前主軸：

- 降低 `SecOC / TSK-nearest lifecycle` 的不確定性。
- 建立 `control-side integration prerequisites`。
- 將研究結果整理成可重現、可交接、可公開分享的中文資料。

## 已完成

- 建立 `VIRTUAL_TSK_SPEC_v2.md` 作為 working spec。
- 建立 `0x116 / 0x131 / 0x2E4` passive backbone。
- 確認 `0x260` 是目前最穩 control-side anchor。
- 補齊 curated logs。
- 補入 `analysis-output/` 與本機 share bundle 中缺失的輔助資料。
- 完成 Markdown 第一輪中文化。

## 重要里程碑

### 2026-05-10 DATAFLASH dump-only branch

- DATAFLASH range：`0xff200000:0xff208000`
- useful partial runs 合併 coverage：`31916 / 32768`
- 這條 branch 只作為 dump-only research path，不代表已穩定取得可公開 key。

### 2026-05-22 Steering SecOC validation

- `0x2E4` 已確認為 Toyota `STEERING_LKA`。
- `0x131` 已確認為 Toyota `STEERING_LTA_2`。
- key 已在 steering-related protected frames 驗證鏈上生效。
- 實際 `SecOCKey` 不保存於本 repo。

### 2026-05-25 implementation-stage update

- `TSK` 視為 project-level confirmed。
- C3X lateral / longitudinal operation 視為 field-working。
- 新 bottleneck 不再是找 key，而是 live `sendcan`、freshness / synchronization、MAC packing、protected message acceptance、fault recovery 與 workflow 固化。

## 下一步

1. 精修核心中文文件，不只停留在機械中文化。
2. 建立 `docs/READING_ORDER_ZH.md`。
3. 建立 `docs/public-redaction-policy-zh.md`。
4. 將 root-level 與 docs 裡的主線文件整理成可發布版。
5. 釐清大型 raw archive 是否用 Git LFS 或 local-only archive 管理。
