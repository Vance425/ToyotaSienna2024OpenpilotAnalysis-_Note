# 20260509 Session 3 vs 190101：plateau / exit pocket 并排对照

## 目的

这页只做一件事：

- 把 `20260509 Session 3` 里最值得看的两个 pocket
- 和 `190101` 的对应结构并排摆在一起

这样可以最快回答：

- 现在已经像到哪
- 还差在哪

参考：

- [grade-a-golden-sample.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/grade-a-golden-sample.md)
- [session-review-20260509-session3-targeted-plateau-exit-cut-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-session3-targeted-plateau-exit-cut-zh.md)
- [session-review-20260509-session3-continuity-gap-vs-171414-190101-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-session3-continuity-gap-vs-171414-190101-zh.md)

## 一、plateau pocket 对照

### `20260509 Session 3` plateau-like pocket

- 时间：
  - `03:38:12 -> 03:38:42`
- 来源：
  - [toyota_all_20260508_193747_008.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_193747_008.ndjson)

当前特征：

- 已经有明显 plateau-like 味道
- 更像 deeper steady-follow / promoted-side hold
- 在 `15s / 5s stride` 下出现：
  - `phase_plateau_present = 1`
- 但同一短窗口里通常是：
  - `seed_touch_present = 0`
  - `ramp_present = 0`
  - `phase_exit_present = 0`

最白话的意思：

- 中段的“高处”已经抓到了
- 但前段 entry/ramp 和后段 exit 没有在同一小窗口里一起闭环

### `190101` plateau

- 参考样本：
  - [toyota_seg_IGN_ON_20260312_190101_000.ndjson](/D:/Temp/20260312/raw_can_logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

当前 gold-standard 特征：

- `fff4|fff4`
- 已经从 base `00 00` 正式爬升上来
- plateau peak 明确：
  - `43 48`
  - `44 46`
- `phase_sum >= 130`
- family pair 持续保持在：
  - `fff4|fff4`

最白话的意思：

- 不只是有“高处”
- 而是能清楚证明：
  - 这是从正确 entry/ramp 走上来的 top-tier plateau

### plateau 对照结论

`20260509` 这段已经像：

- promoted-side 的“中段高处”

但还不像 `190101` 的地方在于：

- 缺少同窗口的前段 ramp 证据
- 缺少同窗口的后段 exit 接续
- 因此更像：
  - **plateau-like pocket**
- 不像：
  - **完整 top-tier plateau segment**

## 二、exit pocket 对照

### `20260509 Session 3` exit-near pocket

- 时间：
  - `03:41:52 -> 03:42:25`

当前特征：

- 最像 late-adjustment / exit-near 行为
- 更像：
  - target switch 后的连续纵向修正
  - route 尾段的复杂调整
  - 可能夹着 exit-side behavior

但当前问题是：

- 它比较像 mixed adjustment cluster
- 还切不成一个干净、独立、短窗口的 top-tier exit 段
- 在 local-window 层面，exit 证据不够漂亮

### `190101` exit

- 参考样本：
  - [toyota_seg_IGN_ON_20260312_190101_000.ndjson](/D:/Temp/20260312/raw_can_logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

当前 gold-standard 特征：

- `0x260: fff4 -> fff0`
- `0x116: 42 40 -> 3E 3C`
- `n0` 有 `+1` shift
- exit family sequence 很干净：
  - `fff4|fff0`
  - `fff0|ffee`
  - `fff0|ffeb`
  - `ffeb|ffea`

最白话的意思：

- 这是一个结构很明确的退出段
- 不是“复杂修正很多，所以也许快退出了”
- 而是“退出路径本身就看得见”

### exit 对照结论

`20260509` 这段已经像：

- exit 前后的复杂尾段调整

但还不像 `190101` 的地方在于：

- 没切出清楚的 `fff4 -> fff0` 局部退出结构
- 没切出同等级的短窗口 exit continuity
- 更像：
  - **exit-near mixed cluster**
- 不像：
  - **clean top-tier exit segment**

## 三、并排总表

| 项目 | `20260509 Session 3` | `190101` |
| --- | --- | --- |
| plateau 位置 | `03:38:12 -> 03:38:42` | top-tier plateau in golden sample |
| plateau 性质 | plateau-like / deeper steady-follow | true top-tier plateau |
| plateau 闭环度 | 中段高处清楚，但前后没一起闭环 | entry -> ramp -> plateau 连得很清楚 |
| exit 位置 | `03:41:52 -> 03:42:25` | top-tier exit in golden sample |
| exit 性质 | exit-near / mixed late adjustment | clean `fff4 -> fff0` exit |
| exit 闭环度 | 尾段修正很多，但退出结构不够干净 | 退出路径本身就很明确 |

## 四、这张表真正告诉我们的事

如果只看局部 pocket：

- `20260509` 已经不是“完全不像 `190101`”
- 它已经出现：
  - plateau-like pocket
  - exit-near pocket

但两边最大的差别是：

- `190101` 的 pocket 是结构闭环的一部分
- `20260509` 的 pocket 还比较像：
  - 各自成立
  - 但彼此之间还没有在局部窗口层面接成 top-tier 闭环

## 一句话总结

`20260509 Session 3` 现在已经有了“像 plateau 的地方”和“像 exit 前尾段的地方”，但它们仍然更像 route-level 连续高值区里的两个强 pocket；`190101` 则是这些 pocket 已经被接成了一个完整、干净、可单点成立的 top-tier lifecycle。
