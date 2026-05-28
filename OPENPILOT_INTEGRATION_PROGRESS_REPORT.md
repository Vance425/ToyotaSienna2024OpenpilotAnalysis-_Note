# Toyota Sienna 2024 Openpilot 整合進度報告

## 核心目標

降低 `2024 Toyota Sienna` openpilot support 在以下兩個面向的不確定性：

- `SecOC / TSK-nearest lifecycle`
- `control-side integration prerequisites`

本報告以中文整理 openpilot 整合進度，保留英文技術詞是刻意設計：frame ID、控制分支名稱、log 檔名、script 名稱與 validation result 都需要與原始資料逐字對齊。中文部分負責說明判斷脈絡、風險、限制與下一步。

這份報告是 **passive-analysis-first** 的進度報告。它不代表 direct `TSK` extraction 或 implementation-ready injection 已完全解決。

主要參考：

- [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md)
- [current-findings-summary-v2.md](docs/current-findings-summary-v2.md)
- [VIRTUAL_TSK_SPEC_v2.md](docs/VIRTUAL_TSK_SPEC_v2.md)
- [tsk-nearest-ladder-entry-to-anchor.md](docs/tsk-nearest-ladder-entry-to-anchor.md)
- [openpilot-control-side-working-note.md](docs/openpilot-control-side-working-note.md)
- [implementation-prerequisites-vs-working-assumptions.md](docs/implementation-prerequisites-vs-working-assumptions.md)
- [implementation-prerequisite-checklist.md](docs/implementation-prerequisite-checklist.md)

## 已驗證 baseline

### 1. Working spec baseline

- [x] `VIRTUAL_TSK_SPEC_v2.md` 是目前 working spec，不是 final authority。
- [x] 目前 `0x260` decoding branch 仍是有用的 control-side baseline。
- [x] Neutral reference `289` 仍是有用的 control-side calibration anchor。

### 2. Passive backbone

- [x] `0x116 + 0x131 + 0x2E4` 是目前最強 passive `TSK-nearest` backbone。
- [x] `toyota_seg_IGN_ON_20260312_190101_000.ndjson` 仍是 top-tier joined lifecycle anchor。
- [x] 目前 corpus 支撐從 early `seed-touch` 到 top-tier joined lifecycle 的 ladder。

### 3. Control-side findings

- [x] `0x260` 是目前最強 longitudinal / control command anchor。
- [x] `0x191` 是 regime-dependent companion family，不是單一 globally stable feedback field。
- [x] `0x371` 是 regime-dependent secondary feedback candidate。
- [x] `0x2E4` 常與 high-value protected windows 同時出現，但早期 passive 分析中尚未證明它是 strict trigger。
- [x] 最強 replay-backed control-side branch：
  - `no_b1_flip + identity + higher slew`
- [x] 最強 city-side local replay rule：
  - `low-band catch-up 5.5x`
  - `deeper-negative helper 2.5x`
  - 僅 gated to `transition / settle`

### 4. Event 與 transition understanding

- [x] ACC-active longitudinal events 應解讀為 multi-ID cluster，不是單一 accel / brake ID。
- [x] `0x260` 大幅變動附近最可靠的 short-window synchronous movers：
  - `0x116`
  - `0x131`
  - `0x2E4`
  - `0xD8`
  - `0x90`
- [x] `disengage suspect` 與 `lane-change transition` 已成為正式 local-band interpretation classes。

## 待完成與缺口

### 1. Passive analysis gap

- [ ] 補上 `20260315_171414_000` 與 `20260312_190101_000` 之間的 bridge gap。
- [ ] 繼續針對 bounded log / session / window candidates 做 triage。
- [ ] 找到比 compact partial-ramp 更深、但仍低於 top-tier joined lifecycle 的 bridge-side windows。

### 2. Integration mapping

- [ ] 將目前 `0x260` setpoint branch 轉成 openpilot 可用的 normalized control domain。
- [ ] 判定 `0x2E4` 應只作為 protected-family side channel，或是否能在 operational path 裡扮演更強角色。
- [ ] 繼續分離：
  - passive backbone findings
  - control-side branch findings
- [ ] 不把 replay-backed working assumptions 直接當作 implementation prerequisites。

### 3. Final validation

- [ ] 在任何 implementation-grade claim 前完成 passive viability sign-off。
- [ ] 確認下一批 bridge-target logs 真的改善 ladder position，而不是只增加 partial-seed coverage。
- [ ] 將 direct-branch assumptions 與 passive-model conclusions 分開。
- [ ] 清掉 [implementation-prerequisite-checklist.md](docs/implementation-prerequisite-checklist.md) 裡的 blocked items。

## 目前不應宣稱的事

