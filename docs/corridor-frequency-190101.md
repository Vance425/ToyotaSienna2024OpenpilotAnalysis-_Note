# Corridor Frequency (`190101`)

## 目的

统计高优先级 family corridor：

- `fff4 -> fff0 -> ffee -> ffeb -> ffe8 -> ffe7`

在 [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson) 中的出现频率与持续时间。

## 总体结果

- corridor segments: `80`
- total duration: `7283 ms`
- max duration: `756 ms`
- max phase_sum: `139`

## 最重要的观察

### 1. 这条 corridor 不是单一孤例

它在整段长 log 里总共出现：

- `80` 个 segment

所以不能把它当成偶发噪声。

### 2. 但真正高价值的 segment 只占少数

虽然 corridor segment 很多，但绝大多数 phase 深度不高。

真正高价值的是这几段：

- `1773342250360 -> 1773342251116`
  - duration: `756 ms`
  - max_phase_sum: `139`
- `1773342223249 -> 1773342223795`
  - duration: `546 ms`
  - max_phase_sum: `106`
- `1773342295257 -> 1773342319136`
  - duration: `418 ms`
  - max_phase_sum: `106`

### 3. 高 phase corridor segment 很稀疏

如果只看 `phase_sum >= 100` 的样本，它们集中在少数几段，而不是均匀分布在整段 driving log 里。

这表示：

- corridor 本身会反复出现
- 但真正高深度的 corridor 事件是稀疏的

## 目前最实用的判准

后面看新 log 时，不要把所有 `fffx` corridor 都当成同等级事件。

更好的优先顺序是：

### Tier 1

- corridor segment
- 且 `phase_sum >= 120`

### Tier 2

- corridor segment
- 且 `phase_sum >= 100`

### Tier 3

- corridor segment
- 但 `phase_sum < 100`

Tier 3 更像一般 driving family state 活动，不应优先占分析时间。

## 对整体任务的意义

这个结果很关键，因为它把候选范围缩得更小：

- 不是所有 `fffx` corridor 都值得追
- 真正该追的是：
  - corridor 内
  - phase 还爬得很高
  - 且持续时间足够长

## 下一步

最值得做的是：

1. 把 `phase_sum >= 120` 的 corridor 事件列成顶级候选
2. 再去看这些顶级候选在 `0x131 / 0x260` 上是否有额外共同结构
