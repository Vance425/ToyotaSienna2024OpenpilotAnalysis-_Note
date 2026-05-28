# 2024 Sienna `extract_keys` 失败层分析（中文版）

## 这页要回答什么

这页只回答一个问题：

- 为什么旧 `extract_keys` 在 `2024 Sienna` 上前半段看起来跑通了，
- 但最后还是没有拿到可用的 `SecOC Key`？

## 结论先讲

**从现有输出看，这次失败不像卡在最前面的 UDS / SecurityAccess，反而更像卡在 dump 区域、key 结构或 parser 假设这一层。**

更白话地说：

- 前半段很多关键步骤是成功的
- 但最后读出来的内容，不像旧脚本以为的那种 key table
- 所以最后才会变成：
  - `0000...`
  - checksum fail
  - `KEY_1 / KEY_4` 无效

## 对应原始输出

- secoc_getKey_result20241124.txt (local-only external source path)
- extract_keys.py (local-only external source path)
- [old-secoc-tsk-method-explained.md](old-secoc-tsk-method-explained.md)
- [old-secoc-method-likely-broken-points.md](old-secoc-method-likely-broken-points.md)

## 第 1 层：目标 ECU / 版本识别

### 观察到的结果

- 成功读到 application version：
  - `8965B4514000`
- 成功读到 bootloader version：
  - `\x02!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!`

### 判断

- 这说明：
  - 目标 ECU 有回应
  - 版本 gating 没有在最前面失败
- 所以问题不像：
  - `0x7A1` 完全不对
  - 或一开始就版本不匹配

### 结论

- **这一层看起来成功**

## 第 2 层：诊断 session 切换

### 观察到的结果

脚本依次成功走了：

- `0x1001`
- `0x1003`
- `0x1002`

并收到了：

- `0x50 01`
- `0x50 03`
- `0x50 02`

虽然 `0x1002` 中间有：

- `0x7F 10 78`

但随后继续拿到了正响应。

### 判断

- 这表示：
  - default / extended / programming session 路径至少在这次尝试里是通的

### 结论

- **这一层看起来成功**

## 第 3 层：Security Access

### 观察到的结果

脚本：

- 请求 seed
- 打印：
  - `SEED: 871b833d...`
  - `KEY: 7c9e2d15...`
- 发出 send key
- ECU 回：
  - `0x6702`
- 脚本打印：
  - `Key OK!`

### 判断

- 这表示：
  - 当前脚本里的 seed-key 路径至少在这次尝试里成功过了
- 所以问题不像：
  - 一开始就卡在 `SecurityAccess`

### 结论

- **这一层看起来成功**

## 第 4 层：下载前准备

### 观察到的结果

脚本成功写了：

- DID `0x203`
- DID `0x201`
- DID `0x202`

都收到了正响应：

- `0x6E 0203`
- `0x6E 0201`
- `0x6E 0202`

### 判断

- 这说明旧流程里要求的前置状态在这次也没有直接被拒绝

### 结论

- **这一层看起来成功**

## 第 5 层：payload 上传

### 观察到的结果

脚本成功完成：

- `RequestDownload`
- `TransferData 0..3`
- `RequestTransferExit`

响应都正常，虽然 `TransferData` 中间有 `0x7F 36 78` 的 pending，但最终都回：

- `0x7601`
- `0x7602`
- `0x7603`
- `0x7604`

### 判断

- 这说明：
  - payload 并不是完全没上去
  - 下载路径至少没有在这里直接断掉

### 结论

- **这一层看起来成功**

## 第 6 层：payload 验证 / 触发

### 观察到的结果

- routine `0x10F0` 成功
- 脚本打印：
  - `Routine control 0x10f0 OK!`
- 然后进入：
  - `Trigger payload...`
  - `Dumping keys...`

### 判断

- 这说明：
  - 至少从脚本视角，payload 不只是上传了，还被“触发到开始 dump”

### 结论

- **这一层至少部分成功**

## 第 7 层：memory dump 本体

### 观察到的现象

dump 出来的地址从：

- `0xFEBE6E34`
- 一直到：
  - `0xFEBE6FF0` 左右

但内容并不是旧 parser 期待的那种稳定 key table。

你可以直接看到：

- 前半大量 `00 00 00 00`
- 中间夹着一些：
  - `5A 5A`
  - `22 22`
  - `01 00 00 00`
  - `1A 00 00 00`

### 为什么这不太像“正常 key structure”

旧脚本期待的是：

- 每个结构长度 `0x20`
- checksum 可验证
- key 偏移固定
- `KEY_1` / `KEY_4` 能切出来

但现在看到的是：

- 结构很不干净
- pattern 很像：
  - 占位
  - 状态字
  - 边界标记
  - 或其它非 key table 区数据

### 结论

- **最可疑的第一层失真，就在这里**

## 第 8 层：旧 parser 解释

### 观察到的结果

脚本最后输出：

- `key_1_ok False`
- `key_4_ok False`
- `__ECU_MASTER_KEY 000...000`
- `__SecOC Key (KEY_4) 000...000`
- `SecOC key checksum verification failed!`

### 正确解释

这不应直觉解读成：

- 车上没有 key

更合理的解释是：

- 旧 parser 期待的结构不成立
- 所以它切出来的“key”只是错误偏移上的零值

### 结论

- **`0000...` 更像 parser/结构失败的结果，不像真正证明“没有 key”**

## 最可能的失败原因树

### 可能性 A：dump 区间错了

意思是：

- payload 确实在跑
- 但 `0xFEBE6E34 -> 0xFEBE6FF4` 已经不是新车正确 key table 区

### 可能性 B：key structure layout 变了

意思是：

- 区域可能还接近对
- 但：
  - 结构大小变了
  - checksum 规则变了
  - key 偏移变了
  - `KEY_4` 不再是 SecOC key

### 可能性 C：payload 只部分成功

意思是：

- 流程走到 dump
- 但读取的数据并不是目标 key table，而是邻近区或不完整区

### 可能性 D：2024 车系多了一层保护

意思是：

- key 不再像旧车那样直接以同样结构放在同样位置
- 可能有额外包装、间接引用或运行时派生

## 当前最稳的阶段判断

### 可以先认为“成功”的

- target ECU 有回应
- session path 通
- `SecurityAccess` 通
- DID 写入通
- download path 通
- payload 至少部分被触发

### 当前最可疑的失败层

- **dump 区域 / memory layout / parser 假设**

## 这对现在项目的意义

这说明：

- 旧 direct branch 不是“完全死在最前面”
- 它更像：
  - **走到中后段才开始失真**

所以如果未来真的要重开 direct branch，
最该重验的不是：

- 单纯再跑一次旧脚本

而是：

1. dump range 对不对
2. key structure layout 还在不在
3. parser 规则要不要重写
4. payload 有没有真的跑到目标区

## 一句话总结

**这次 `2024 Sienna` 的 `extract_keys` 结果，更像是“UDS / unlock / download 流程大致跑通了，但最后 dump 到的区域或结构已经不再符合旧车假设”，所以旧 parser 才会把结果解释成全 0 并 checksum fail。**