- [ ] 不應宣稱 `VIRTUAL_TSK_SPEC_v2` 是 final authority。
- [ ] 不應宣稱 `0x116 + 0x131 + 0x260` 是 final lifecycle trio。
- [ ] 不應宣稱 `0x2E4 -> 0x260` 已是 fully proven strict trigger / heartbeat mechanism。
- [ ] 不應宣稱目前 passive logs 已足夠 derive actual `TSK`。
- [ ] 不應把 control-side consistency 當成 secure/auth-layer closure 的證明。

## 目前最佳短版總結

專案已經有強 passive backbone 與可信的 control-side interpretation layer，但系統尚未完全 closed。

最強 passive model 仍是：

```text
0x116 / 0x131 / 0x2E4 lifecycle backbone
anchor = 20260312_190101_000
```

最強 control-side anchor 仍是：

```text
0x260
```

最重要缺口仍是：

```text
171414_000 -> 190101_000
```

## 2026-05-25 project-level update

- [x] `TSK` 已在 project level 視為 confirmed。
- [x] `2024 Toyota Sienna` lateral operation with `C3X` 已視為 field-working。
- [x] `2024 Toyota Sienna` longitudinal operation with `C3X` 已視為 field-working。
- [x] 專案不再卡在 proving passive `TSK-nearest` path exists。
- [ ] 新 bottleneck：
  - `SecOCKey` export repeatability
  - freshness / synchronization closure
  - MAC / packing closure
  - protected message-set acceptance
  - stable implementation workflow

參考：

- [research-update-20260525-zh.md](docs/research-update-20260525-zh.md)
- [current-conclusion-20260525-zh.md](docs/current-conclusion-20260525-zh.md)

## 2026-05-09 CAN log update

- [x] 專案不再只是等待 new CAN logs。
- [x] `20260509` CAN batch 已納入 passive mainline。
- [x] 短 `fingerprint + LKAS Context + LKAS Failed` segment 提供了更強的 `SecOC / key-state / synchronization` failure-context sample。
- [x] 長 `Session 3` mixed-route sample 提供：
  - route-length real-world follow sample
  - late whole-file `Grade A` high-value region
  - stable follow / auto-decel / target-switch / reacquisition / exit-near complex longitudinal adjustment 的初步 event-style mapping
- [ ] 它本身仍未 close `171414 -> 190101` bridge gap。
- [x] 目前 mainline 將 `20260509 Session 3` late high-value zone 視為 route-level bridge-tier candidate。
- [ ] 下一步要判定它相對於 `190101` 還缺什麼，尤其：
  - single-window plateau persistence
  - single-window exit continuity
  - promoted-side hold length

參考：

- [mainline-progress-update-20260509-zh.md](docs/mainline-progress-update-20260509-zh.md)
- [session-review-20260509-first-pass-zh.md](docs/session-review-20260509-first-pass-zh.md)
- [session-review-20260509-session3-high-region-detailed-zh.md](docs/session-review-20260509-session3-high-region-detailed-zh.md)
- [session-review-20260509-session3-event-table-zh.md](docs/session-review-20260509-session3-event-table-zh.md)
- [session-review-20260509-session3-continuity-gap-vs-171414-190101-zh.md](docs/session-review-20260509-session3-continuity-gap-vs-171414-190101-zh.md)

## 中文閱讀補充

這份進度報告的核心是把研究與實作分開：研究面已經建立出相當可靠的 frame 關係、session ladder 與 control-side 假設；實作面仍然需要確認金鑰載入、freshness 同步、MAC packing、message acceptance 與故障回復。換句話說，專案已經不是「不知道方向」的狀態，而是進入「把可工作的路徑固定成可重複流程」的階段。後續每一個 live test 都應該先有明確觀察項目、成功條件與停止條件。

實務上，這份報告應該被當成測試前的安全檢查清單。任何新增控制邏輯之前，都要先確認它是來自 passive evidence、replay-backed evidence，還是 live vehicle evidence。三者的可信度與風險完全不同，不能混在同一層結論裡。只有當資料來源、預期行為、失敗回退與紀錄方式都清楚時，才適合進入下一輪實車驗證。

因此，這份文件的閱讀方式是先看已驗證項目，再看尚未完成的缺口，最後再回到各個細節文件查證。若某個功能已經在車上看起來可用，仍然要回頭確認它是否具備可重複啟動、可重複關閉、故障可復原、資料可記錄、結果可比對這幾個條件。只有這些條件同時成立，才適合把它從研究假設推進到穩定實作。

簡單說，這份報告的用途是保護專案節奏：知道哪些已經可以依賴，哪些只能作為參考，哪些必須等待下一次驗證。
