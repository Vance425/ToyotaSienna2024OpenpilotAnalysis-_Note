# Current Best Hypothesis

## 目前最值得相信的模型

在現有被動 log 上，最合理的結構是：

- `0x131`: boundary / state indicator
- `0x260`: family sync / state snapshot
- `0x116.b0-b1`: phase selector
- `0x116.tail.n0`: phase-aware rolling nibble
- `0x116.tail.n1/n3`: transition region
- `0x116.tail.n4-n7`: auth-heavy region

## 這個模型的價值

它把原本一整塊很模糊的 `0x116`，拆成了不同角色：

- 可追蹤的 phase
- 可追蹤的 state family
- 可追蹤的 rolling 候選
- 以及較高熵的保護尾端

## 目前最像高勝率入口的地方

不是整個 tail，也不是新 ID，而是：

- `0x116.tail.n0`

因為它已經表現出：

- phase 內常見 `+4` 步進
- phase 邊界附近重定相

## 下一步主線

如果再往前走，最值得做的是：

1. 觀察 `n0` 在 phase 切換時的起始值
2. 看這個起始值是否和 `0x131.b3` / `0x260.b4` 有關
3. 如果有，再把 `n0` 視為「可被 state 約束的 rolling nibble」
