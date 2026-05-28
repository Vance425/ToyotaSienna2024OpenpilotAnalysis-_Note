# Final Grading Rules

## 目的

把目前所有分析收敛成一套统一分级规则，用于后续所有新 log。

目标不是解释背景，而是直接给出判定标准。

## Grade A: Full Match

满足以下条件：

1. `0x131 family zone = fff4`
2. `0x260 family zone = fff4`
3. `0x116 phase = 00 00`
4. `fff4|fff4` 在 base phase 上有稳定停留，不是单点穿过
5. 从 `00 00` 离开时出现 `n0 +8` re-seed
6. 后续出现明显 ramp
   - 例如 `20 31 -> 2A 3A`
7. 进入高位平台
   - `phase_sum >= 130`
8. 退出时出现：
   - `fff4 -> fff0`
   - phase 下退

### 当前已知样本

- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

## Grade B: Partial Seed

满足以下条件中的前半段，但没有完成后续展开：

1. 碰到 `fff4|fff4`
2. `0x116 phase = 00 00`
3. 但 `fff4|fff4` 停留很短，未形成稳定 base
4. 没有 `+8` re-seed
5. 没有明显 ramp
6. 没有高位平台

### 当前已知样本

- [toyota_seg_IGN_ON_20260312_185520_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_185520_000.ndjson)

## Grade C: Corridor Only

满足以下条件：

1. 落在 `fff4 -> ffe7` corridor
2. 但 `phase_sum < 120`
3. 或 family pair 不满足 `fff4|fff4`

这类样本仍有价值，但优先级低于 Full Match / Partial Seed。

## Grade D: No Match

不满足上述结构。

包括：

- 没有 `fff4|fff4`
- 没有 base phase
- 没有 high phase
- 或 family / phase / tail 结构不对齐

## 实际使用顺序

后面新 log 进来时，按这个顺序检查：

1. 先看是否出现 `fff4|fff4`
2. 再看是否出现 `00 00`
3. 再看是否有 `+8` re-seed
4. 再看是否有 ramp
5. 再看是否进入 `phase_sum >= 130`
6. 最后看是否按 `fff4 -> fff0` 退出

## 当前最实用的结论

对你的目标最有帮助的，不是“候选 ID 列表”，而是这套分级：

- Grade A: 最像接近 security-like state
- Grade B: 触边但未进入
- Grade C: 一般 corridor 活动
- Grade D: 无关

## 后续策略

以后你再录新路况 log，优先找：

1. 新的 Grade A
2. 次要找 Grade B

如果新资料里没有新的 Grade A，但出现更多 Grade B，也有分析价值，因为那表示：

- 触边条件会复现
- 但完整 entry 仍然稀少
