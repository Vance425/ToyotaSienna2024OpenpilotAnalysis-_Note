# Match Matrix (2026-03-14)

## 目的

把 $label (local-only source path) 这批新 log 按当前 `Grade A/B/C/D` 规则做第一轮分级。

## 结果

| file | grade | 说明 |
| --- | --- | --- |
| $label (local-only source path) | `D` | 无 `fff4` family seed |
| $label (local-only source path) | `D` | 无 `fff4` family seed |
| $label (local-only source path) | `D` | 无 `fff4` family seed |
| $label (local-only source path) | `D` | 无 `fff4` family seed |
| $label (local-only source path) | `D` | 无 `fff4` family seed |
| $label (local-only source path) | `D` | 无 `fff4` family seed |
| $label (local-only source path) | `D` | 无 `fff4` family seed |
| $label (local-only source path) | `D` | 无 `fff4` family seed |
| [toyota_seg_IGN_ON_20260314_173834_000.ndjson](../logs/toyota_seg_IGN_ON_20260314_173834_000.ndjson) | `B` | 有 `base_fff4`，但无 `+8` / plateau / exit |
| [toyota_seg_IGN_ON_20260314_175006_001.ndjson](../logs/toyota_seg_IGN_ON_20260314_175006_001.ndjson) | `B` | 有 `base_fff4`，但无 `+8` / plateau / exit |

## 结论

### 1. 没有新的 `Grade A`

这批 `2026-03-14` 新 log 里，没有出现新的完整 top-tier lifecycle。

### 2. 出现了两个新的 `Grade B`

这很重要，因为它说明：

- `Partial Seed` 不是一次性现象
- `fff4|fff4 + 00 00` 的触边条件是可复现的

### 3. 目前最实用的解释

当前模式看起来更像：

- `Grade B` 触边相对常见
- `Grade A` 完整进入非常稀少

这和先前 `2026-03-12` 的结果是一致的。

## 对后续录制的意义

如果后面还想提高 `Grade A` 复现率，最该做的不是随机多录，而是：

- 继续拉长连续 `IGN_ON` 段
- 尽量包含速度变化、转向变化、辅助状态切换

因为目前已知唯一 `Grade A` 仍然出现在长段 driving log 中。
