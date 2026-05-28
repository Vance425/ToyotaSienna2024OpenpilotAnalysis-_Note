# Toyota Reverse Batch Pipeline 手冊（中文版）

參考：
- [batch-pipeline-manual.md](./batch-pipeline-manual.md)
- [current-findings-summary-v2.md](./current-findings-summary-v2.md)
- [final-frame-role-map.md](./final-frame-role-map.md)

## 1. 目的

這份手冊是給 batch 分析流程用的。

用途：

- 批次處理 CAN log
- 做 cross-log 比較
- 避免把局部有效結果誤當成全域結論
- 讓後續腳本、SOP、交接都有共同基線

這份手冊不是在宣稱：

- TSK 已經解出
- 控制迴路已經完全解出
- 某一條 feedback 線已經被全域確認

## 2. 目前穩定基線

除非後續文件明確推翻，否則先用這組基線：

- `0x260` = 主 reverse/control target
- `0x131` = boundary/state frame
- `0x116` = protected phase frame
- `0x115` = core support frame
- `0xD8` = 最乾淨的結構參考線
- `0x191` = 重要 external companion line
- `0x2E4 / 0x177 / 0x183 / 0x127` = 次級候選集合

注意：

- 不同 log 不一定包含相同現象
- 同一個 companion field 不一定在所有 log 都有效

## 3. Pipeline 總覽

```text
raw_can_logs
    -> toyota_can_analyzer
    -> toyota_reverse_toolkit / signal_classifier
    -> toyota_control_model 局部建模
    -> regime split / validation
    -> cross-log comparison
    -> batch filtering / summary
```

## 4. Stage 1：Raw Log Intake

### 輸入

- 一份或多份 `.ndjson` CAN log

### 每份 log 最少要補的資訊

- 日期
- 路線型態
- 是否開 `LKAS / ACC`
- 是否包含：
  - 市區
  - 紅燈停走
  - 快速道路 / 高速
  - 匝道 / 轉彎 / 回轉
  - 純原地切換

### Intake 規則

不要把所有 `IGN_ON` 都當成同類。

至少先分成：

- static toggle
- city boundary-rich
- plateau-heavy highway
- mixed long session

## 5. Stage 2：Candidate ID Discovery

### 工具

- `toyota_can_analyzer`

### 目的

從大量 ID 裡找出值得深挖的目標。

### 典型用法

```bash
python3 toyota_can_analyzer_v13.py \
  ~/raw_can_logs/log.ndjson \
  --outdir ~/raw_can_logs/_scan \
  --buses 0
```

### 要保留的 ID 特徵

- period 穩定
- frame count 高
- entropy 不低
- 變化集中在少數 bytes
- 有結構，不是整包亂跳

### 目前應優先保留

- `0x260`
- `0x131`
- `0x116`
- `0x115`
- `0xD8`
- `0x191`

次級集合：

- `0x2E4`
- `0x177`
- `0x183`
- `0x127`

## 6. Stage 3：Single-ID Structure Analysis

### 工具

- `toyota_reverse_toolkit`
- `toyota_signal_classifier`

### 目的

分析單一 ID 的 byte role：

- 哪些 bytes 像 payload
- 哪些 bytes 像 state
- 哪些 bytes 像 counter / checksum / protected tail

### 典型用法

```bash
python3 toyota_reverse_toolkit_v13.py \
  ~/raw_can_logs/log.ndjson \
  --bus 0 \
  --id 0x260 \
  --outdir ~/raw_can_logs/_rtool_260
```

```bash
python3 toyota_signal_classifier_v1_2.py \
  ~/raw_can_logs/log.ndjson \
  --bus 0 \
  --id 0x260 \
  --outdir ~/raw_can_logs/_sigcls_260
```

### 目前 `0x260` 的工作模型

- `b1-b2` = 最強 signed motion/control candidate
- `b3` = spacer / reserved
- `b4` = structured state axis
- `b5` = coarse mode / substate
- `b6-b7` = mixed tail

這是目前最穩的中途模型，不是最終解。

## 7. Stage 4：Local Control Model

### 工具族

- `toyota_control_model_v14` 到 `v18`

### 目的

建立 `0x260` 的局部 offline control decomposition。

### 這一階段可以得出的結論

- 局部 decomposition candidate
- coarse band 解釋
- field ranking

### 這一階段不能直接得出的結論

- 全域 field map closure
- 全域物理量身份

### 目前正確做法

每次做 local model 時，必須一起保留：

- 來源 log
- 來源 regime
- fit 品質

不要把單一 log 的成功結果直接推廣到所有 log。

## 8. Stage 5：External Companion Search

### 工具族

- `toyota_control_model_v19` 到 `v21`

### 目的

找哪些外部 ID / signal 和 `0x260` 有 lagged relationship。

### 典型用法

```bash
python3 toyota_control_model_v19_safe.py \
  log.ndjson \
  --control-id 0x260 \
  --candidate-ids 0x191,0x2E4
```

### 目前實務結論

- `0x191` 值得帶進後續比較

但注意：

- `0311` 裡 `0x191.s16be_b6_7` 有局部有效性
- `0316` 裡同一條解釋會崩掉

