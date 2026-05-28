# Phase / Reset Watch Rules

## 用途

這份是給之後看新 log 時直接套用的簡化規則，不需要每次都從零開始猜。

## Rule 1: 先找 `0x131` reset

優先找前 4 bytes 的前 2 bytes 是否出現：

- `003x -> 000x`

例子：

- `003e003d -> 0000003d`
- `003ff9bc -> 0001f9a8`

這種變化可以先當成事件邊界。

## Rule 2: 再看 `0x116` phase

如果 `0x131` 有 reset-like 邊界，再看 `0x116` 的前 2 bytes 是否一起切 phase。

已知有效例子：

- `24 -> 25 -> 26 -> 27 -> 28 -> 29`
- `0909 -> 090a -> 0a0c -> 0d0e`

如果 `0x116` 只剩高熵 tail 在變，但前 2 bytes 不動，優先度就下降。

## Rule 3: 用 `0xD5` 排除速度事件

如果同窗口內 `0xD5` 改變，就先不要把那個窗口當成高價值 security 候選。

如果 `0xD5` 不變，而 `0x131 + 0x116` 同步切換，價值就高很多。

## Rule 4: 用 `0x610` 切 anchor

優先從 `0x610` 有變化的地方往前後看 `150-250 ms`。

這比全段瞎掃有效很多。

## Rule 5: `0x260` 當 family sync 驗證

如果以下三件事一起出現：

- `0x131` reset-like
- `0x116` phase change
- `0x260` prefix change

那個窗口就可以列為高優先級。

## 目前最實用的模板

高優先級窗口至少滿足：

1. `0x610` 有 anchor
2. `0xD5` 不變
3. `0x131` 前 2 bytes reset
4. `0x116` 前 2 bytes phase change
5. `0x260` prefix change

## 目前最好的已知樣本

- [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)
- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)

其中更值得優先對照的是：

- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)
