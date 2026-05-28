# `0x116` `n0` Transition Model

## 目標

把 `0x116 tail` 的第一個 nibble (`n0`) 單獨拉出來，確認它是不是目前最像 rolling 候選的欄位。

## `184921` 結果

檔案：

- [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)

### 各 phase 的 `n0`

- `24 00`: `1 -> 5`
- `25 00`: `9 -> d -> 1 -> 6`
- `26 00`: `a -> e`
- `27 00`: `2 -> 6 -> a -> e`
- `28 00`: `2 -> 6 -> a`
- `29 00`: `e -> 2`

### phase 內 delta

- `24 00`: `+4`
- `25 00`: `+4 +4 +5`
- `26 00`: `+4`
- `27 00`: `+4 +4 +4`
- `28 00`: `+4 +4`
- `29 00`: `+4`

### 判讀

`184921` 的 `n0` 非常強，因為大部分 phase 內都近似：

- 固定步進 `+4`

只有 `25 00` 最後一步出現 `+5`，像是 phase 尾端或切段邊界的擾動。

## `185451` 結果

檔案：

- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)

### 各 phase 的 `n0`

- `09 09`: `1`
- `09 0a`: `5 -> 6 -> a -> e -> 2 -> 6 -> a`
- `0a 0c`: `e`
- `0d 0e`: `6 -> a -> 2 -> 6 -> 7 -> b`

### phase 內 delta

- `09 0a`: `+1 +4 +4 +4 +4 +4`
- `0d 0e`: `+4 +8 +4 +1 +4`

### 判讀

`185451` 沒有 `184921` 那麼乾淨，但仍然保留明顯的 `+4` 骨架：

- `09 0a` 幾乎全是 `+4`
- `0d 0e` 以 `+4` 為主，中間插入 `+8` 和 `+1`

這很像：

- 某個主 rolling nibble
- 但會在特定 phase / 邊界附近被調整或重定相

## 合併結論

目前 `0x116 tail` 裡最像 rolling 候選的，就是 `n0`。

它的特徵是：

1. phase 內常以 `+4` 前進
2. 在 phase 切換附近會重設或插入額外步進
3. 不像純高熵亂數

## 現在最合理的工作模型

`n0` 不是全域單調 counter，但很像：

- phase-aware rolling nibble

也就是：

- 在某個 phase 帶內，`n0` 有偏好的步進規律
- 一旦 phase 或 family state 變了，`n0` 也可能重新定相

## 對後續的意義

這是目前最接近「可建模」的 tail 子欄位。

接下來如果要繼續逼近保護結構，最值得做的是：

1. 把 `n0` 當主 rolling 候選
2. 看 phase 切換前後 `n0` 的起始值是否可由 state base 推測
3. 把 `n1 / n3` 當輔助過渡位，不再和 `n0` 同等對待
