# Quick Triage Workflow

## 用途

新 log 进来后，先用这套流程快速判断是否值得深挖。

## Step 1: 看是否有基础家族

先确认以下 ID 在 bus 0 都有足够数据：

- `0x116`
- `0x131`
- `0x260`
- `0x610`
- `0xD5`

如果没有，先降权。

## Step 2: 找 `fff4|fff4`

检查是否出现：

- `0x131 family zone = fff4`
- `0x260 family zone = fff4`

如果完全没有，通常不会是 `Grade A / B`。

## Step 3: 看 `00 00`

如果出现 `fff4|fff4`，再看同窗口 `0x116` 是否落在：

- `00 00`

如果有，至少可能是 `Partial Seed`。

## Step 4: 看 `+8` re-seed

从 `00 00` 离开时，检查 `n0` 是否出现：

- `+8`

如果有，优先度大幅上升。

## Step 5: 看 ramp

检查是否出现中高 phase 推升，例如：

- `20 31`
- `2A 3A`

不要求字面完全一样，但应有明显连续上升。

## Step 6: 看 plateau

确认是否进入：

- `phase_sum >= 130`

且仍保持：

- `fff4|fff4`

## Step 7: 看 exit

检查退出是否符合：

- `fff4 -> fff0`
- phase 下退

## 快速分级

### Grade A

- 命中完整 lifecycle

### Grade B

- 命中 `fff4|fff4 + 00 00`
- 但没有后续完整展开

### Grade C

- 在 corridor 内，但不进入 top-tier

### Grade D

- 不满足上述结构

## 当前最重要的判断原则

不要只看高 phase。

优先顺序必须是：

1. family pair
2. base phase
3. re-seed
4. ramp
5. plateau
6. exit
