# Cross-Log Candidate Ranking (2026-03-14)

## 目的

把前面做好的 event-band 模板，拿去對比多段 `IGN_ON` 實車 log，找出最像 `comma 3X` 失敗邊界或 `TSK / SecOC` 狀態切換的窗口。

本輪模板條件：

1. `0x610` 出現事件點
2. `0xD5` 在同窗口內維持不變
3. `0x131` 出現 reset-like prefix 行為
4. `0x116` 出現 phase change
5. `0x260` 出現 prefix change

## 目前排序

### Tier 1: 最值得先深挖

- Log: [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)
- Best anchor: `1773255299671`
- Template score: `4/4`

判讀：

- `0x610` 有明確 anchor
- `0xD5` 在窗口內維持固定 `08000000000000e5`
- `0x131` 從 `003c... / 003e... / 003f...` 轉成 `0001... / 0004... / 0005... / 0007...`
- `0x116` prefix 出現明顯 phase 遞進：`09 -> 0a -> 0d`
- `0x260` 在同窗口有結構化 prefix 推進

結論：

這段比前面 `184714` 更像完整的跨邊界事件帶，值得當成下一份主要示範 log。

### Tier 2: 有事件邊界，但較不像完整 protected phase

- Log: [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)
- Best anchor: `1773255027173`
- Template score: `4/4`

判讀：

- 這段已經證明模板有效
- 很適合當教學示範
- 但目前更像 steering/state event band 的乾淨樣本

結論：

它是目前最好的基準樣本，但未必最像 `comma 3X` 失敗邊界。

### Tier 3: 有邊界感，但 `0x116` 不夠強

- Log: [toyota_seg_IGN_ON_20260311_184714_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184714_000.ndjson)
- Best anchor: `1773254840727`
- Template score: `3/4`

判讀：

- `0x131` 有 reset-like 行為
- `0x260` 有 prefix change
- `0xD5` 維持固定 `00000000000000dd`
- 但 `0x116` 沒有明顯 phase 遞進，prefix 幾乎維持 `00`

結論：

它像跨狀態切換，但不像強 protected phase 候選，不應排在 `185451` 前面。

## 目前最實用的結論

如果現在只能先挑一段往下鑽，優先順序應該是：

1. `185451`
2. `184921`
3. `184714`

原因不是 `185451` 分數獨占，而是它同時具備：

- 清楚的 `0x610` anchor
- 完整的 `0x116` phase change
- 明確的 `0x131` reset-like 行為
- 穩定不動的 `0xD5`

這組合更像我們之後要拿來對照 `comma 3X` 失敗前後的模板。

## 下一步

下一份最值得寫成完整人工判讀的是：

- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)

建議窗口：

- `1773255299471` to `1773255299871`
- anchor: `1773255299671`
