# 第二輪採集計畫

## 目標

重新取得一批真正能支撐 `TSK` 研究的被動 log。

這一輪的核心不是多錄，而是：

- 確認場景切換被完整錄到
- 確認 `comma 3X` 失敗前後窗口被完整保留
- 確認每一份 log 都有清楚場景與時間點

## 第一輪暴露出的問題

- 主流程裡 `uds_enabled` 為 `false`
- `seed_hunter` 有跑，但候選 ECU 幾乎全部 `timeout`
- `toyota_logger_hotkeyd.py` 缺失
- 目前資料不足以定位真正的 security 路徑

## 第二輪成功條件

至少達成以下其中兩項：

- 能穩定重現相同場景的 frame 變化
- 能把可疑 frame 縮小到少數 ID
- 能看到 `comma 3X` 失敗前後的候選 frame 模式改變
- 能把 `bus 1` 的可疑窗口縮小到少數訊息群

## 採集前檢查

- [ ] 確認裝置端腳本完整存在
- [ ] 確認 `toyota_logger_hotkeyd.py` 或等效 watcher 已部署
- [ ] 確認這次要跑的 logger / hunter 指令版本
- [ ] 確認會記錄 `events.jsonl`
- [ ] 確認會輸出 `uds_events.jsonl`
- [ ] 確認能分辨本次資料夾與上一輪資料夾

## 建議採集批次

### Batch A: Baseline

目的：

- 建立完全不主動探測的車況 baseline
- 對照哪些訊息是車自己發的

條件：

- 不做 seed hunter
- 不做 security 掃描
- 只錄原廠上電、IGN on、Ready、ACC on/off

建議長度：

- 每段 30 到 60 秒

### Batch B: comma 3X fail path baseline

目的：

- 在不主動發 seed 的前提下，錄到 `comma 3X` 失敗前後的自然流量
- 建立與 Batch A 的差異比對

條件：

- 接上 `comma 3X`
- 明確標記開始嘗試的時間點
- 明確標記錯誤出現的時間點

### Batch C: State transition focus

目的：

- 看 `0x116 / 0x177 / 0x260` 與 `bus 1` 是否在狀態切換時出現可疑變化

條件：

- `IGN off -> IGN on`
- `IGN on -> Ready`
- 原廠 `ACC on/off`
- 原廠 `ADAS on/off`

### Batch D: bus comparison

目的：

- 對照 `bus 0 / bus 1 / bus 2` 在同一場景下的差異

條件：

- 同一場景連續保留三個 bus
- 優先選擇 `IGN on` 與 `comma 3X` fail path

## 每次只改一個變因

這一輪最重要的規則：

- 不要同時改 bus、ECU、腳本版本、車輛狀態
- 一次只動一個變因
- 不然很難知道哪個因素真的造成差異

## 推薦順序

1. 先重錄 `Baseline`
2. 再錄 `comma 3X fail path baseline`
3. 再錄 `State transition focus`
4. 最後做 `bus comparison`

## 命名規則

建議每次錄製都帶這些資訊：

- 日期
- 批次
- bus
- 場景
- 是否有 `comma 3X`
- 關鍵觀察 ID

範例：

- `20260313_batchA_bus1_baseline_ign_on.ndjson`
- `20260313_batchB_bus1_c3x_failpath.ndjson`
- `20260313_batchC_bus0_state_transition_watch116_177_260.ndjson`

## 每次採集都要同步記錄

- 開始時間
- 結束時間
- 車輛狀態
- 是否接 `comma 3X`
- 使用的腳本 / fork / 版本
- 指定的 bus
- 指定的觀察 ID
- 看到的錯誤訊息

## 這一輪的優先焦點

先不要追求直接拿到 `TSK`。

先追求這三件事：

1. 確認場景被完整錄到
2. 確認哪個 bus / ID 最可疑
3. 確認 `comma 3X` 失敗前後有哪些可疑時序
