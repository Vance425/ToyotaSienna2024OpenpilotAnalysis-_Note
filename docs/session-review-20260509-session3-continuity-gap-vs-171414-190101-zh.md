# 2026-05-09 Session 3：相对 `171414` 与 `190101` 的连续性差距

## 目的

这份笔记专门回答一个主线问题：

- `20260509 Session 3` 后半这块高价值连续区
- 到底是怎么高于 `171414`
- 又为什么还不能直接升成 `190101`

参考：

- [20260315-171414-protected-lifecycle-read.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/20260315-171414-protected-lifecycle-read.md)
- [grade-a-golden-sample.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/grade-a-golden-sample.md)
- [session-review-20260509-session3-bridge-tier-read-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-session3-bridge-tier-read-zh.md)
- [session-review-20260509-session3-high-region-detailed-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-session3-high-region-detailed-zh.md)

## 先讲结论

最稳的读法是：

- `20260509 Session 3` 后半高价值区
- **已经高于 `171414`**
- **但还低于 `190101`**
- 它最像的是：
  - **route-level bridge-tier candidate**

更白话一点：

- `171414` 强在局部 seed / ramp
- `190101` 强在完整 joined lifecycle
- `20260509 Session 3` 强在：
  - **跨多个相邻子带的连续性**
- 但弱在：
  - **单一局部窗口的 top-tier 闭环证据**

## 相对 `171414`，它赢在哪里

### 1. 不再只是单口袋的 partial-ramp

`171414` 的典型问题是：

- 有 seed
- 有 real ramp
- 但主要是局部 pocket
- 没有稳定 plateau
- 没有 exit

而 `20260509 Session 3` 后半这块不是只有一个 pocket。

它至少有三类相邻子带连续出现：

- plateau-like 稳跟区
  - `03:38:12 -> 03:38:42`
- reconnect / target reacquisition 区
  - `03:39:37 -> 03:40:42`
- auto-decel / recovery / target-switch cluster
  - `03:40:29 -> 03:40:57`

这表示它不是：

- seed 一下
- ramp 一下
- 很快掉光

而是已经有：

- 连续跟车上下文
- 连续受保护结构活性
- 连续纵向修正带

### 2. whole-file 已经能被打成 `A`

这块的 strongest whole-file 样本是：

- [toyota_all_20260508_193747_008.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_193747_008.ndjson)

whole-file grader 给的是：

- `Grade A`
- `seed + ramp + plateau + exit under fff4/fff0 pattern`

而前后邻近文件也不是掉回低值：

- [toyota_seg_IGN_ON_20260508_193555_015.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_193555_015.ndjson)
  - `B`
  - `touches fff4|fff4 + 0000 but lacks full lifecycle`
- [toyota_seg_IGN_ON_20260508_193824_016.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_193824_016.ndjson)
  - `B`
  - `touches fff4|fff4 + 0000 but lacks full lifecycle`

这和 `171414` 最大的不一样是：

- `171414` 强窗口之间的断感更重
- `20260509 Session 3` 后半已经像一段 route-level 连续高值区域

### 3. bridge-gap 第一次被明显缩小

如果只看旧 ladder：

1. `185520`
2. `173834`
3. `184921`
4. `171414`
5. `190101`

那么 `20260509 Session 3` 后半现在最合理的位置是：

- `4.5` 附近
- 也就是：
  - 高于 `171414`
  - 低于 `190101`

这就是为什么现在可以说：

- bridge-gap 被明显缩小了

## 相对 `190101`，它还差在哪里

### 1. 缺的不是“活动度”，而是“单窗口闭环”

`190101` 是当前唯一真正站得住的 golden sample。

它的最关键结构不是只有：

- seed
- ramp
- high phase

而是这几件事在同一个 top-tier 生命周期里接起来：

1. `fff4|fff4`
2. `00 00`
3. base exit / ramp
4. high plateau at `phase_sum >= 130`
5. `fff4 -> fff0` exit

`20260509 Session 3` 的问题不是没有这些味道，而是：

- 这些证据更像分散在多个相邻子带
- 而不是某一个短局部窗口里完整闭环

### 2. local-window 还是只到 `B / ladder 3`

虽然 whole-file 有 `A`，但把它切成 `15s / 5s stride` 之后，最强局部窗口仍然只是：

- `Grade B`
- `ladder_level = 3`

代表窗口例如：

- `03:40:29.684 -> 03:40:44.684`
- `03:40:34.684 -> 03:40:49.684`
- `03:40:32.838 -> 03:40:47.838`

它们共同的特征是：

- `seed_touch_present = 1`
- `ramp_present = 1`
- `phase_plateau_present = 0`
- `phase_exit_present = 0`

这说明：

- 真正缺的仍是：
  - **单窗口 plateau persistence**
  - **单窗口 exit continuity**

### 3. 它更像 route-level joined zone，不像 top-tier anchor

`190101` 的强，是：

- 单样本内部就能讲完整
- 不需要靠相邻文件帮忙补 continuity

`20260509 Session 3` 后半则更像：

- 一段真实长 route 里
- 晚段连续冒出多个高价值子带
- 组合起来很像 joined zone

但它还不是：

- 单一文件、单一局部窗口、单一闭环
  就能稳稳站成 `190101`

## 所以现在最准确的阶段判断

### 它已经不是 `171414` 型

因为它不再只是：

- seed-heavy
- partial-ramp
- failure-to-promote

### 它也还不是 `190101` 型

因为它还缺：

- 单窗口 top-tier plateau
- 单窗口 top-tier exit
- 单样本内部更干净的闭环证据

### 它最像的中间定位

- **route-level bridge-tier candidate**
- **bridge-gap narrowed, not closed**

## 对主线任务的意义

这一步最大的价值，不是把项目宣布完成，而是把下一步问题问得更精确了。

现在最该问的已经不是：

- `20260509` 有没有价值

而是：

- `20260509 Session 3` 后半这块连续高值区
- 到底还差哪一种 top-tier continuity

最可能还差的层，是：

1. plateau persistence
2. exit continuity
3. promoted-side hold length

## 一句话总结

`20260509 Session 3` 后半这块高价值连续区，已经明显高于 `171414` 的 partial-ramp 层级；但它的强项主要是跨多个相邻子带的 route-level continuity，而不是像 `190101` 那样在单一局部窗口里完成干净的 top-tier plateau + exit 闭环。
