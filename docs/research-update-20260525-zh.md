# Toyota Sienna TSK 專案研究結果更新

日期：

- `2026-05-25`

## 這次更新的核心

到目前為止，`Toyota Sienna 2024 + C3X` 這個 `TSK / SecOC` 專案，已經不再只是被動分析專案。

目前最重要的新狀態是：

- **`TSK` 已確認**
- **`2024 Sienna` 上 `C3X` 橫向操作已正常**

這代表專案重心已經從：

- `TSK` 是什麼
- 哪條 passive backbone 最可信

逐步轉向：

- 怎麼把 secure/auth 材料穩定導出
- 怎麼把成功路徑固化
- 怎麼完成可重複實作

## 一、已完成的研究成果

### 1. Passive backbone 已定型

目前最穩的 passive `TSK-nearest` backbone 已固定為：

- `0x116`
- `0x131`
- `0x2E4`

這條線已經足夠支撐：

- lifecycle 判讀
- bridge-tier 判讀
- 高價值 session / window 篩選

### 2. Top-tier anchor 已固定

目前 top-tier anchor 仍然是：

- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](/D:/Temp/20260312/raw_can_logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

它仍然是：

- 最完整的 joined lifecycle
- 所有 `Grade A` 結構比較的基準樣本

### 3. Bridge ladder 已建立

目前 ladder 已清楚建立：

1. `185520`
2. `173834`
3. `184921`
4. `171414`
5. `190101`

### 4. `20260509` 新 batch 已把 bridge-gap 明顯縮小

`20260509 Session 3` 已提供一段很有價值的長 mixed-route 主樣本。

目前最合理定位是：

- **route-level bridge-tier candidate**
- 高於 `171414`
- 低於 `190101`

也就是：

- bridge-gap **已明顯縮小**
- 但還不能直接叫 closed

### 5. Control-side branch 已收斂

目前最穩的 control-side anchor 是：

- `0x260`

replay-backed working branch 已收斂成：

- `decode_mode = no_b1_flip`
- `mode = identity`
- `higher slew`

### 6. City-side local working rule 已收斂

在 `transition / settle` 子相位下，已有可用 local working rule：

- `low-band catch-up 5.5x`
- `deeper-negative helper 2.5x`

### 7. 直接導出舊分支的失效層已定位

舊 `extract_keys` 分支現在最可信的失效解釋不是：

- 車上沒有 key

而是：

- dump range
- memory layout
- parser assumptions

對 `2024 Sienna` 已不再匹配

### 8. LKAS / SecOC 故障上下文已補強

目前已經有：

- fingerprint + `LKAS Context`
- `LKAS Failed`
- `SecOC synchronization / key-state`

這條線對 future direct validation 很重要。

### 9. 新實作里程碑：C3X 橫向已正常

目前已確認：

- **`C3X` 已可在 `2024 Sienna` 上正常做橫向操作**

這是目前最重要的實作里程碑之一。

它代表：

- secure/auth / protected path 至少已有一條實際可工作的橫向鏈
- 專案已從「能不能控制」進入「怎麼穩定、怎麼導出、怎麼擴展」

## 二、目前仍未完成的研究問題

### 1. bridge-gap 尚未正式閉合

雖然 `20260509 Session 3` 已大幅縮小 bridge-gap，
但目前仍然缺：

- single-window plateau persistence
- single-window exit continuity
- promoted-side hold length

### 2. secure/auth closure 尚未完成

即使 `TSK` 已確認、橫向也已成功，
還是需要真正完成：

- `SecOCKey` 有效性
- freshness / synchronization
- MAC / authenticator packing
- protected message set

### 3. `0x2E4` 的 operational meaning 仍未完全閉合

目前知道它重要，
但還要確認它在實作中到底只是 side channel，
還是更強的 operational prerequisite。

### 4. final mapping 仍未 implementation-grade closure

`0x260` working branch 已很強，
但仍然是：

- replay-backed working branch

而不是最後 implementation truth。

## 三、目前最合理的專案重心

如果用一句話描述目前研究重心：

**主線已經從「證明 TSK」轉成「如何把 secure/auth 與 control-side 路徑穩定導出並固化成可重複實作流程」。**

## 四、接下來最值得做的事

### 1. 少量、目的明確的驗證型 logs

未來 log 收集不應再以擴 corpus 為主，
而應改成：

- fingerprint / `LKAS Context` / fault 對照
- active attempt 前後對照
- sync 成功 / sync 失敗對照
- 成功橫向樣本 / 輕微異常樣本

### 2. direct branch 改造成穩定導出鏈

最短執行路徑是：

1. `dump-only`
2. `candidate parser`
3. `write-back / acceptance validation`

### 3. 固化成功橫向路徑

既然 `C3X` 橫向已正常，
現在最該做的是：

- 固化成功條件
- 固化版本資訊
- 固化啟動順序
- 固化 fault / recovery 行為

## 五、一句話總結

截至 `2026-05-25`，`Toyota Sienna 2024 TSK` 專案已完成 passive backbone、bridge ladder、control-side working branch、direct branch failure-layer 定位，並進一步確認 `TSK` 與 `C3X` 橫向可用；目前專案的真正主重心已轉為 secure/auth 導出、成功路徑固化，以及實作級 acceptance 驗證。

## 參考

- [current-findings-summary-v2.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/current-findings-summary-v2.md)
- [OPENPILOT_INTEGRATION_PROGRESS_REPORT.md](/D:/Codex/toyota-sienna-tsk-analysis/OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)
- [tsk-confirmed-milestones-and-fast-export-plan-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/tsk-confirmed-milestones-and-fast-export-plan-zh.md)
- [implementation-next-step-plan-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/implementation-next-step-plan-zh.md)
- [post-secoc-key-remaining-checklist-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/post-secoc-key-remaining-checklist-zh.md)
