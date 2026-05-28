# Toyota Sienna TSK 專案到目前的結論

日期：

- `2026-05-25`

## 最短版結論

**`2024 Toyota Sienna` 的 `TSK` 路徑已確認，`C3X` 橫向也已在實車上正常工作；目前專案不再卡在「能不能控制」，而是卡在「怎麼把 secure/auth 與 acceptance 路徑穩定導出並固化」。**

## 到目前為止可以很穩地說的事

### 1. `TSK-nearest` 主 backbone 已確認

目前最穩的 passive backbone 是：

- `0x116`
- `0x131`
- `0x2E4`

### 2. Top-tier anchor 已固定

目前最強 anchor 仍然是：

- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](/D:/Temp/20260312/raw_can_logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

### 3. Bridge-gap 已縮小，但尚未正式 closed

`20260509 Session 3` 已經把：

- `171414`
- 到
- `190101`

之間的空間明顯縮小。

目前最合理的說法是：

- **route-level bridge-tier candidate**

但還不能直接升成：

- top-tier anchor
- 或 bridge-gap fully closed

### 4. `0x260` 是最穩的 control-side anchor

而且 replay-backed main branch 已經很清楚：

- `no_b1_flip + identity + higher slew`

### 5. 舊 direct `extract_keys` 分支不是完全死掉

它比較像：

- 前半 diagnostic / unlock / download / payload path 能走很深
- 但最後 dump range / layout / parser 不再適合 `2024 Sienna`

### 6. `C3X` 橫向已能在 `2024 Sienna` 上正常工作

這是目前最重要的實作里程碑之一。

它代表：

- secure/auth / protected path 至少已有一條可用橫向鏈

## 到目前還不能過度宣稱的事

### 1. 不能說 secure/auth 已完全閉合

因為還沒正式完成：

- key 有效性 closure
- sync / freshness closure
- MAC / packing closure

### 2. 不能說 final implementation mapping 已定案

因為 current mapping 仍然偏：

- replay-backed working branch

### 3. 不能說 openpilot / C3X 全部功能都已 ready

目前最穩的是：

- 橫向已可用

但仍需確認：

- acceptance
- stability
- safety
- fault recovery
- 其它功能路徑

## 现在真正的专案重心

如果只用一句话说：

**现在主重点已经不是再证明 `TSK`，而是把 direct branch 做成稳定的导出链，并把 secure/auth acceptance 路径走通。**

## 目前最合理的下一步

1. 收验证型 logs，不再大量扩普通 corpus
2. 做稳定 `dump-only`
3. 做 `candidate parser`
4. 做 key / sync / MAC / message-set acceptance 验证
5. 固化 `C3X` 横向成功路径与异常回退

## 一句话总结

**到目前为止，这个项目已经从“研究 `TSK` 是什么”进入“如何把 `TSK / SecOC / acceptance` 变成可重复实作路径”的阶段。**

## 参考

- [research-update-20260525-zh.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/research-update-20260525-zh.md)
- [current-findings-summary-v2.md](/D:/Codex/toyota-sienna-tsk-analysis/practical/current-findings-summary-v2.md)
- [OPENPILOT_INTEGRATION_PROGRESS_REPORT.md](/D:/Codex/toyota-sienna-tsk-analysis/OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)
