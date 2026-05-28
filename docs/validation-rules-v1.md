# Validation Rules v1

## 目的

把目前分析收斂成可重複套用的驗證規則，後面不管是看新 log、實車 driving log，或比對 `comma 3X` 失敗窗口，都用同一套標準。

## Rule A: 先看 family 結構

高信心窗口應先滿足：

1. `0x131` 出現 boundary / reset-like 行為
2. `0x260` 同步切 family state
3. `0x116` phase 在同窗口內切換

如果三者不同步，優先度下降。

## Rule B: `0xD5` 的用法

- 靜態樣本：`0xD5` 應盡量不變
- driving 樣本：`0xD5` 可作為 speed context line，不再硬要求完全固定

## Rule C: `n0` 的主規律

`0x116.tail.n0` 應主要符合：

- backbone: `+4`

允許的修正步進：

- `+8`: boundary re-seed
- `+5`: in-phase correction
- `+1`: 輕微修正
- `+13`: rare dynamic correction

## Rule D: `n0` 的分段解讀

- boundary segment: 容易出現修正步進
- steady segment: 應主要回到 `+4`

如果 steady segment 長時間脫離 `+4`，模型信心下降。
如果偏離 `+4` 的步進同時伴隨 `0x131 / 0x260` 跳點，先視為 boundary correction。

## Rule E: tail 的其他欄位

目前優先度：

1. `n0`
2. `n3`
3. `n1`
4. `n6/n7`
5. `n4/n5`

不要反過來花時間。

## 目前最好的基準樣本

- [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)
- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)
- $label (local-only source path)
- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

## 現在最值得做的事

後面新 log 進來時，先不要再做大範圍搜候選。

先照這套規則跑：

1. 找 family event band
2. 找 `0x116` phase
3. 驗 `n0` 是否符合 allowed transition set
