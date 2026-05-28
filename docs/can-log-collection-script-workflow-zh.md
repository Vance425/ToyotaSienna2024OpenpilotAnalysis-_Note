# CAN Log 收集 Script 與 Workflow 說明

結論先寫清楚：目前 repo 裡已有完整的 log 分析 scripts、capture checklist / workflow 文件，也補上了當時 C3X 端 `START LOG` 實際使用的 raw CAN logger。

公開版 repo 不保存 raw CAN `.ndjson` logs，也不保存 C3X context log 原始輸出。這類資料只保留在本機或私有 archive。

## 目前保留的內容

- `scripts/grade_can_logs.py`
- `scripts/generate_log_feature_table.py`
- `scripts/scan_longitudinal_event_ids.ps1`
- `scripts/capture/toyota_full_bus_logger_seed_hunter_v3_3.py`
- `scripts/capture/README.md`
- `docs/tsk-bridge-capture-checklist-zh.md`
- `docs/new-log-standard-workflow.md`
- `docs/log-capture-program-change-recommendation.md`

## 各檔案角色

`scripts/capture/toyota_full_bus_logger_seed_hunter_v3_3.py` 是 C3X 端 legacy tool API 的 `START LOG` 所啟動的 raw CAN logger。它直接使用 Panda，輸出 continuous 與 ignition-segmented `.ndjson` raw CAN logs。

`grade_can_logs.py`、`generate_log_feature_table.py`、`scan_longitudinal_event_ids.ps1` 是針對 raw CAN `.ndjson` 的離線分析工具，不是車上 logger。

capture checklist / workflow 文件用來定義要收哪些 session、marker 怎麼標、IGN/LKAS/ACC 狀態如何切段，以及後續怎麼把 raw log 轉成分析輸出。

## Legacy API 啟動路徑

當時 phone UI 的 `START LOG` 會呼叫：

```text
POST /tools/jobs/start_logger/run
```

在 C3X 上，job 設定來自：

```text
/data/tools/mySienna_api/config/jobs.json
```

`start_logger` job 會執行：

```text
/data/tools/start_logger.sh
```

而 `start_logger.sh` 實際啟動：

```text
/data/tools/toyota_full_bus_logger_seed_hunter_v3.3.py
```

公開 repo 中對應檔案是：

```text
scripts/capture/toyota_full_bus_logger_seed_hunter_v3_3.py
```

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
