# Boundary vs Steady Results

## 目標

驗證 `0x116.tail.n0` 的 `+4` 骨架，是不是主要出現在 phase 內的穩定段，而不是 phase 剛切換的邊界段。

這裡採用的簡化定義：

- `boundary segment`: 每個 phase 的前 2 筆 `0x116`
- `steady segment`: 同一 phase 之後的剩餘 `0x116`

## `184921`

檔案：

- [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)

### 觀察

- `25 00`
  - boundary: `9 -> d` (`+4`)
  - steady: `d -> 1` (`+4`), `1 -> 6` (`+5`)
- `27 00`
  - boundary: `2 -> 6` (`+4`)
  - steady: `6 -> a` (`+4`), `a -> e` (`+4`)
- `28 00`
  - boundary: `2 -> 6` (`+4`)
  - steady: `6 -> a` (`+4`)

### 判讀

`184921` 幾乎完全符合預期：

- boundary 段通常先把 `n0` 帶進節奏
- steady 段大多回到乾淨 `+4`

唯一比較明顯的例外是：

- `25 00` 最後一步出現 `+5`

但整體仍非常支持 `n0` 的主骨架是 `+4`。

## `185451`

檔案：

- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)

### 觀察

- `09 0a`
  - boundary: `5 -> 6` (`+1`)
  - steady: `6 -> a -> e -> 2 -> 6 -> a` 全部是 `+4`
- `0d 0e`
  - boundary: `6 -> a` (`+4`)
  - steady: `a -> 2` (`+8`), `2 -> 6` (`+4`), `6 -> 7` (`+1`), `7 -> b` (`+4`)

### 判讀

`185451` 也大致支持模型，但比 `184921` 複雜：

- `09 0a` 很漂亮，steady 段完全回到 `+4`
- `0d 0e` 仍以 `+4` 為主，但 steady 段混入 `+8` 和 `+1`

這代表：

- `+4` 很可能是 `n0` 的主要骨架
- 但在某些 phase / state 下，steady 段仍會受額外擾動

## 合併結論

目前最合理的說法是：

1. `n0` 的主 rolling 骨架是 `+4`
2. phase 邊界段更容易出現重定相
3. steady 段通常更接近純 `+4`
4. 但某些 phase 仍會在 steady 段混入額外步進，如 `+1` 或 `+8`

## 對目前模型的更新

現在可以把 `0x116.tail.n0` 描述成：

- phase-aware rolling nibble
- 主骨架為 `+4`
- 邊界段會重定相
- 某些複雜 phase 的 steady 段仍可能插入修正步進

## 目前最值得記住的高價值樣本

### 最乾淨的 steady 樣本

- `184921 / 27 00`
- `185451 / 09 0a`

這兩段最適合當之後進一步建模的基準。
