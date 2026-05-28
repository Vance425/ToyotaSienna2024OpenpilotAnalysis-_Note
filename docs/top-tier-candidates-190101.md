# Top-Tier Candidates (`190101`)

## 目的

把 `190101` 中同时满足：

- `phase_sum >= 120`
- 落在高优先级 corridor

的事件，列成当前顶级候选集合。

## 顶级候选

| ts | phase | phase_sum | family131 | family260 | tail |
| --- | --- | ---: | --- | --- | --- |
| `1773342250785` | `43 48` | 139 | `fff4` | `fff4` | `c4c9b5cf` |
| `1773342250810` | `44 46` | 138 | `fff4` | `fff4` | `03b58bee` |
| `1773342250831` | `42 40` | 130 | `fff4` | `fff4` | `47657959` |
| `1773342250856` | `3e 3c` | 122 | `fff4` | `fff0` | `5495425d` |

## 共同结构

### 最强共同点

前三个最高样本全部落在：

- `family131 = fff4`
- `family260 = fff4`

只有第四个样本开始从：

- `fff4|fff4`

转向：

- `fff4|fff0`

### 这代表什么

当前最强的顶级候选状态，可以先定义成：

- `phase_sum >= 130`
- `family131 = fff4`
- `family260 = fff4`

这比之前的泛化 corridor 更精确。

## 当前最强候选状态定义

### Candidate State A

- `0x116 phase_sum >= 130`
- `0x131 family zone = fff4`
- `0x260 family zone = fff4`

### Candidate State B

- `0x116 phase_sum >= 120`
- `0x131 family zone = fff4`
- `0x260 family zone = fff0`

这看起来像从 Candidate State A 往下退一层的边界。

## 为什么这很重要

因为它让候选条件从：

- 高 phase
- corridor

进一步收紧成：

- 顶级高 phase
- 固定 family pair

这已经接近可以直接拿去做“是否接近 security gate”的被动筛选规则。

## 当前最实用的筛选规则

如果之后看新 log，要优先标记顶级样本，可先用：

1. `0x116 phase_sum >= 130`
2. `0x131 family zone = fff4`
3. `0x260 family zone = fff4`

只要三者同时满足，就列为：

- top-tier security-like candidate

## 下一步

最值得继续做的是：

1. 看这组 top-tier candidate 在 `190101` 里前后各发生了什么
2. 对照它前后的 `n0`、phase ramp、family corridor 是否有固定前兆
