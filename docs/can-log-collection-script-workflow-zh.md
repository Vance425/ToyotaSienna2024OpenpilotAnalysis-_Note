# CAN Log 收集 Script 與 Workflow 說明

結論先寫清楚：目前 repo 裡有完整的 log 分析 scripts，也有 capture checklist / workflow 文件；但「車上原始 CAN logger 本體」不是以一支明確命名的 standalone script 放在 repo 裡。

公開版 repo 不保存 raw CAN `.ndjson` logs，也不保存 C3X context log 原始輸出。這類資料只保留在本機或私有 archive。

## 目前保留的內容

- `scripts/grade_can_logs.py`
- `scripts/generate_log_feature_table.py`
- `scripts/scan_longitudinal_event_ids.ps1`
- `docs/tsk-bridge-capture-checklist-zh.md`
- `docs/new-log-standard-workflow.md`
- `docs/log-capture-program-change-recommendation.md`

## 各檔案角色

`grade_can_logs.py`、`generate_log_feature_table.py`、`scan_longitudinal_event_ids.ps1` 是針對 raw CAN `.ndjson` 的離線分析工具，不是車上 logger。

capture checklist / workflow 文件用來定義要收哪些 session、marker 怎麼標、IGN/LKAS/ACC 狀態如何切段，以及後續怎麼把 raw log 轉成分析輸出。

## 原始 logger 尚缺的明確文件

目前還缺一份專門描述 raw CAN logger 的文件，應補上：

- logger 是在 C3X、laptop 還是 Panda 端執行
- `.ndjson` schema
- bus / addr / timestamp / payload 欄位定義
- `toyota_all_*` 與 `toyota_seg_IGN_ON_*` 的命名規則
- `IGN_ON / IGN_OFF / ACC_ON / LKAS_ON` marker 規則
- session continuity 檢查方式

## `.ndjson` 建議格式

```json
{
  "bus": 0,
  "addr": 740,
  "ts_ms": 1770000000000,
  "data": "cc000000717ea22c"
}
```

核心欄位：

- `bus`
- `addr`
- `ts_ms`
- `data`

## Note repo 範圍

`ToyotaSienna2024OpenpilotAnalysis_Note` 不保存 raw `.ndjson` logs，也不保存 context log 原始輸出。公開版只保留 workflow、log spec、analysis scripts、analysis output，以及不含 raw key 的 SecOC validation 文件。
