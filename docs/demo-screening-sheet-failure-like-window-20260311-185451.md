# Screening Sheet: Failure-Like Candidate Window

## 基本資料

- Log: [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)
- State: `IGN_ON`
- Window: `1773255299471` to `1773255299871`
- Anchor: `1773255299671`

## Anchor 條件檢查

- `0x610` event point: `True`
- `0xD5` unchanged: `True`
- `0x131` reset-like: `True`
- `0x116` phase change: `True`
- `0x260` prefix change: `True`

## 快速判讀

- `0x131`: 強 reset-like
- `0x116`: 強 phase candidate
- `0x260`: 強 core family candidate
- `0x115`: 中度伴隨候選
- `0xD5`: 穩定參考線
- `0x610`: 事件 anchor

## 本輪結論

- 這是目前最值得深挖的 failure-like candidate window
- 如果下一步要做 bytes 級人工比對，先從 `0x116` 和 `0x131` 開始
- 如果要做跨 log 模板比對，先拿這個窗口當新基準
