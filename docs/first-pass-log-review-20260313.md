# 第一輪 CAN Log 檢視

## 來源

- 壓縮檔：`<LOCAL_RAW_CAN_LOG>.zip`
- 已解壓到：`<LOCAL_ANALYSIS_WORKSPACE>\analysis-input\raw_can_logs`

## 這批資料包含什麼

### 原始 log

- 多份 `toyota_all_*.ndjson`
- 多份 `toyota_seg_IGN_ON_*.ndjson`
- 多份 `toyota_seg_UNKNOWN_*.ndjson`

### 摘要 / 工具輸出

- `events.jsonl`
- `uds_events.jsonl`
- `uds_rankings.json`
- `uds_scan_results.csv`
- `security_ecu_guess.json`
- `seed_key_pairs.csv`
- `seed_hunter_v5_1.log`
- `toyota_seed_hunter_v5.log`
- `toyota_hotkeyd.log`

## 第一輪結論

### 1. 目前沒有抓到有效的 seed/key

從以下檔案可看出來：

- `seed_key_pairs.csv` 只有表頭，沒有資料
- `security_ecu_guess.json` 是空物件
- `secoc_frames.json` / `counter_candidates.json` / `seed_clusters.json` 都是空

這代表目前流程不是「拿到 seed 但還沒算出 key」，而是更早就沒有形成有效 security 對話。

### 2. UDS 掃描有執行，但全部 timeout

`uds_events.jsonl` 顯示：

- bus `0`、`2` 都對 `0x7a1/0x7a9`、`0x750/0x758`、`0x760/0x768`、`0x7e0/0x7e8`、`0x7e1/0x7e9`、`0x7b0/0x7b8`、`0x7c0/0x7c8` 做了掃描
- session 與 `security_access` 嘗試全部是 `timeout`

這代表目前不是單一 ECU 沒回，而是整個目標集合都沒有得到有效回覆。

### 3. 更上游的問題：主記錄流程裡 `uds_enabled` 是 `false`

`events.jsonl` 每次 `start` 幾乎都顯示：

- `uds_enabled: false`
- `uds_bus: 1`
- `uds_tx: 0x7e0`
- `uds_rx: 0x7e8`

這是這批資料最重要的訊號之一。

意思是：

- 主要 raw CAN log 錄製流程是被動記錄
- 並沒有在主流程中真正啟動 UDS security 抓取
- 所以 raw log 本身不太可能直接包含完整的主動 security negotiation

### 4. 工具鏈也有缺件跡象

`toyota_hotkeyd.log` 顯示：

- `watcher not found: <C3X_TOOLS_PATH>/toyota_logger_hotkeyd.py`

這代表至少有一個依賴腳本沒有在裝置端正確就位。

這很可能導致：

- 你以為某些採集或觸發機制有啟動
- 但實際上根本沒有完整執行

### 5. bus 0 與 bus 2 看起來高度鏡像，bus 1 比較值得深挖

以 `toyota_seg_IGN_ON_20260311_185451_000.ndjson` 為例：

- bus 0: `28065` frames
- bus 1: `21340` frames
- bus 2: `28079` frames

其中：

- bus 0 和 bus 2 的高頻 CAN ID 幾乎相同
- bus 1 的高頻 CAN ID 分布明顯不同

這代表後續如果要找 security 相關流程，`bus 1` 很可能更值得優先分析。

## 目前最合理的判斷

你現在卡住的原因，不只是「沒有 TSK」本身，而是：

1. `comma 3X` 自動抓取失敗
2. 目前的主記錄流程沒有真的啟用 UDS security 流程
3. 你後面補跑的 seed hunter 也沒有打中真正會回應的 ECU / bus / 路徑

所以現階段最需要先確認的不是 key 演算法，而是：

- 到底哪個 bus / ECU / gateway 路徑才是真正會回 security 的目標

## 下一步建議

### 第一優先

重新建立一批「有明確主動探測意圖」的 log：

- 明確標記哪一次有跑 UDS / seed hunter
- 明確標記目標 bus
- 明確標記目標 ECU
- 明確記錄失敗訊息與時間點

### 第二優先

把分析重點從 bus 0 / 2 的鏡像流量移到：

- bus 1
- 點火狀態切換瞬間
- `comma 3X` 介入前後

### 第三優先

先確認工具鏈完整性：

- `toyota_logger_hotkeyd.py` 是否真的部署在裝置端
- seed hunter 是否真的對預期 bus 發包
- 掃描時的 tx/rx 配置是否正確

## 這一輪可以確定的事

- 目前這批資料還不足以直接導出 `TSK`
- 但足以確認目前的自動流程沒有真正打到有效 security 對話
- 所以下一輪要優先修正的是「採集與探測方式」，不是直接猜 key
