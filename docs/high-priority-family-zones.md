# High-Priority Family Zones

## 目的

把 `190101` 中同时满足：

- 高 phase
- `fffx` family state 区域

的样本整理成高优先级候选族群。

## 筛选条件

目前采用：

- `0x116 phase_sum >= 100`
- `0x131` 或 `0x260` 落在 `ff*` family state 区域

## 最高优先级样本

### Tier 1

这些样本最值得优先视为高价值候选：

| ts | phase | phase_sum | family131 | family260 |
| --- | --- | ---: | --- | --- |
| `1773342250785` | `43 48` | 139 | `fff4` | `fff4` |
| `1773342250810` | `44 46` | 138 | `fff4` | `fff4` |
| `1773342250831` | `42 40` | 130 | `fff4` | `fff4` |
| `1773342250856` | `3e 3c` | 122 | `fff4` | `fff0` |
| `1773342250882` | `3c 3a` | 118 | `fff0` | `ffee` |
| `1773342250904` | `3b 3b` | 118 | `fff0` | `ffeb` |

### Tier 2

这些样本仍然重要，但优先度略低：

| ts | phase | phase_sum | family131 | family260 |
| --- | --- | ---: | --- | --- |
| `1773342250974` | `3a 3b` | 117 | `ffe7` | `ffe7` |
| `1773342250953` | `3a 3a` | 116 | `ffeb` | `ffe7` |
| `1773342251023` | `3a 3a` | 116 | `ffe8` | `ffe8` |
| `1773342251043` | `3a 3a` | 116 | `ffe8` | `ffe8` |
| `1773342251067` | `38 35` | 109 | `ffe8` | `ffe8` |

## 核心结论

### 1. 高 phase 并不是随机落在任何 family state

最高 phase 的样本集中在：

- `fff4`
- `fff0`
- `ffee`
- `ffeb`
- `ffe8`
- `ffe7`

这些连续下降的 family state 区域。

### 2. 这是一条有结构的 state 走廊

从最高 phase 往下看，family zone 不是乱跳，而是大致沿着：

- `fff4 -> fff0 -> ffee -> ffeb -> ffe8 -> ffe7`

往下走。

这说明它更像：

- 一条高优先级 family corridor

而不是单点异常。

### 3. `fff4` 是当前最值得盯的顶层区域

目前看到的最高 phase：

- `43 48`
- `44 46`
- `42 40`

都落在：

- `family131 = fff4`
- `family260 = fff4`

这让 `fff4|fff4` 成为当前最高优先级 zone。

## 目前最实用的判准

如果之后看新 log，某个窗口同时满足：

1. `0x116 phase_sum >= 100`
2. `0x131 / 0x260` 落在 `fff4 -> ffe7` 这条走廊

那这个窗口应优先列为：

- high-priority security-like candidate

## 下一步

最值得继续做的是：

1. 统计 `fff4 -> ffe7` 走廊在 `190101` 中出现的持续时间和频率
2. 看这条走廊是否只出现在少数深爬升窗口
3. 之后拿新 driving log 比较，看这条走廊是否稳定复现
