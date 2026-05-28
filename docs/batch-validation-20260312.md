# Batch Validation (2026-03-12)

## 目的

把 `2026-03-12` 全部 `IGN_ON` driving log 用同一套規則做批次驗證，確認目前模型是不是只對少數樣本成立。

檢查指標：

- `0x116` phase transition 數量
- 同 phase 內 `n0` 的步進分布
- `n0` 的 backbone 比例

規則：

- backbone: `+4`
- corrections: `+1`, `+5`, `+8`, `+13`
- other: 其他步進

## 批次結果

| file | phase transitions | same-phase steps | backbone | corrections | other | backbone % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| $label (local-only source path) | 0 | 2312 | 1759 | 496 | 57 | 76.1 |
| $label (local-only source path) | 0 | 1179 | 872 | 279 | 28 | 74.0 |
| [toyota_seg_IGN_ON_20260312_185520_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_185520_000.ndjson) | 0 | 1375 | 1067 | 280 | 28 | 77.6 |
| $label (local-only source path) | 0 | 1791 | 1345 | 405 | 41 | 75.1 |
| $label (local-only source path) | 305 | 1554 | 1172 | 349 | 33 | 75.4 |
| $label (local-only source path) | 423 | 5679 | 4288 | 1290 | 101 | 75.5 |
| [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson) | 1123 | 13351 | 10317 | 2784 | 250 | 77.3 |

## 核心結論

### 1. `n0` 模型是跨 log 穩定的

七段 log 的 backbone 比例都落在：

- `74.0%` 到 `77.6%`

這個集中度很高。

代表：

- `n0 = +4 backbone` 不是單一窗口現象
- 在整批 `2026-03-12` driving log 上都能重現

### 2. corrections 是常態，不是例外

所有檔案都有相當數量的 corrections。

這代表：

- 真實 driving 條件下，不能期待 `n0` 是純淨 counter
- 正確模型必須保留 boundary / dynamic correction

### 3. `other` 比例維持很低

各檔 `other` 只占很小比例。

這表示目前的 allowed transition set 已經抓到主要行為：

- `+4`
- `+1`
- `+5`
- `+8`
- `+13`

## 額外解讀

### phase transition = 0 的前幾段

`185306` 到 `185607` 前幾段 phase transition 幾乎沒有，這表示：

- 當時 driving 狀態較單純
- 但 `n0` backbone 仍然存在

所以 `n0` 不依賴 phase 一直切換才成立。

### phase transition 很多的後幾段

`185704`、`185801`、`190101` phase transition 明顯上升。

尤其 `190101` 有：

- `1123` 次 phase transitions

但 backbone 比例反而仍有 `77.3%`。

這很重要，因為它說明：

- 即使在高動態 driving 條件下
- `n0` 的主骨架仍然站得住

## 目前最穩的工作結論

現在可以把這件事說得更直接：

`0x116.tail.n0` 是跨 log、跨 driving 場景都可重現的 rolling backbone，主步進為 `+4`，並夾帶少量可分類的 correction steps。

## 下一步

如果還要繼續往下挖，最值得做的是兩件事之一：

1. 對 `corrections` 做更細的條件統計，確認它們和 `0x131 / 0x260` 的哪種跳點最相關
2. 開始把這套規則回套到 `comma 3X` 失敗前後的窗口，找是否存在「模型斷裂點」
