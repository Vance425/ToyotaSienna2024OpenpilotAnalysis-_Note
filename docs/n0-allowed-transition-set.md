# `n0` Allowed Transition Set

## 目的

把目前從靜態樣本與 driving 樣本看到的 `0x116.tail.n0` 行為，整理成可直接套用的轉移集合模型。

## 資料來源

主要依據：

- [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)
- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)
- $label (local-only source path)
- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

## 主骨架

目前最高信心的轉移是：

- `+4`

理由：

- 在 `2026-03-11` 的乾淨樣本裡，很多 phase 內幾乎全部都是 `+4`
- 在 `2026-03-12` 的 driving 樣本裡，steady 段仍然反覆回到 `+4`

所以目前最合理的主模型是：

- `n0_next ~= n0_current + 4 (mod 16)`

## 修正步進

目前已經觀察到的非主骨架步進有：

- `+1`
- `+5`
- `+8`
- `+13`

### `+1`

典型場景：

- phase 剛切換後的早期樣本
- 或較複雜 phase 中的局部修正

### `+5`

典型場景：

- 靜態樣本 phase 尾端
- 或 driving 樣本的 phase 重新定相區

### `+8`

典型場景：

- 明顯 boundary / re-seed 痕跡
- 例如新 phase 的前幾步

### `+13`

典型場景：

- 目前只在較動態 driving phase 中看到
- 優先視為高動態修正項，不當成主規律

## 目前的轉移分層

### Tier 1: Backbone

- `+4`

### Tier 2: Boundary / re-seed corrections

- `+8`
- `+5`
- `+1`

### Tier 3: Rare dynamic correction

- `+13`

## 使用方式

之後看新 log 時，可以先用這個規則判斷 `n0` 是否仍在模型內：

1. 如果 phase 內大多數步進是 `+4`，視為模型一致
2. 如果 phase 邊界前後插入 `+1 / +5 / +8`，視為可接受修正
3. 如果偶發 `+13` 出現在高動態 driving 段，先標記為 rare correction
4. 如果開始大量出現其他步進，再視為模型偏離

## 目前最實用的工程判準

一個窗口若同時滿足：

- `0x131` 有 boundary
- `0x260` 有 family sync
- `0x116` phase 清楚切換
- `n0` 主要以 `+4` 前進，並只在邊界附近出現少量修正步進

那這個窗口就應視為高信心樣本。

## 目前還不能說的事

這個模型還不能證明：

- `n0` 就是公開可重建的 counter
- 修正步進的精確觸發公式已經找到了
- 已經能直接推回 `TSK`

這份模型的價值在於：

- 它把 `n0` 從「像 counter」提升成「可驗證的 rolling 規則」

## 下一步

如果要再往前推，最值得做的是：

1. 針對 phase 邊界附近統計 `+1 / +5 / +8 / +13` 的出現條件
2. 檢查這些修正步進是否和 `0x131.b3` 或 `0x260.b4` 的特定跳點對齊
