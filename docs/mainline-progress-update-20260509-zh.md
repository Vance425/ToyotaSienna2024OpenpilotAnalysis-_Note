# 2026-05-09 主线进度更新（中文版）

## 这份更新的意义

在这份更新之前，主线状态大致是：

- passive backbone 已稳定
- replay/control-side 已有主分支
- city `transition / settle` 已有本地 working rule
- bridge-gap 仍然 open
- GitHub 主线的现实状态可以理解成：
  - **等待新的高价值 CAN LOG**

现在这件事已经变化了：

- **新的 `20260509` CAN LOG 已经到位**
- 而且第一轮主线分析已经完成

## 这批新 CAN LOG 帮到了什么

### 1. `Session 1` 补强了异常线

最前面那段：

- `fingerprint`
- `LKAS Context`
- `LKAS Failed`

现在更清楚地支持：

- 这不是普通控制逻辑没起来
- 更像 active fingerprint context 下的：
  - `SecOC synchronization / key-state` 失败

对应：

- [session-review-20260509-segment1-preliminary-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-segment1-preliminary-zh.md)
- [lkas-context-quick-read-20260508-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/lkas-context-quick-read-20260508-zh.md)

### 2. `Session 3` 补到了真正有价值的长 mixed-route 主段

这批最重要的不是前面短段，而是：

- `Session 3`
- `02:58:35 -> 03:43:17`
- 约 `44.9` 分钟

它很像你描述的那条长 mixed route：

- 市区 / 高速切换
- 长时间跟车
- 前车变道
- 跟车目标切换
- 自动降速
- 靠右离开高速
- 大转向 / 地面道路过渡
- 再次上高速

对应：

- [session-review-20260509-first-pass-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-first-pass-zh.md)
- [session-review-20260509-session3-route-read-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-session3-route-read-zh.md)

### 3. `Session 3` 后半出现了连续高价值区

最关键的 whole-file 高价值区是：

- [toyota_all_20260508_193747_008.ndjson](/D:/Temp/20260312/raw_can_logs/20260509/raw_can_logs/toyota_all_20260508_193747_008.ndjson)
- `03:37:47.838 -> 03:42:35.929`
- whole-file `Grade A`

这批不是只有零碎 pocket，而是真的有一块连续高价值区。

这对主线很重要，因为它说明：

- 新 log 不是只补 partial-seed
- 它已经给了我们一段更接近 joined-lifecycle 的 route-level 连续区域

对应：

- [session-review-20260509-session3-high-region-detailed-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-session3-high-region-detailed-zh.md)

### 4. `Session 3` 已经可以翻成事件级路况

当前最值得记的几段是：

- `03:38:12 -> 03:38:42`
  - 最像稳定跟车
- `03:39:37 -> 03:40:42`
  - 最像前车变道 / 换跟车目标后的重抓
- `03:40:29 -> 03:40:57`
  - 最像自动降速 / 跟车恢复
- `03:41:52 -> 03:42:25`
  - 最像靠右离开高速前的复杂调整

对应：

- [session-review-20260509-session3-event-table-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/session-review-20260509-session3-event-table-zh.md)

## 这批新 CAN LOG 还没有帮到什么

### 1. 还不能直接说 bridge-gap 已闭合

虽然 `Session 3` 后半很强，
但目前我们还没有把它正式判成：

- 明确已经高于 `171414`
- 又还没到 `190101`
- 并且足以充当新的 bridge-anchor

也就是说：

- **bridge-gap 有推进**
- **但还不能宣布 closed**

### 2. 还没有解决 secure/auth closure

这批让 `SecOC / key-state` 失败更清楚了，
但没有把：

- `SecOCKey`
- synchronization
- freshness / auth closure

直接解决掉。

### 3. 还没有让 steering physical-angle 闭合

我们现在在大转向区能看到：

- `0x260` control-side 数值明显变化

但这还不是：

- 已验证的物理方向盘角度
- 已验证的前轮转角

所以 steering 这条线还需要真正的实体 angle / torque signal 来闭合。

## 这代表主线状态怎么变了

之前：

- 等待新的 CAN LOG

现在：

- 新 CAN LOG 已到位
- 第一轮主线分析已完成
- 主线已经进入：
  - **新样本深化 / bridge定位 / 事件级路况映射阶段**

## 当前最合理的主线判断

### 已完成

- 新 `20260509` 样本已纳入主线
- `Session 1` 的 `SecOC / key-state` 异常线更清楚
- `Session 3` 的长 mixed-route 主段已识别
- `Session 3` 后半 `Grade A` 高价值区已识别
- `Session 3` 的事件级路况对照已建立

### 仍未完成

- bridge-gap closure
- `0x2E4` operational meaning
- secure/auth closure
- steering physical-angle closure

## 接下来主线最该怎么走

### 1. 先把 `20260509` 这批正式挂进 GitHub 主线

这一步的意义是：

- 让主线状态从“等待新 log”正式更新成“新 log 第一轮已完成”
- 也让伙伴能直接看到：
  - `Session 1`
  - `Session 3`
  - `Grade A` 区
  - 事件级对照表

### 2. 然后继续深切 `Session 3`

现在最值钱的下一层不是再扫整批，而是：

- 判断 `03:37:47 -> 03:42:35` 这块高价值区
- 到底只是 route-level joined zone
- 还是已经足以进入新的 bridge-tier 候选

### 3. 再决定 bridge-gap 有没有实质缩小

也就是：

- 它是不是终于比 `171414` 更完整
- 但又还没完全到 `190101`

这才是主线当前真正缺的判断。

## 一句话总结

**主线现在已经不再是“等待新 CAN LOG”，而是“`20260509` 新样本已进入主线，并且给出了一段真正值得继续深切的长 mixed-route 高价值主段”；但 bridge-gap 还没有到可以宣布闭合的程度。**
