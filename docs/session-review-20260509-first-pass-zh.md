# 2026-05-09 CAN LOG 第一轮总览（中文版）

## 目录

- [raw_can_logs](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs)

## 先讲结论

这一批 `20260509` 现在可以先分成 **3 段可分析主段**：

1. **短异常段**
   - `fingerprint + LKAS Context + LKAS Failed`
   - 很短
   - 价值在 `SecOC / key-state` 故障上下文
   - 不在 `bridge-target`

2. **前置短段**
   - 约 `4.4` 分钟
   - 更像主长 route 之前的一段过渡 / 前置移动

3. **长主段**
   - 约 `44.9` 分钟
   - 是这批真正的主分析段
   - 里面已经出现一个 whole-file `Grade A`

## Session 切分

### Session 1：短异常段

- 时间：
  - `2026-05-09 02:49:58.967`
  - 到
  - `2026-05-09 02:50:32.412`
- 长度：
  - `33.445s`
- 代表文件：
  - [toyota_seg_IGN_ON_20260508_184958_000.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_184958_000.ndjson)
  - [toyota_all_20260508_184957_000.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_184957_000.ndjson)

### Session 2：前置短段

- 时间：
  - `2026-05-09 02:52:43.473`
  - 到
  - `2026-05-09 02:57:04.830`
- 长度：
  - 约 `262.358s`
  - 约 `4.37` 分钟
- 代表文件：
  - [toyota_seg_IGN_ON_20260508_185243_000.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_185243_000.ndjson)
  - [toyota_seg_IGN_ON_20260508_185518_001.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_185518_001.ndjson)
  - [toyota_all_20251125_181721_000.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20251125_181721_000.ndjson)

### Session 3：长主段

- 时间：
  - `2026-05-09 02:58:35.600`
  - 到
  - `2026-05-09 03:43:17.873`
- 长度：
  - `2695.327s`
  - 约 `44.92` 分钟
- 代表文件：
  - [toyota_seg_IGN_ON_20260508_185835_000.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_185835_000.ndjson)
  - 一直到
  - [toyota_seg_IGN_ON_20260508_194316_018.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_194316_018.ndjson)

## 第一轮 grade 结果

输出：

- [can_log_grades.csv](/D:/Codex/toyota-sienna-tsk-analysis/analysis-output/grade_20260509_batch/can_log_grades.csv)
- [can_log_grades.json](/D:/Codex/toyota-sienna-tsk-analysis/analysis-output/grade_20260509_batch/can_log_grades.json)

### 最重要结果

- `Session 1` 短异常段：
  - `D`
  - 这和我们先前对 `LKAS Failed / SecOC sync failure` 的判断一致

- `Session 2` 前置短段：
  - mixed
  - 有一个 `B`
  - 但不是主突破段

- `Session 3` 长主段：
  - 里面已经出现 **1 个 whole-file `A`**
  - 是这批真正值得深切的主段

## 当前最强候选

### Whole-file `A`

- [toyota_all_20260508_193747_008.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_193747_008.ndjson)
- 时间：
  - `2026-05-09 03:37:47.838`
  - 到
  - `2026-05-09 03:42:35.929`
- grade：
  - `A`
- 原因：
  - `seed + ramp + plateau + exit under fff4/fff0 pattern`

这是目前这批里最值得继续切 local windows 的文件。

### 邻近强段

- [toyota_seg_IGN_ON_20260508_193555_015.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_193555_015.ndjson)
  - `03:35:55.672 -> 03:38:24.684`
  - `B`
  - 已经有 `seed + ramp + plateau`，但还没有 exit

- [toyota_seg_IGN_ON_20260508_193824_016.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_seg_IGN_ON_20260508_193824_016.ndjson)
  - `03:38:24.684 -> 03:40:50.821`
  - `B`
  - 紧贴最强 `A` 段

这表示：

- 长主段后半真的有一块连续高价值区域
- 不是单独偶发一格

## 和你描述的车况怎么对

基于时间位置，当前最合理的工作推断是：

- `Session 1`
  - 就是你说的：
    - `Add Sienna fingerprint`
    - 有 `LKAS Context`
    - `LKAS Failed Alarm`
    - 短段

- `Session 2`
  - 更像：
    - `Remove fingerprint` 后的前置短移动 / 准备段
    - 还不是主高速 mixed-route

- `Session 3`
  - 更像你描述的主长 route：
    - 市区移动
    - 上快速道路 / 高速
    - 长时间跟车
    - 中间有自动降速
    - 有前车变道 / 换目标
    - 右转下快速道路 / 再上高速
    - 大角度左右转
    - 再上高速并持续跟车

### 对 `A` 段的当前推断

`03:37:47 -> 03:42:35` 这段 whole-file `A`
位于长主段的后半。

按时间位置，它更像：

- 后段持续高速 / 快速道路跟车
- 或后段换主线后仍保持自动跟车的稳定阶段

它不像：

- 一开始的短异常段
- 也不像纯城市前置段

## 当前阶段判断

### 已经可以确定的

- 这批不是只有一个长段
- 第一段短异常样本已经独立确认
- 第三段长主段里已经出现 whole-file `A`
- 当前最值得深切的是长主段后半：
  - 以 [toyota_all_20260508_193747_008.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_193747_008.ndjson) 为中心

### 还没做的

- 把长主段再切成：
  - 最像跟车建立
  - 最像自动降速
  - 最像目标切换
  - 最像 route transition
  的 local windows

## 下一步

最值得继续做的是：

1. 先深切长主段后半 `A` 段
2. 再用你提供的事件顺序去对：
   - 自动降速
   - 前车变道 / 跟车目标切换
   - 右转下快速道路 / 再上高速
   - 靠右切换到主线 / 国 3
