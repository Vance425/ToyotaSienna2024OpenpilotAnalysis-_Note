# Project Status

## 核心目標

目前目標是讓 `2024 Toyota Sienna + comma 3X` 的整合狀態變得可理解、可重現，並且足夠安全，能支撐 controlled implementation work。

本狀態文件採中文敘述，保留必要英文技術詞。凡是 `CAN ID`、frame 名稱、log 檔名、script 名稱、param key 與 validation label，均保留原文，避免後續與程式、log、DBC 或實車資料對不上。

目前專案層級的判斷：

1. `TSK` 已在 project level 視為 confirmed。
2. `2024 Toyota Sienna` 的 C3X lateral operation 已視為 field-working。
3. `2024 Toyota Sienna` 的 C3X longitudinal operation 也已進入 field-working / implementation-stage 判讀。
4. 主要 bottleneck 已從「是否存在 TSK path」轉為：
   - `SecOCKey` 已生效後的 live validation repeatability
   - freshness / synchronization closure
   - MAC / packing closure
   - protected message-set acceptance
   - stable implementation workflow

## 範圍

這個 share bundle 聚焦：

- passive `TSK-nearest` lifecycle research
- control-side replay 與 event interpretation
- direct SecOC branch 的 public-safe 狀態
- implementation-stage prerequisites 與 remaining gaps

它不應被解讀為：

- 所有 secure/auth details 已完全 closed
- raw `SecOCKey` 已可公開
- passive logs 本身足以直接 derive 出完整 TSK
- 任何 active ECU programming workflow 可以無風險執行

## 已確認里程碑

- Passive backbone 已收斂到：
  - `0x116`
  - `0x131`
  - `0x2E4`
- `0x260` 仍是目前最強 control-side anchor。
- `20260312_190101_000` 仍是最強 top-tier joined lifecycle anchor。
- `20260509 Session 3` 目前視為 route-level bridge-tier candidate：
  - 強於 `171414`
  - 仍弱於 `190101`
- Steering-frame SecOC validation 已確認：
  - `0x2E4 / STEERING_LKA`
  - `0x131 / STEERING_LTA_2`
- Steering SecOC key 目前結論停在已安裝、已生效；下一階段是 live validation。
- `C3X` lateral operation 目前視為已可在 `2024 Sienna` 上工作。

## 目前解讀模型

Main passive lifecycle path：

```text
0x116 / 0x131 / 0x2E4
```

Main control-side anchor：

```text
0x260
```

Strongest replay-backed control branch：

```text
no_b1_flip + identity + higher slew
```

Strongest city `transition / settle` local working rule：

```text
low-band catch-up 5.5x
deeper-negative helper 2.5x
```

## 尚未完成的缺口

### 1. Passive bridge gap

Passive bridge gap 已縮小，但尚未宣稱 closed。

相對於 `190101`，目前仍缺：

- single-window plateau persistence
- single-window exit continuity
- promoted-side hold length

### 2. Secure/Auth closure

Secure/auth branch 仍未視為 fully closed。

主要未解項已從 key search 轉為 key 生效後的 validation closure：

- live `sendcan` repeatability
- freshness / synchronization closure
- MAC / packing closure
- protected message-set acceptance
- fault recovery 與低速 validation

### 3. Direct branch limits

舊 `extract_keys` path 現在較合理的理解是：

- active ECU memory-extraction workflow
- 可以深入 diagnostic / programming chain
- 但在 `2024 Sienna` 上可能卡在：
  - dump range
  - memory layout
  - parser assumptions

本 repo 不保存實際 `SecOCKey` 或可直接重建 key 的材料。

## 中文閱讀補充

本文件的重點不是列出所有實驗細節，而是回答目前專案「已經確定什麼、還不能宣稱什麼、下一步卡在哪裡」。如果讀者只想掌握目前狀態，可以先看「已確認里程碑」與「尚未完成的缺口」兩節；如果要繼續做實車驗證，才需要進一步閱讀 implementation checklist、SecOC validation report 與 session review。整體判斷必須保持保守：已經能工作的路徑不等於所有安全認證細節都已封閉，實車測試仍應分階段、低風險、可回退。

## 建議閱讀順序

1. [README.md](./README.md)
2. [Openpilot Integration Progress Report](./OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)
3. [Current Conclusion 2026-05-25](./docs/current-conclusion-20260525-zh.md)
4. [Research Update 2026-05-25](./docs/research-update-20260525-zh.md)
5. [Current Findings Summary](./docs/current-findings-summary-v2.md)
6. [SecOC Steering LKA Key Validation Full Report](./docs/secoc-20260522-steering-lka-key-validation-full-zh.md)

## Public-safe sharing notes

- 代表性 raw CAN logs 只以 curated subset 放在 `./logs`。
- local-only raw log references 需標記為 `local-only source path`。
- private IP、實際 `SecOCKey`、private key file 不放入本 repo。
- key 相關內容只保留 validation result 與遮罩後資訊。
