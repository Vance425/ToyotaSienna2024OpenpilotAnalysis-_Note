# 伙伴阅读顺序（中文版）

## 目的

这份是给新加入的伙伴看的最短阅读顺序。

目标不是一次看完全部文档，而是先用最少的材料建立正确心智模型，再决定要不要往更深的 log / script / direct branch 看。

---

## 最短路线

如果时间很少，先看这 5 份：

1. [current-findings-summary-v2.md](./current-findings-summary-v2.md)
2. [final-frame-role-map.md](./final-frame-role-map.md)
3. [tsk-nearest-ladder-entry-to-anchor.md](./tsk-nearest-ladder-entry-to-anchor.md)
4. [passive-tsk-nearest-overview-zh.md](./passive-tsk-nearest-overview-zh.md)
5. [next-log-analysis-template.md](./next-log-analysis-template.md)

看完这 5 份，基本就会知道：

- 现在项目主线是什么
- `TSK-nearest` 是怎么定义的
- 当前最强样本是谁
- 新 log 一来要怎么判

---

## 第二层：理解 companion / city / freeway / special-band

如果要继续理解 `0x260 / 0x191` 这条 control / companion 线，再看：

1. [final-companion-classification-table.md](./final-companion-classification-table.md)
2. [city-vs-highway-companion-reading-table.md](./city-vs-highway-companion-reading-table.md)
3. [20260314-175006-lane-change-transition-candidate.md](./20260314-175006-lane-change-transition-candidate.md)
4. [20260312-190101-disengage-suspect-bands.md](./20260312-190101-disengage-suspect-bands.md)

这层的重点是：

- `0x191` 不是单一固定字段
- 不同 regime 要用不同 companion 读法
- `lane-change transition` 和 `disengage suspect` 要分开

---

## 第三层：理解 TSK-nearest 旧样本梯子

如果要看“为什么现在说 `190101_000` 是 anchor”，再按这个顺序看：

1. [20260312-185520-protected-lifecycle-read.md](./20260312-185520-protected-lifecycle-read.md)
2. [20260314-173834-protected-lifecycle-read.md](./20260314-173834-protected-lifecycle-read.md)
3. [20260311-184921-protected-lifecycle-read.md](./20260311-184921-protected-lifecycle-read.md)
4. [20260315-171414-protected-lifecycle-read.md](./20260315-171414-protected-lifecycle-read.md)
5. [grade-a-golden-sample.md](./grade-a-golden-sample.md)

这样看最容易理解：

- seed-touch only
- ramping bridge
- compact ramping partial
- strongest older partial-ramp
- top-tier joined lifecycle anchor

---

## 第四层：理解 direct branch 和它为什么还不能直接用

如果伙伴会问：

- “那为什么不直接拿 key？”
- “旧 secoc 方法不能直接套吗？”

就看：

1. [old-secoc-direct-branch-overview.md](./old-secoc-direct-branch-overview.md)
2. [direct-tsk-branch-minimum-validation-order.md](./direct-tsk-branch-minimum-validation-order.md)
3. [direct-tsk-branch-decision-note-zh.md](./direct-tsk-branch-decision-note-zh.md)
4. [passive-log-model-to-tsk-extraction-roadmap.md](./passive-log-model-to-tsk-extraction-roadmap.md)

这层的重点是：

- passive path 不会直接吐出 TSK
- 但它会把 direct branch 缩到更小的目标面

---

## 第五层：公开资料参考

如果伙伴想先对照外部世界，再看：

1. [public-references-map-zh.md](./public-references-map-zh.md)
2. [public-references-map.md](./public-references-map.md)

这层适合回答：

- 外部有没有类似案例
- 什么是 direct TSK 公开路线
- 什么是 SecOC 结构参考
- 什么是社群现实旁证

---

## 最短说明给伙伴

如果只要一段话说明现状，可以直接用：

```text
目前主线不是 direct TSK extraction，而是 regime-first 的 passive CAN reverse。
最接近 TSK 的被动主线是 0x116 + 0x131/0x116 lifecycle + 0x2E4 side channel。
0x260/0x191 主要用于 control / companion / local regime 理解。
当前最强被动 anchor 是 20260312_190101_000，但还缺一个比 171414_000 更完整、又还没到 190101_000 的 bridge sample。
```

---

## 一句话

如果伙伴只看一小时，就让他按：

- 主摘要
- frame role map
- TSK-nearest 梯子
- passive overview
- next-log template

这条线读，不要一开始就陷进单篇局部 memo。
