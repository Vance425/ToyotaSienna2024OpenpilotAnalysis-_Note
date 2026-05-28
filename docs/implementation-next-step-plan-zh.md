# 进入实作阶段：下一步该怎么做

## 先讲结论

**不是只继续收集 CAN logs。**

如果现在前提是：

- `TSK` 已确认
- passive backbone 已够稳

那接下来应该改成：

1. **少量、目的明确的 CAN log 收集**
2. **active / direct branch 的 dump-only 导出**
3. **secure/auth 闭合验证**
4. **最小 protected message set 验证**

也就是说：

- CAN log 仍然有用
- 但已经不是主角
- 现在主角应该是：
  - `dump`
  - `sync`
  - `MAC`
  - `acceptance`

## 现在不该再做什么

### 1. 不该再把主时间花在“多收一些普通路况 CAN log”

因为：

- `TSK-nearest` backbone 已经够清楚
- `190101` anchor 已经有
- `20260509 Session 3` 也已经把 bridge-tier 缩得更近

所以现在再收很多普通路况 log，边际价值会下降。

### 2. 不该只停在 replay / passive 对照

因为：

- passive 已经帮你把路找出来了
- 真正卡住你的已经不是“看懂”
- 而是“怎么让 ECU 接受”

## 现在最值得做的 4 条线

## 1. 保留少量 CAN log 收集，但改成“验证型收集”

以后收 log 的目标，不再是“多收一点看看”。

而应该只收这几类：

- fingerprint + `LKAS Context` + `LKAS Failed`
- active direct branch 前后对照
- sync 成功 / sync 失败对照
- candidate key / candidate packing 变化前后对照

也就是：

- **收能验证某个假设的 log**
- 不收只是增加 corpus 体积的 log

## 2. 先做 dump-only 实作

这是现在最值得先写、先跑、先稳定的东西。

目标：

- 稳定导出：
  - transcript
  - metadata
  - raw dump

最小输出建议固定成：

```text
out/secoc_dump_YYYYMMDD_HHMMSS/
  transcript.jsonl
  metadata.json
  dump_xxxxx.bin
  dump_summary.txt
```

这一步的重点不是：

- 立刻拿到正确 key

而是：

- 每次 active attempt 都留下可比较、可回放的原始证据

## 3. 然后做 candidate parser

等 dump-only 稳后，下一步就是 parser。

parser 的目标：

- 从 dump 中找：
  - key-like structure
  - candidate offsets
  - checksum hypothesis
  - layout hypothesis

输出建议：

```text
candidate_report.md
candidate_keys.csv
layout_hypotheses.json
```

## 4. 最后才做 acceptance 验证

拿到 candidate key 后，真正的实作顺序应该是：

1. 验证 key 是否有效
2. 验证 freshness / sync
3. 验证 MAC / packing
4. 验证最小 protected message set
5. 做 bounded ECU acceptance

这一步才真正开始接近：

- “能不能让 2024 Sienna 接受 C3X 控制”

## 你现在最实作的做法

如果你现在就要开始动手，我建议按这个顺序：

### Phase 1：把主动尝试可重复化

做：

- `dump-only` 脚本
- 固定 metadata 格式
- 固定 transcript 格式

目标：

- 每次 direct 尝试都能留下完整证据

### Phase 2：把 dump 变成可分析资产

做：

- candidate parser
- layout hypothesis
- candidate key 报表

目标：

- 不再只看到 `0000...`
- 而是能比较“哪段像新结构”

### Phase 3：做最小 acceptance

做：

- key candidate
- sync/freshness
- MAC packing
- 最小 protected frame set

目标：

- 看 ECU 会不会接受

### Phase 4：再谈 openpilot / C3X 整合

做：

- Panda safety
- sender / packer
- startup / shutdown
- fault handling

## 所以你现在到底还要不要继续收 CAN logs

要，但要**收得更少、更准**。

### 该收的

- active/direct 尝试前后对照 log
- sync 失败 / 成功切换 log
- LKAS fault context log
- bounded acceptance test log

### 不该大量再收的

- 纯普通跟车
- 纯一般市区
- 没有新验证目标的长 route

## 最短路线

如果你问我：

> 现在进入实作，我第一步到底该做什么？

我的答案是：

**先不要把主力放在继续大量收 CAN logs。**

**先把 direct branch 改造成 `dump-only + parser` 这条稳定导出链。**

因为这一步才最接近真正打开：

- `SecOCKey`
- sync
- acceptance

这几层门。

## 一句话总结

进入实作阶段后，CAN log 仍然要收，但应该从“探索型收集”切换成“验证型收集”；真正最该优先做的，是把 direct branch 先收成一条稳定的 `dump-only -> parser -> acceptance` 导出链。