所以：

- `0x191` 可以保留
- 但 `0x191.b6-b7` 不能當全域 feedback target

## 9. Stage 6：Feedback Modeling

### 工具

- `v22`
- [control_model_v22.py](../scripts/control_model_v22.py)

### 目的

不是再回頭證明 `control = control`。

而是問：

- 外部 companion 對 `0x260` 的響應是不是可建模
- 這個關係是否會隨 state 改變
- 有沒有 regime-specific deadband
- control 相較 feedback persistence 到底有沒有增量價值

### 目前應跑的四項

- state-conditioned regression
- regime-conditioned deadband
- feedback-only AR baseline
- feedback-plus-control ARX

### 關鍵規則

永遠要比較：

- `AR baseline`
- `ARX`

如果：

- `ARX` 的 `R²` 只多一點點
- 或 `MAE` 更差

就不能說：

- control dynamics 已解出

### 目前最穩結論

- 沒有可信的全域 deadband
- 只有某些 `b5 / domain` regime 內有 deadband-like 行為
- feedback 本身高度平滑、強自相關
- 全域 ARX 對 AR baseline 幾乎沒有增量價值

## 10. Stage 7：Regime Split

### 為什麼一定要做

這一步現在不是可選，而是必做。

原因：

- `0311` 和 `0316` 已經證明全域單模型不安全

### 分段維度

每份 log 至少要按這些維度切：

- session band
- `0x260.b5`
- `0x260` domain
- route / event note

### 每段最少要標的 phenomenon

- static toggle
- seed-heavy
- plateau-heavy
- boundary-rich mixed
- invalid / inactive

### 核心原則

不要拿混合長 session 直接跑一個全域模型，然後相信結果。

## 11. Stage 8：Cross-Log Comparison

### 目的

比較不同 log 之間，哪些局部模型可重現，哪些只是局部現象。

### 每份 log / segment 最少要比的東西

- 最強 companion signal
- best lag
- correlation
- regression 品質
- deadband regime summary
- AR vs ARX gain

### 目前最重要的例子

`0311`：

- `0x191.b6-b7` 像局部有效 feedback-like companion

`0316`：

- `0x191.b6-b7` 幾乎失效
- 有用資訊明顯轉向 `0x191.b4-b5`

正確解讀：

- external companion behavior 是 regime-dependent

## 12. Stage 9：Batch Filtering

### 工具族

- `v23`
- `v24`

### 目的

批次處理多份 log，做：

- valid
- weak
- invalid
- duplicate

### 批次分類原則

batch label 只是 triage，不是證明。

建議類別：

- `VALID`
  - 有 meaningful companion signal
  - lag 穩定
  - regression 品質不差
  - 不明顯是 mixed / invalid
- `WEAK`
  - 有一些關係，但不夠穩
- `INVALID`
  - 在當前模型下看不到有效關係
- `DUPLICATE`
  - 與既有樣本重複度太高

### batch 不該做的事

- 不要默默把不相容的 regime 混在一起
- 不要只報一個全域 winner 而不帶 segment context

## 13. 標準輸出集合

每份 log 或 segment 建議至少保留：

- candidate scan summary
- single-ID reverse outputs
- control model summary
- companion search summary
- feedback regression summary
- deadband summary
- AR vs ARX comparison
- regime split notes

## 14. 建議的目錄結構

```text
raw_can_logs/
  YYYYMMDD/
    log.ndjson
    notes.md

analysis/
  scan/
  reverse/
  control_model/
  batch/

reports/
  per_log/
  cross_log/
```

## 15. Batch 決策順序

照這個順序走：

1. 先確認 log 類型與 route context
2. 掃 candidate IDs
3. 確認 `0x260` 是否存在且有結構
4. 找 external companion
5. 跑 feedback modeling
6. 如果是 mixed log，先做 regime split
7. 和歷史 log 做比較
8. 最後才給 batch label

## 16. 目前最穩的工程結論

這些結論已足夠當 pipeline 基線：

- `0x260` 仍是主 reverse/control target
- `0xD8` 仍是最乾淨的結構參考線
- `0x191` 值得保留為主要 external companion line
- `0x191` 的 field identity 還沒有全域解出
- 全域單模型不安全
- regime split 現在是必需步驟

## 17. 常見反模式

不要：

- 因為一份 log 成功，就宣稱模型全域成立
- 把單一 feedback field 當成永遠正確
- 不做 AR baseline 就直接讀 ARX `R²`
- 對混合長 session 不分段就建模
- 太早宣稱物理量身份

## 18. 下一步最值得做的事

目前最值得的 batch 方向是：

- 先把 `0316` 類 log 切 regime
- 在每個 regime 裡分別比較：
  - `0x191.b4-b5`
  - `0x191.b6-b7`
- 再把 per-regime 結果送進 batch classifier

## 19. 一句話總結

這條 pipeline 現在已經不是在找一個 magic frame。

而是在做：

- 建立局部模型
- 用 external companion 驗證
- 過濾 overfit
- 只保留能跨 log、跨 regime 站得住的結論
