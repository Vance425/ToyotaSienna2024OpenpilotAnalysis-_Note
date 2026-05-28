# 2026-05-09 Session 3 后半高价值区详细解读（中文版）

## 这页看什么

这页只看 `20260509` 长主段后半那块连续高价值区域，也就是：

- [toyota_seg_IGN_ON_20260508_193555_015.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_193555_015.ndjson)
- [toyota_seg_IGN_ON_20260508_193824_016.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_193824_016.ndjson)
- [toyota_all_20260508_193747_008.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_193747_008.ndjson)

其中：

- `toyota_all_20260508_193747_008.ndjson`
  是这一批唯一的 whole-file `A`

## 先讲结论

这一块**不是某个 15 秒单窗自己就是 `190101` 级别的完整 A**。  
它更像是：

- **前半有 plateau-like 高相位触碰**
- **中间有多次 seed-only 重置 / 接续**
- **后半有连续 seed+ramp 恢复 cluster**

也就是说：

- whole-file 会被判成 `A`
- 但拆成 `15s / 5s stride` 的 local windows 后
- 最强还是：
  - `Grade B`
  - `ladder_level = 3`

这说明它的价值在：

- **跨数分钟的 joined continuity**

不是：

- 单个短窗里的极强 promotion

## 相关输出

- [window_summary.csv](/D:/Codex/toyota-sienna-tsk-analysis/analysis-output/session3_high_region_window_triage/window_summary.csv)
- [shortlist.csv](/D:/Codex/toyota-sienna-tsk-analysis/analysis-output/session3_high_region_window_triage/shortlist.csv)
- [manifest.json](/D:/Codex/toyota-sienna-tsk-analysis/analysis-output/session3_high_region_window_triage/manifest.json)
- 脚本：
  - [session_window_triage.py](/D:/Codex/toyota-sienna-tsk-analysis/scripts/session_window_triage.py)

## 这块区域的文件级判断

### 1. `toyota_seg_IGN_ON_20260508_193555_015`

- 时间：
  - `03:35:55.672`
  - 到
  - `03:38:24.684`
- whole-file：
  - `B`
- 特征：
  - `seed + ramp + plateau`
  - 但没有 exit

### 2. `toyota_seg_IGN_ON_20260508_193824_016`

- 时间：
  - `03:38:24.684`
  - 到
  - `03:40:50.821`
- whole-file：
  - `B`
- 特征：
  - `seed + ramp`
  - 没有 plateau / exit

### 3. `toyota_all_20260508_193747_008`

- 时间：
  - `03:37:47.838`
  - 到
  - `03:42:35.929`
- whole-file：
  - `A`
- 特征：
  - `seed + ramp + plateau + exit`

## 为什么 whole-file 是 A，但 local windows 不是

这是这次最关键的点。

当前最合理的解释是：

- `A` 文件里的完整 lifecycle 元素
  - 不是都挤在同一个短窗里
- 而是分布在同一个约 `4.8` 分钟文件里的不同子带

也就是：

1. 一段 plateau-like 高相位子带
2. 几段 seed-only 接续子带
3. 几段 seed+ramp 恢复子带
4. 以及稍后的 exit 连接

所以：

- **whole-file 看起来完整**
- **single 15s local window 还不够完整**

## 关键局部窗口

### A. 早段 plateau-like 子带

在 `toyota_all_20260508_193747_008` 里，
最明显的 plateau-like 触碰出现在：

- `rel 25s -> 40s`
- `rel 30s -> 45s`
- `rel 35s -> 50s`

换成绝对时间大致是：

- `03:38:12.838 -> 03:38:37.838`
- `03:38:17.838 -> 03:38:42.838`

特征：

- `phase_plateau_present = 1`
- 但 `seed_touch_present = 0`
- `ramp_present = 0`
- 所以单独看仍然不是完整窗口

解读：

- 这更像一段已经在比较深状态里的高相位触碰
- 不是从 seed 一路爬上去的完整单窗

### B. 中段 seed-only / reconnect 子带

在同一支 `A` 文件里，中段出现多段 seed-only pocket：

- `rel 110s -> 145s`
- `rel 135s -> 175s`

大致落在：

- `03:39:37` 到 `03:40:42`

特征：

- `seed_touch_present = 1`
- `ramp_present = 0`

解读：

- 更像中途的重接、切换、重新抓取 protected-family continuity
- 不是深层 promotion 本身

### C. 后段最强 seed+ramp cluster

当前最强局部窗口主要集中在：

- `toyota_all_20260508_193747_008`
  - `rel 165 -> 180`
  - `rel 170 -> 185`
  - `rel 175 -> 190`

换成绝对时间大致是：

- `03:40:32.838 -> 03:40:47.838`
- `03:40:37.838 -> 03:40:52.838`
- `03:40:42.838 -> 03:40:57.838`

以及相邻文件：

- `toyota_seg_IGN_ON_20260508_193824_016`
  - `rel 125 -> 140`
  - `rel 130 -> 145`

大致是：

- `03:40:29.684 -> 03:40:44.684`
- `03:40:34.684 -> 03:40:49.684`

特征：

- `grade = B`
- `ladder_level = 3`
- `seed_touch_present = 1`
- `ramp_present = 1`
- `phase_plateau_present = 0`
- `phase_exit_present = 0`

这说明：

- 这块后段最像：
  - **跟车恢复**
  - **换目标后重新建立**
  - **自动降速后再拉回**
- 它是这块区域里最像“动态跟车事件”的部分

## 用车况语言怎么理解

在没有 marker 的前提下，最合理的工作解释是：

### 不是单一稳态巡航

因为如果是单一稳定高速巡航，
我们更容易看到：

- 单窗里的完整连续结构

但这里看到的是：

- plateau-like 早段
- reconnect 中段
- recovery 后段

### 更像 mixed follow / target change / route transition

所以这块更像：

- 高速或快速道路上的持续跟车
- 中途出现：
  - 前车变道
  - 跟车目标切换
  - 自动降速
  - 再恢复跟车

特别是后段 `03:40:30` 左右那块，
最像：

- **换目标后的重新抓取 + 跟车恢复 cluster**

## 当前阶段判断

### 这块已经比 `20260426` 强很多

因为这里已经出现：

- whole-file `A`
- 连续高价值 `B/B/A` 区

### 但它还不是“单窗版 190101”

因为当前 `15s` local windows 里：

- 还没有一个单窗自己就完整到 `A`
- 最强还是 `B / ladder 3`

### 它最像什么

它最像：

- **跨几分钟拼接出来的 joined lifecycle zone**
- 而不是：
  - 一个超尖锐的短时 burst

## 现在最值得继续看的方向

如果继续往下切，
最值得优先对回你叙述中的事件的是：

1. `03:40:30` 左右这块后段 recovery cluster
   - 最像自动降速后再跟上
   - 或前车变道后重新抓取目标

2. `03:38:12 -> 03:38:42` 左右的 plateau-like 子带
   - 最像较深跟车稳态 / promoted-side 触碰

## 一句话总结

`20260509 Session 3` 后半这块高价值区，不是“某个 15 秒单窗直接复制 `190101`”，而是**一段跨数分钟、由 plateau-like 触碰、中途 reconnect、后段 seed+ramp recovery 拼起来的 joined lifecycle zone**；其中最像动态跟车事件的，是 `03:40:30` 左右那块后段恢复 cluster。
