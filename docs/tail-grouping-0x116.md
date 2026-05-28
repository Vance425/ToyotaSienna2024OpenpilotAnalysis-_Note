# `0x116` Tail Grouping

## 目標

確認 `0x116` 的 tail (`b4-b7`) 能不能只靠 phase 分群，還是它本質上就是高熵、快速變動的輸出。

比較樣本：

- [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)
- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)

## 先看 `184921`

### phase 與 tail

- `24 00` -> `155db90d`, `54c6b3ae`
- `25 00` -> `9d6d0666`, `d4e3a360`, `15f0ada0`, `660a66c1`
- `26 00` -> `a42aaf8c`, `eaeb7a6a`
- `27 00` -> `2321fa94`, `6f8809ce`, `a63aa1db`, `e86fcf4c`
- `28 00` -> `2ffd0dcc`, `612d3cae`, `aae9f3c3`
- `29 00` -> `ef4f0979`, `2ba5cffe`

### 觀察

- 同一個 phase 下，tail 幾乎每筆都不同
- 但 phase 本身仍然有明顯區段感
- 代表 `phase` 和 `tail` 不是同一層訊息

## 再看 `185451`

### phase 與 tail

- `09 09` -> `1d411261`
- `09 0a` -> `5648936a`, `66d37c81`, `a1669e30`, `e27e3102`, `2e097cf8`, `6c3a68ef`, `abdf5f55`
- `0a 0c` -> `ecc18170`
- `0d 0e` -> `6933d4c2`, `a54bcc58`, `27ff7243`, `67cf3cea`, `799d6ec6`, `b7ffc3af`

### 觀察

- 結果和 `184921` 一樣
- 同一個 phase 下，tail 還是幾乎不重複
- 但 tail 的變化是掛在特定 phase 帶內發生的

## 最重要的結論

`0x116` 的 tail 不能只靠 phase 分群。

也就是說，下面這件事大致成立：

- `phase` 定義目前所處的狀態段
- `tail` 在這個狀態段內仍然高速變化

這很像：

- auth-like output
- rolling protected value
- state-dependent 保護尾端

而不像：

- 固定 payload
- 單純 checksum
- 只靠 phase 就能決定的欄位

## 和 `0x131 / 0x260` 的關係

從對照表看，`0x116` 的 tail 雖然不會因為 phase 固定住，但它確實是在特定 state base 內變動。

例如在 `185451`：

- `09 0a` 這個 phase 段，`0x131` 會從 `3f/bc -> 01/a8 -> 04/9a -> 05/95 -> 07/91`
- 同時 `0x260` 會從 `fc/b2 -> fd/9a -> fe/95 -> ef/90`
- tail 也在這個 family state 帶內持續變

判讀：

tail 比較像「依賴 phase + state base 的快速變動量」，而不是單一 phase 常數。

## 目前最合理的假設

### 假設 A

`0x116.b0-b1` 是 phase/state selector。

### 假設 B

`0x116.b4-b7` 是高熵保護尾端，可能依賴：

- 當前 phase
- 當前 state base
- 以及某種 rolling element

### 假設 C

如果真的要逼近 `TSK / SecOC`，下一步應該不是再看 phase 本身，而是看：

- 同 phase 下 tail 如何隨 state base 演進

## 下一步

下一輪最值得做的是：

1. 固定一個 phase，對照 `0x131.b3` / `0x260.b4`
2. 看 tail 是否隨 state base 有單調或分段規律
3. 檢查 tail 是否存在 nibble-level counter 或切分邊界
