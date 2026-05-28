# 2026-05-09 第一段 CAN LOG 初判（中文版）

## 对应文件

- [toyota_seg_IGN_ON_20260508_184958_000.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_184958_000.ndjson)
- [toyota_all_20260508_184957_000.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_184957_000.ndjson)
- [toyota_seg_UNKNOWN_20260508_184957_000.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_UNKNOWN_20260508_184957_000.ndjson)
- [lkas-context-quick-read-20260508-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/lkas-context-quick-read-20260508-zh.md)

## 时间范围

- 本地时间起点：`2026-05-09 02:49:58.967 +08:00`
- 本地时间终点：`2026-05-09 02:50:32.412 +08:00`
- 有效长度：约 `33.445s`

## 已确认事实

- 这是一个很短的 `IGN_ON` 段，不是长 route。
- 这一段里关键 ID 都很活，不是空段：
  - `0x00F`: `590`
  - `0x090`: `5120`
  - `0x0AA`: `4926`
  - `0x0D8`: `1881`
  - `0x116`: `2301`
  - `0x127`: `3402`
  - `0x131`: `2275`
  - `0x191`: `2890`
  - `0x260`: `2875`
  - `0x2E4`: `2325`
  - `0x371`: `310`
- 也就是说，这不是单纯没有数据的故障段；它带着一小段真实的 `LKAS / SecOC / control-side` 上下文。

## 快速分级

现成 grader 对这一段的 whole-file 判定是：

- `Grade D`
- 原因：`no seed/corridor pattern`

对应输出：

- [can_log_grades.csv](/D:/Codex/toyota-sienna-tsk-analysis/analysis-output/grade_20260509_first_segment/can_log_grades.csv)
- [can_log_grades.json](/D:/Codex/toyota-sienna-tsk-analysis/analysis-output/grade_20260509_first_segment/can_log_grades.json)

这表示：

- 虽然 `0x116 / 0x131 / 0x2E4 / 0x260` 都活着
- 但它没有形成我们当前关心的：
  - `seed-touch`
  - `ramp`
  - `corridor-active`
  - `partial-ramp`
  这类 `TSK-nearest` 结构

## 和 LKAS Context 的并读结论

结合 [lkas-context-quick-read-20260508-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/lkas-context-quick-read-20260508-zh.md)，当前最合理的工作判断是：

- 这段很像：
  - `fingerprint` 已启用
  - `LKAS Context` 已经跑起来
  - 同时进入了 `SecOC synchronization / key-state` 失败路径
- 它不像：
  - 一段正常发展的 `bridge-target`
  - 或一段会往 `171414 / 190101` 那条梯子爬升的 route

更白话一点：

- 这是“系统有开始尝试进入更深上下文”
- 但很快在 `SecOC / synchronization` 这层出问题
- 所以没有走成真正的 protected-lifecycle promotion

## 当前最稳的阶段判断

这一段的价值主要在：

- `fingerprint + LKAS Context + Failed Alarm`
- `SecOC synchronization / key-state` 故障上下文

这一段的价值不在：

- `bridge-gap`
- `partial-ramp`
- `190101` 方向的长段 promotion

## 下一步

等 `20260509` 其余 CAN log 传完后，最值得继续做的是：

1. 先把这一段和长 mixed-route 主段分开
2. 长主段再按：
   - 跟车建立
   - 自动降速
   - 前车变道 / 跟车目标切换
   - 匝道 / 主线切换
   去做主线分析
3. 这一段则单独保留为：
   - `LKAS Failed / SecOC sync failure` 参考样本
