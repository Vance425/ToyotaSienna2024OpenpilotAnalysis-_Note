# Partial Seed Comparison (`185520` vs `20260314`)

## 目的

比较三段 `Grade B / Partial Seed` 样本，确认 `2026-03-14` 的新样本是否只是重复旧的 partial-seed 型态，还是更接近 `Grade A`。

样本：

- [toyota_seg_IGN_ON_20260312_185520_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_185520_000.ndjson)
- [toyota_seg_IGN_ON_20260314_173834_000.ndjson](../logs/toyota_seg_IGN_ON_20260314_173834_000.ndjson)
- [toyota_seg_IGN_ON_20260314_175006_001.ndjson](../logs/toyota_seg_IGN_ON_20260314_175006_001.ndjson)

## 样本 A: `185520`

特征：

- 命中 `fff4|fff4 + 00 00`
- 只出现单一命中点
- family pair 很快漂走
- 没有 `+8`
- 没有 ramp

结论：

- 标准 `Partial Seed`

## 样本 B: `20260314 / 173834`

关键窗口：

- around `1773510290447`

观察：

- `0x116` 全程仍停在 `00 00`
- `0x131 / 0x260` 从：
  - `fff7 -> fff4 -> fff3 -> fff0 -> ffed -> ffec`
 这一带快速漂移
- 命中的 `fff4|fff4` 只有一个点：
  - `1773510290447`
- 之后没有出现 `+8`
- 也没有 phase ramp

结论：

- 和 `185520` 同型
- 甚至更像“family state 穿过 `fff4|fff4`”而不是稳定锁住

## 样本 C: `20260314 / 175006`

关键窗口：

- around `1773510858591`

观察：

- `0x116` 全程仍停在 `00 00`
- `0x131 / 0x260` 只短暂落在 `fff4`
- 很快回到：
  - `fff3`
  - `fff2`
- 一样没有 `+8`
- 一样没有 ramp

结论：

- 也是 `Partial Seed`
- 没有看到任何比 `185520` 更接近 `Grade A` 的特征

## 合并结论

`2026-03-14` 的两个新 `Grade B`，本质上都在重复 `185520` 型态：

- 触到 `fff4|fff4 + 00 00`
- 但没锁住
- 没有 `+8`
- 没有 ramp

## 当前最重要的判断

这说明：

- `Partial Seed` 已经是可复现模式
- 但到目前为止，还没有看到 `Partial Seed -> Full Match` 的中间态

也就是：

- 现有数据里，`Grade B` 和 `Grade A` 之间仍有明显鸿沟

## 对后续录制的意义

后面新 log 进来时，如果再次出现 `Grade B`，不要把它当作“差一点成功”。

更准确的说法应该是：

- 触边条件会复现
- 但完整 lifecycle 仍然非常稀少

## 当前最值得继续追的信号

如果之后要判断一个新样本是否“比 Grade B 更强”，至少要多看到其中一个：

1. `fff4|fff4` 稳定停留，不再只是单点穿过
2. `00 00 -> 非 00 00` 时出现 `+8`
3. 开始出现中高 phase ramp
