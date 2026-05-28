# Current Findings Summary

## 目的

用最短路径总结当前已经站得住的结论，作为后续录新 log 和继续分析的统一入口。

## 1. 当前最稳的结构模型

### 核心角色

- `0x131`: boundary / state indicator
- `0x260`: family sync / state snapshot
- `0x116.b0-b1`: phase selector
- `0x116.tail.n0`: rolling backbone
- `0x116.tail.n3`: secondary transition
- `0x116.tail.n1`: weak transition
- `0x116.tail.n6/n7`: auth-heavy weak-structure
- `0x116.tail.n4/n5`: highest-entropy region

## 2. `0x116.tail.n0` 的规则

### backbone

- 主步进：`+4`

### corrections

- `+8`: boundary re-seed
- `+5`: in-phase correction
- `+1`: light correction
- `+13`: rare dynamic correction

### 适用范围

- 这套规则已经在 `2026-03-11` 与 `2026-03-12` 的多段 log 中复现
- `2026-03-12` 整批 `IGN_ON` 段里，`+4` backbone 比例集中在 `74% ~ 78%`

## 3. `00 00` 的意义

- `0x116 phase = 00 00` 更像 base phase
- session 尾端会收敛到 `00 00`
- 新事件带也会从 `00 00` 重新起跑

所以：

- `00 00` 不是失败本身
- 是 protected family 的基底态

## 4. 深爬升 vs 短爬升

### 深爬升

- `0x116` 不只离开 `00 00`
- 还会一路推到高 phase
- 同时 `0x131 / 0x260` family state 深展開

### 短爬升

- `0x116` 有往上跳
- 但 family state 没有同步深展開

当前高价值判断标准：

- 不是只看 `0x116` phase
- 必须同时看 `0x131 / 0x260` family state

## 5. 高优先级 family corridor

目前高 phase 样本集中在一条连续下降的 family corridor：

- `fff4 -> fff0 -> ffee -> ffeb -> ffe8 -> ffe7`

这条 corridor 不是孤例，但真正高 phase 的样本只占少数。

## 6. 当前最强 top-tier candidate

### 严格定义

1. `0x116 phase_sum >= 120`
2. `0x131 family zone = fff4`
3. `0x260 family zone = fff4`

### 实际结果

在 `2026-03-12` 全部 `IGN_ON` 段里，只有一簇满足：

- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

具体点：

- `43 48`
- `44 46`
- `42 40`

这是当前唯一的 top-tier cluster。

## 7. top-tier lifecycle

### Entry

- `fff4|fff4`
- `00 00`
- `n0 +8` re-seed
- 中高 phase ramp

### Plateau

- `phase_sum >= 130`
- `fff4|fff4`

### Exit

- `fff4 -> fff0`
- phase 下退
- `n0 +1` 轻微修正

## 8. Partial Seed

当前已知样本：

- [toyota_seg_IGN_ON_20260312_185520_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_185520_000.ndjson)

定义：

- 触到 `fff4|fff4 + 00 00`
- 但没有稳定停留
- 没有 `+8`
- 没有 ramp
- 没有高位平台

## 9. 当前分级规则

- `Grade A`: Full Match
- `Grade B`: Partial Seed
- `Grade C`: Corridor Only
- `Grade D`: No Match

详细规则见：

- [final-grading-rules.md](./final-grading-rules.md)

## 10. 当前最实用的工作结论

现在最像接近 security-like state 的被动模板，不是单一 frame，也不是单一 ID，而是：

- `fff4|fff4`
- `00 00`
- `+8` re-seed
- 中高 phase ramp
- `43+ / 44+` 高位平台
- `fff4 -> fff0` 退出

## 11. 接下来该做什么

### 录新 log 时

优先：

- 长时间连续 `IGN_ON`
- 同段包含速度变化、方向变化、辅助状态切换

### 新 log 进来后

先用：

- [quick-triage-workflow.md](./quick-triage-workflow.md)
- [top-tier-screening-checklist.md](./top-tier-screening-checklist.md)

### 分析目标

优先找：

- 新的 `Grade A`

其次找：

- 新的 `Grade B`
