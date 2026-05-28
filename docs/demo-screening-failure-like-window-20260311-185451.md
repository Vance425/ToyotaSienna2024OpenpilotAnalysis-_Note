# 第 5 輪示範: Failure-Like Candidate Window

## 目標

這一輪不再用 `184921` 做教學樣本，而是直接看目前跨多段 log 比對後，最像失敗邊界候選的窗口：

- Log: [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)
- Window: `1773255299471` to `1773255299871`
- Anchor: `1773255299671`

## 先看參考線

### `0x610`

在 `1773255299671` 出現 anchor：

- `1773255299671  0x610  00001a3cd0000040`

這代表這個窗口裡確實有 steering/state 類型事件點。

### `0xD5`

在整個窗口內都維持：

- `08000000000000e5`

所以這不是 speed-driven 事件。這點很重要，因為它把一般車速變化造成的 frame 波動先排掉了。

## 候選線觀察

### `0x131`: reset-like 很明顯

窗口前半段：

- `003cf9d3...`
- `003ef9c7...`
- `003ff9bc...`

接著跨進 reset-like 區段：

- `0001f9a8...`
- `0004f99a...`
- `0005f995...`
- `0007f991...`
- `0008f990...`
- `000af98d...`

判讀：

這不像單純連續量測值，更像 state family 進入另一個 phase。

### `0x116`: 這次 phase change 很乾淨

窗口內可以看到 prefix phase 遞進：

- `09090000...`
- `090a0000...`
- `0a0c0000...`
- `0d0e0000...`

判讀：

這比 `184714` 強很多。`0x116` 在這裡不是單純 tail 抖動，而是前半部 phase 也在切換。

### `0x260`: 核心 family 在同步改變

窗口內例子：

- `00fef2f9...`
- `00fefbf9...`
- `00fefcf9...`
- `00fefdf9...`
- `00fefef9...`
- `00ff01f9...`
- `00ff04f9...`

判讀：

`0x260` 很像整個 control/state family 的主幹，和 `0x131`、`0x116` 的邊界感是同步的。

### `0x115`: 同步，但比較像伴隨型候選

例子：

- `00000002d1844284`
- `000000021623eabf`
- `00000002681794f1`
- `00000002a3be19f5`

判讀：

`0x115` 仍然有價值，但這個窗口裡它比較像伴隨同群移動，不像 `0x116` 那樣把 phase 特徵直接露出來。

## 和 `184714` 的差別

對照 [toyota_seg_IGN_ON_20260311_184714_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184714_000.ndjson) 的最佳窗口：

- `184714` 也有 `0x131 reset-like`
- `184714` 也有 `0x260 prefix change`
- `184714` 的 `0xD5` 也維持不動
- 但 `184714` 的 `0x116` prefix 幾乎都停在 `00000000...`

所以 `185451` 比 `184714` 更像完整 protected-phase 邊界。

## 本輪結論

目前最像 failure-like candidate window 的，不再是 `184714`，而是：

- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)
- anchor: `1773255299671`

這一輪最關鍵的意義是：

1. `0x610` 幫我們切出事件點
2. `0xD5` 證明這不是 speed event
3. `0x131` 顯示 reset-like 邊界
4. `0x116` 顯示真正明顯的 phase change
5. `0x260` 顯示核心 family 在同步切換

如果之後要對照 `comma 3X` 真正失敗前後，`185451` 應該是你現在最值得優先比對的樣本。
