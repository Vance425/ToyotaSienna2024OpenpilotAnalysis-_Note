# Top-Tier Recurrence Check (2026-03-12)

## 目的

检查当前最严格的 top-tier 定义，是否会在 `2026-03-12` 全部 `IGN_ON` 段里重复出现。

## 使用的 top-tier 定义

严格条件：

1. `0x116 phase_sum >= 120`
2. `0x131 family zone = fff4`
3. `0x260 family zone = fff4`

cluster 定义：

- 相邻命中点时间差 `<= 100 ms`

## 批次结果

### 无 top-tier cluster

- $label (local-only source path)
- $label (local-only source path)
- [toyota_seg_IGN_ON_20260312_185520_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_185520_000.ndjson)
- $label (local-only source path)
- $label (local-only source path)
- $label (local-only source path)

### 有 top-tier cluster

- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

cluster:

- start: `1773342250785`
- end: `1773342250831`
- count: `3`
- max_phase_sum: `139`
- phases: `43 48`, `44 46`, `42 40`

## 结论

在 `2026-03-12` 这批数据里，按当前最严格定义：

- top-tier cluster 只出现一次
- 且只出现在 `190101`

## 这代表什么

### 1. 当前定义具有很强的区分力

它不会把一般 driving 段误判成 top-tier 候选。

### 2. `190101` 的那一簇确实是离群高值样本

它不是“只要开久一点就常见”的模式。

### 3. 目前最需要的是复现样本

如果未来新 log 再次出现同型 cluster，可信度会显著上升。

## 当前最实用的结论

现阶段可以把：

- `phase_sum >= 120`
- `fff4|fff4`

视为一个高精度、低召回的顶级筛选规则。

它适合拿来找极少数高值事件，不适合拿来覆盖全部 candidate。
