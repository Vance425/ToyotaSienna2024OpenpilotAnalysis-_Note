# Partial Seed Analysis (`185520`)

## 目的

解释为什么：

- [toyota_seg_IGN_ON_20260312_185520_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_185520_000.ndjson)

只命中 `base_fff4`，却没有进入完整 top-tier lifecycle。

## 实际命中点

唯一的明确命中是：

- `ts = 1773341749887`
- `phase = 00 00`
- `family131 = fff4`
- `family260 = fff4`
- tail = `bb530556`

## 前后文

附近的 `0x116` 状态：

- `1773341749838`: `00 00`, `f131 = fff5`, `f260 = fff4`, `n0 = 6`
- `1773341749887`: `00 00`, `f131 = fff4`, `f260 = fff4`, `n0 = b`
- `1773341749959`: `00 00`, `f131 = fff4`, `f260 = fff3`, `n0 = 7`
- `1773341750409`: `00 00`, `f131 = fff6`, `f260 = fff4`, `n0 = c`

对应 `n0` 变化：

- `6 -> b` (`+5`)
- `b -> 7` (`+12`)
- `7 -> c` (`+5`)

## 为什么它不是完整 entry

### 1. `fff4|fff4` 停留太短

只出现了单一命中点，没有形成稳定的 base plateau。

### 2. 没有 `+8` re-seed

从 `00 00` 离开 top-tier entry 时，预期应看到：

- `n0` 的 `+8`

这里没有看到。

### 3. family pair 没有稳定锁住

family pair 是：

- `fff5|fff4`
- `fff4|fff4`
- `fff4|fff3`
- `fff6|fff4`

也就是：

- 只短暂穿过 `fff4|fff4`
- 没有像 `190101` 那样在该 pair 上稳定停住

### 4. phase 完全没有离开 `00 00`

这表示：

- base seed 有碰到
- 但没有真正触发 entry ramp

## 当前最合理的解释

`185520` 更像：

- 触及了 top-tier entry 的 seed 条件
- 但没有完成锁定

它是：

- Partial Seed

不是：

- Full Match

## 对后续的意义

这给了当前模板一个很有用的补充：

### Full Match

- `fff4|fff4` 稳定
- `00 00`
- `+8` re-seed
- ramp
- plateau

### Partial Seed

- 短暂碰到 `fff4|fff4`
- 仍停在 `00 00`
- 没有 `+8`
- family pair 很快漂走

## 当前最实用的判断

以后如果在新 log 里看到：

- `fff4|fff4`
- `00 00`

不要立刻当作 top-tier entry。

先确认：

1. 是否稳定停留
2. 是否出现 `+8`
3. 是否真的开始 ramp

如果三者没有，就更接近 `185520` 这种 partial seed。
