# Correction Step Alignment

## 目的

確認 `0x116.tail.n0` 的修正步進：

- `+1`
- `+5`
- `+8`
- `+13`

是否和 `0x131.b3` / `0x260.b4` 的跳點對齊。

## 檢查樣本

- $label (local-only source path)
- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

## 觀察結果

### `+8` in `18:58:01`

例 1:

- phase: `17 17`
- `n0`: `6 -> e`
- `0x131.b3`: `f3`
- `0x260.b4`: `f4`

這筆發生在 phase 邊界早期，屬於新相位起跑。

例 2:

- phase: `16 16`
- `n0`: `e -> 6`
- `0x131.b3`: `f9 -> fb`
- `0x260.b4`: `f9 -> f9`

這筆明顯對齊 `0x131.b3` 的跳點。

例 3:

- phase: `19 19`
- `n0`: `8 -> 0`
- `0x131.b3`: `4c -> 56`
- `0x260.b4`: `4c -> 5b`

這筆同時對齊 `0x131.b3` 和 `0x260.b4` 的大跳點。

### `+5` in `18:58:01`

- phase: `16 16`
- `n0`: `6 -> b`
- `0x131.b3`: `fb -> fb`
- `0x260.b4`: `f9 -> fb`

這筆沒有像 `+8` 那麼強烈的雙軸跳點。

比較合理的解讀是：

- `+5` 偏向 phase 內修正
- 有時會伴隨較小的 family 微調

### `+13` in `19:01:01`

- phase: `1c 1c`
- `n0`: `7 -> 4`
- `0x131.b3`: `2b -> 2b`
- `0x260.b4`: `2b -> 2b`

這筆最重要，因為它說明：

- `+13` 不一定和 state 跳點綁在一起

比較合理的解讀是：

- `+13` 是 rare dynamic correction
- 比較像高動態 driving 條件下的局部例外

## 合併結論

目前可以把修正步進分成兩類：

### Type A: boundary-aligned correction

- 代表：`+8`

特徵：

- 常和 `0x131.b3` / `0x260.b4` 的明顯跳點一起出現
- 比較像 phase re-seed 或邊界重定相

### Type B: in-phase correction

- 代表：`+5`
- 稀有代表：`+13`

特徵：

- 不一定伴隨強 state 跳點
- 更像 phase 內或高動態條件下的局部修正

## 更新後的 `n0` 規則

現在可以把 `n0` 的 allowed transition set 寫得更精確：

- Backbone: `+4`
- Boundary re-seed: `+8`
- In-phase correction: `+5`
- Rare dynamic correction: `+13`
- `+1` 保留為早期觀察到的輕微修正項

## 對後續分析的意義

後面看新 log 時，不只要看 `n0` 有沒有偏離 `+4`，還要分辨：

1. 這次偏離是不是和 `0x131 / 0x260` 的 state 跳點一起出現
2. 如果是，優先當 boundary correction
3. 如果不是，才當 in-phase / rare dynamic correction
