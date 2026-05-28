# 被动分析主线 vs Key / Sync 限制（中文版）

## 这页要回答什么

这页要回答一个很核心的问题：

- 我们现在用大量 CAN log、`TSK-nearest`、`0x260` replay，到底已经做到什么？
- 为什么走到后面，还是会卡在：
  - `SecOCKey`
  - `freshness`
  - `synchronization`
  - `MAC`

## 最短答案

**被动分析可以帮我们找到“最接近受保护控制的状态和窗口”，但通常不能只靠它直接把 `SecOC key` 逆出来。**

如果受保护 ECU 真正要求：

- 正确 key
- 正确 freshness
- 正确 sync
- 正确 authenticator / MAC

那么：

- **没有 key 时，很多控制侧努力最后还是会被挡住**
- **只有 key，但 sync/freshness 不对，也一样会失败**

## 被动分析已经帮我们做到什么

### 1. 找到 passive backbone

我们现在已经收敛出：

- `0x116`
- `0x131`
- `0x2E4`

这条 `TSK-nearest` 主 backbone。

它的价值不是“直接给出 key”，而是：

- 告诉我们哪段 log 最接近 protected-lifecycle
- 告诉我们哪个样本只是 early seed-touch
- 哪个样本是 partial-ramp
- 哪个样本是 joined lifecycle anchor

### 2. 建立 `TSK-nearest` 梯子

我们现在已经能把样本排成：

- `185520`
- `173834`
- `184921`
- `171414`
- `190101`

也就是说，我们已经能看懂：

- 谁只是刚碰到门
- 谁开始往里走
- 谁已经最接近完整 lifecycle

这让后面不再是盲挖。

### 3. 找到 control-side anchor

目前 control-side 最稳的是：

- `0x260`

它让我们可以做：

- replay-backed simulation
- mapping branch 比较
- city / bridge / anchor 不同 regime 的控制侧比对

### 4. 找到一些局部规则

例如城市 `transition / settle` 这类窗口，我们已经不只是“看起来像”，而是已经有 replay-backed local working rule：

- `low-band catch-up 5.5x`
- `deeper-negative helper 2.5x`

这说明：

- 被动线并不是没用
- 它已经帮我们把控制侧理解推进到很深

## 被动分析做不到什么

### 1. 不能直接看到 ECU 内部的 key

CAN log 里你通常只能看到：

- payload
- 某些 sync / freshness 相关消息
- 某些认证失败现象

但你看不到：

- ECU 内部真实保存的 key
- key derivation
- freshness manager 的内部状态
- 验证策略细节

所以 log 分析再强，也不等于直接拿到钥匙。

### 2. 不能只靠相关性推出完整 MAC 机制

就算你看到：

- `SECOC_SYNCHRONIZATION`
- `MAC mismatch`
- 某些字段很像 freshness

你通常还是没法只靠这些就确定：

- MAC 算法
- key material
- truncation 长度
- sender / receiver 的同步窗口

### 3. 不能证明 ECU 最终会接受我们的注入

就算 control-side replay 很漂亮，
也不代表 ECU 会接受真实控制。

因为 ECU 接受与否，常常还取决于：

- key 对不对
- freshness 对不对
- sync 对不对
- packet packing 对不对

## 为什么 `SecOCKey missing` 很关键

如果日志里出现：

- `SecOCKey missing`

通常更像是：

- 系统这边根本没有可用 key
- 无法产生正确的认证信息
- 所以上层虽然尝试进入更深的 `LKAS / SecOC` 上下文
- 但最后会卡在验证层

这也是为什么我们现在对第一段 `fingerprint + LKAS Failed` 的判断更偏：

- `SecOC synchronization / key-state failure`

而不是：

- 单纯 `0x260` 控制逻辑失败

## `missing` 和 `wrong` 的差别

### `missing`

更像：

- 没有 key
- 没有可用认证材料
- 根本没法正确生成 MAC

### `wrong / invalid`

更像：

- 有放东西
- 但 key 不对
- freshness 不对
- sync 不对
- MAC 不对

两种情况，ECU 都可能不理你。  
只是诊断意义不同：

- `missing` = 没带钥匙
- `wrong` = 带了钥匙，但拿错把

## 这对我们现在的项目意味着什么

### 意味着 1：被动主线仍然必要

虽然它不给 key，
但它帮我们：

- 找到最接近 protected-state 的窗口
- 缩小 active validation 目标面
- 区分哪些样本只是 control-side 参考
- 哪些样本真的更接近 `TSK-nearest`

### 意味着 2：最后还是会碰到 key / sync 问题

如果最终目标是：

- 让 ECU 接受受保护控制

那最后通常还是要面对：

- key 从哪里来
- freshness 怎么同步
- authenticator 怎么算
- receiver 什么时候开始验证

### 意味着 3：现在不要把 replay 结果讲太满

我们现在可以说：

- 有 replay-backed control-side main branch
- 有 city-side local working rule

但还不能说：

- 已经 implementation-ready
- 已经 injection-ready
- 已经完成 SecOC closure

## 一句话总结

**被动分析已经帮我们把“最接近受保护控制的状态”找出来了，但它通常不能单独把 `SecOC key` 变出来；如果没有正确的 key、freshness 和 synchronization，受保护 ECU 很可能还是不会接受我们的控制。**
