# Driving Log Validation (2026-03-12)

## 目的

用 `2026-03-12` 的實際開車 log，驗證之前從 `2026-03-11` 建出的模型能不能跨 log 重現。

驗證對象：

- `0x131`: boundary / state indicator
- `0x260`: family sync / state snapshot
- `0x116`: phase-bearing protected candidate
- `0x610`: anchor
- `0xD5`: speed guardrail

## 先看整體結果

新一批 `IGN_ON` 駕駛 log 裡，這套 ID 家族都存在，而且數量充足。

其中最值得先看的兩段是：

- $label (local-only source path)
- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

原因：

- `2026-03-12 18:58:01` 這段完整命中 `4/4` 模板
- `2026-03-12 19:01:01` 這段也有多個 `4/4` anchor

## 樣本 A: `2026-03-12 18:58:01`

檔案：

- $label (local-only source path)

最佳 anchor：

- `1773341925041`

窗口內的關鍵特徵：

- `0x131` 從 `0038fff1 -> 003afff3 -> 003bfff4 -> 003dfff7` 轉到 `0000fff9 -> 0003fffb -> 0007fffb -> 000afffb`
- `0x260` 從 `000004fff1 -> 000009fff4 -> 000010fff7 -> 00001cfff9` 轉到 `000016fffb -> 00000bfffb -> 000013fffc -> 000017fffc`
- `0x116` phase 從 `18 17 -> 17 17 -> 17 16 -> 16 16`
- `0xD5` 在這個窗口內維持 `08000000000000e5`

### 判讀

這段幾乎是教科書式重現：

1. `0x131` 先翻過邊界
2. `0x260` 跟著切 family state
3. `0x116` phase 在同一帶內遞進
4. `0xD5` 不動

這直接支持目前的工作模型不是只對 `2026-03-11` 有效。

## 樣本 B: `2026-03-12 19:01:01`

檔案：

- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

最佳 anchor 之一：

- `1773342083826`

窗口內的關鍵特徵：

- `0x131` 從 `003bff29 -> 003cff2a -> 003eff2b -> 003fff2b` 轉到 `0000ff2b -> 0002ff2b -> 0004ff2b -> 0007ff30 -> 0008ff32 -> 000aff36`
- `0x260` 從 `00ff79ff2a -> 00ff77ff2b -> 00ff78ff2b -> 00ff76ff2b` 轉到 `00ff8eff30 -> 00ff94ff36 -> 00ff99ff3a -> 00ffa3ff3f -> 00ffa9ff4c -> 00ffb2ff51`
- `0x116` phase 沿著事件帶下降：
  - `1e 1d -> 1d 1d -> 1d 1c -> 1c 1c -> 1c 1b -> 1b 1b -> 1b 1a -> 1a 1a -> 1a 19 -> 19 19`

### 判讀

這段更有價值，因為它不是靜態樣本，而是更動態的 driving window。

最重要的是：

- 模型仍然成立
- 只是 `0xD5` 在這段後半開始從 `08000000000000e5` 轉成 `08ffff00000000e3`

這代表：

- 在真實駕駛條件下，speed guardrail 會開始漂
- 但 `0x131 / 0x260 / 0x116` 的 family-boundary-phase 結構仍然清楚存在

## 最重要的驗證結論

這套模型已經不是只在單一靜態 log 內成立，而是至少跨到 `2026-03-12` 的實際開車 log 也能重現。

目前最穩的共同結構仍然是：

1. `0x131` 給 boundary
2. `0x260` 給 family sync
3. `0x116` 給 phase

## 模型更新

在 driving log 上，這套模型需要補一個現實條件：

- `0xD5` 不一定永遠穩定

所以之後在實車 driving log 上，`0xD5` 更適合當：

- speed context line

而不再是硬性要求完全不變的 guardrail。

## 目前最值得優先深挖的新樣本

如果只選一段 `2026-03-12` 的 log 繼續往下做：

1. $label (local-only source path)
2. [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

前者適合當乾淨重現樣本，後者適合當動態 driving 驗證樣本。
