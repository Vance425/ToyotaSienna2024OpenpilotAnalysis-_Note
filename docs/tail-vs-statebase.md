# `0x116` Tail vs State Base

## 目標

確認在固定 `0x116 phase` 的情況下，tail (`b4-b7`) 是否會因為 `0x131.b3` / `0x260.b4` 固定而收斂，還是仍然持續高變動。

## 樣本 1: `184921` 的 `27 00`

檔案：

- [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)

固定條件：

- `0x116 phase = 27 00`

對照結果：

| `0x131.b3` | `0x260.b4` | tail |
| --- | --- | --- |
| `3d` | `3d` | `2321fa94` |
| `3e` | `3e` | `6f8809ce` |
| `3e` | `3e` | `a63aa1db` |
| `3e` | `3e` | `e86fcf4c` |

觀察：

- 當 `0x131.b3 = 3e` 且 `0x260.b4 = 3e` 固定後
- tail 仍然從 `6f8809ce -> a63aa1db -> e86fcf4c`

結論：

只靠 phase + state base 還不能決定 tail。

## 樣本 2: `185451` 的 `09 0a`

檔案：

- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)

固定條件：

- `0x116 phase = 09 0a`

對照結果：

| `0x131.b3` | `0x260.b4` | tail |
| --- | --- | --- |
| `c7` | `bc` | `5648936a` |
| `bc` | `b2` | `66d37c81` |
| `a8` | `b2` | `a1669e30` |
| `a8` | `b2` | `e27e3102` |
| `a8` | `9a` | `2e097cf8` |
| `9a` | `95` | `6c3a68ef` |
| `95` | `90` | `abdf5f55` |

觀察：

- 就算 state base 接近或部分固定，tail 仍然持續高變
- 特別是 `a8 / b2` 這一段，tail 仍有多個完全不同值

結論：

state base 會約束所處區段，但不會把 tail 固定下來。

## 樣本 3: `185451` 的 `0d 0e`

固定條件：

- `0x116 phase = 0d 0e`

對照結果：

| `0x131.b3` | `0x260.b4` | tail |
| --- | --- | --- |
| `8d` | `90` | `6933d4c2` |
| `8d` | `8d` | `a54bcc58` |
| `8d` | `8b` | `27ff7243` |
| `8b` | `8b` | `67cf3cea` |
| `8b` | `8b` | `799d6ec6` |
| `8a` | `8b` | `b7ffc3af` |

觀察：

- 即使 `0x131.b3 = 8b` 且 `0x260.b4 = 8b` 固定
- tail 仍然有不同值：`67cf3cea`, `799d6ec6`

結論：

就算 phase 與 state base 幾乎固定，tail 還是會繼續轉。

## 最重要的判讀

目前最合理的模型是：

- `phase` 決定大區段
- `state base` 決定事件帶位置
- `tail` 還受另一個 rolling 因子影響

也就是說，`0x116 tail` 很可能不是：

- phase 常數
- 單純 state 映射

而更像：

- `phase + state base + rolling element`

## 目前的工作假設更新

### 假設 A

`0x116.b4-b7` 不是靜態查表值。

### 假設 B

`0x116.b4-b7` 很可能包含每 frame 或每幾 frame 都會更新的 rolling/auth-like 成分。

### 假設 C

如果要繼續逼近，可以把下一輪收斂成：

- tail 的 nibble-level 變化
- tail 上是否存在某個 counter 位元
- 或 tail 是否可分成「短週期位」與「高熵 auth 位」

## 實務意義

這是一個很重要的排除結果：

就算我們已經找到 `phase` 和 `state base`，仍然不能直接預測 `0x116 tail`。

這讓 `0x116` 更像真正的保護輸出，而不是普通控制訊號。
