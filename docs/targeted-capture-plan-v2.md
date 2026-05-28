# Targeted Capture Plan v2

## 目的

基于当前 `Grade A / B / C / D` 规则，优先录最有机会复现：

- `Grade A: Full Match`
- `Grade B: Partial Seed`

的实车场景。

## 优先级 1

### 长时间连续驾驶

目标：

- 复现 `190101` 这类长段内才出现的 top-tier cluster

建议条件：

- 单段连续录制尽量长
- 不要频繁重启 logger
- 保留完整 `IGN_ON` 段

原因：

- 当前唯一 `Grade A` 出现在长段 [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

## 优先级 2

### 多种速度变化但不中断 session

目标：

- 看 `top-tier lifecycle` 是否与特定 driving state 切换有关

建议包含：

- 低速稳定
- 中速巡航
- 加速
- 减速

要求：

- 尽量在同一段 `IGN_ON` 内完成

## 优先级 3

### 方向输入明显变化的路段

目标：

- 利用 `0x610` event anchor 增加 family event band 机会

建议包含：

- 直线
- 缓弯
- 连续转向修正

## 优先级 4

### 驾驶辅助状态切换

目标：

- 看 `0x131 / 0x260 / 0x116` 是否会在辅助系统状态变化时更容易进入 deep climb

建议记录：

- 开启前
- 切换当下
- 切换后 30-60 秒

## 低优先级

### 短段、频繁重启、零散片段

原因：

- 容易只得到 `Partial Seed`
- 很难形成完整 lifecycle

## 录制时最需要保留的元数据

每段至少记：

- 开始时间
- 结束时间
- 路况类型
- 是否有明显转向
- 是否有速度变化
- 是否切换驾驶辅助
- 是否出现 `comma 3X` 相关提示

## 当前最实际的录制目标

如果只能选一种新录法，优先做：

- 一段更长的连续 `IGN_ON` driving log
- 中间包含速度变化和方向变化
- 尽量不要中断
