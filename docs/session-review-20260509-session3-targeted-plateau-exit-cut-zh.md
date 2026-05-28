# 2026-05-09 Session 3：plateau / exit 目标切分

## 目的

这份笔记继续回答同一个主线问题：

- `20260509 Session 3` 后半这块高价值连续区
- 如果要继续往 `190101` 靠近
- 应该先切哪一段 plateau
- 又为什么 exit 现在还不够干净

参考：

- [session-review-20260509-session3-continuity-gap-vs-171414-190101-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-session3-continuity-gap-vs-171414-190101-zh.md)
- [grade-a-golden-sample.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/grade-a-golden-sample.md)

## 先讲结论

这轮切下来，图像很清楚：

- plateau-like 局部带已经能抓出来
- 但 exit 还抓不成一个干净、独立、短窗口的 top-tier 片段

所以当前最合理的判断是：

- `20260509 Session 3` 强在：
  - **route-level continuity**
- 弱在：
  - **single-window exit isolation**

## 最像 plateau 的局部带

主样本：

- [toyota_all_20260508_193747_008.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_193747_008.ndjson)

在 `15s / 5s stride` 切分里，真正出现 `phase_plateau_present = 1` 的局部带集中在：

- `rel 25s -> 40s`
- `rel 30s -> 45s`
- `rel 35s -> 50s`

换成绝对时间，大约是：

- `03:38:12.838 -> 03:38:27.838`
- `03:38:17.838 -> 03:38:32.838`
- `03:38:22.838 -> 03:38:37.838`

如果看更直觉的回忆区间，可以继续记成：

- `03:38:12 -> 03:38:42`

这段的意思是：

- 已经有明显 promoted-side / deeper steady-follow 味道
- 是当前最值得拿来当 plateau-like pocket 的位置

## 这段为什么还不能直接当 `190101` plateau

虽然 plateau-like 很明显，但这些窗口还有两个问题：

1. 它们不是 seed / ramp / plateau / exit 同时闭环
2. 它们在 local-window grader 里仍然不是 top-tier `A`

最直观的现象是：

- `phase_plateau_present = 1`
- 但 `seed_touch_present = 0`
- `ramp_present = 0`
- `phase_exit_present = 0`

也就是说：

- 我们抓到了 plateau-like 中段
- 但还没在同一小窗口里把前后两端也一起抓住

## exit 为什么现在还不够干净

whole-file grader 对 [toyota_all_20260508_193747_008.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_193747_008.ndjson) 的判断是：

- `seed + ramp + plateau + exit under fff4/fff0 pattern`

但当我们切成 `15s` 短窗口后，出现了一个关键现象：

- 没有哪一个短窗口同时给出：
  - `phase_exit_present = 1`
  - 并且仍然保持 top-tier 局部闭环感

这通常表示两种可能：

1. exit 真的存在
   - 但分散在更宽的连续区里
2. exit 不是一个短、干净、尖锐的独立段
   - 而是和 reconnect / target-switch / longitudinal adjustment 混在一起

对这次样本来说，第二种更像当前情况。

## 现在最像 exit-near 的区间

虽然还没切出漂亮的 local exit window，但最像 exit-near 调整带的仍然是：

- `03:41:52 -> 03:42:25`

这段更像：

- 目标变化后的连续纵向修正
- 接近 route 尾段的复杂调整
- 可能包含 exit-side behavior

但它现在的问题是：

- 更像 mixed adjustment cluster
- 不像 `190101` 那种结构很干净的 `fff4 -> fff0` 退出段

## 这对主线代表什么

这一步把差距讲得更具体了：

- `20260509 Session 3` 不是没有 plateau
- plateau-like pocket 已经很清楚
- 真正还弱的是：
  - **exit continuity**
  - **exit isolation**

也就是说，当前 bridge-tier gap 已经不是：

- 会不会 climb

而更像：

- climb 之后能不能在局部窗口里留下更干净的退出结构

## 下一步最值得怎么切

如果继续往主线深切，最值得的顺序是：

1. 继续以 `03:38:12 -> 03:38:42` 作为 plateau-like 主 pocket
2. 继续以 `03:41:52 -> 03:42:25` 作为 exit-near / late-adjustment 主 pocket
3. 专门看这两段之间：
   - family continuity
   - promoted-side hold
   - `fff4 -> fff0` 是否只是被 mixed adjustments 冲散

## 一句话总结

`20260509 Session 3` 现在最清楚的局部优势是 plateau-like pocket 已经可定位；最清楚的局部短板是 exit 还没有被切成一个干净、独立、短窗口的 top-tier 退出段。这就是它为什么已经高于 `171414`，但还没有追平 `190101`。
