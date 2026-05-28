# Top-Tier Screening Checklist

## 用途

这份清单是给后续新 log 直接套用的，不再从头解释模型。

目标是快速判断某段窗口是否接近当前定义的 top-tier security-like candidate。

## Step 1: 先看 family pair

先确认是否出现：

- `0x131 family zone = fff4`
- `0x260 family zone = fff4`

如果没有这组 family pair，先不要往 top-tier 方向判。

## Step 2: 看是否有 base phase

确认在 `fff4|fff4` 期间，`0x116` 是否出现：

- `00 00`

这表示 family pair 已经先到位，但 phase 还在 base state。

## Step 3: 看是否有 re-seed 跳离

从 `00 00` 离开时，优先找：

- `n0` 出现 `+8`

这目前最像 top-tier entry 的 re-seed 信号。

## Step 4: 看中高 phase ramp

检查是否存在连续 ramp，例如：

- `20 31`
- `2A 3A`

不要求完全一样，但至少应有明显中高 phase 推升。

## Step 5: 看高位平台

确认是否进入：

- `phase_sum >= 130`

且此时仍保持：

- `family131 = fff4`
- `family260 = fff4`

这一步是当前最强的 top-tier 判准。

## Step 6: 看退出方式

高位平台结束时，优先确认：

- `0x260` 先从 `fff4` 松到 `fff0`
- `0x116` phase 同步下退
- `n0` 出现 `+1` 或其他轻微修正

如果退出模式完全不同，信心下降。

## 判定等级

### Full Match

同时满足：

1. `fff4|fff4`
2. `00 00`
3. `+8` re-seed
4. 中高 phase ramp
5. `phase_sum >= 130`
6. `fff4 -> fff0` exit

### Partial Match

满足其中 3-5 项，但没有完整高位平台。

### No Match

不满足 family pair，或没有明显高 phase。

## 当前最重要的提醒

不要只看峰值 `43 48 / 44 46 / 42 40`。

必须看完整生命周期：

- entry
- plateau
- exit

否则很容易把普通高 phase 误判成 top-tier。
