# Longitudinal Event ID Scan

這份文件整理 longitudinal event ID scan 的公開版結論。原始 detail CSV 含有本機 raw log 路徑與逐筆 frame-level 資料，不放入公開版 repo。

## 目的

用多段 CAN log 比對 longitudinal 相關 CAN ID 在加速、減速、穩態與 transition window 的同步程度，判斷哪些 ID 比較像 control anchor、context neighbor 或 response / feedback side candidate。

## 輸入

- raw CAN `.ndjson` logs：本機保留，不放入 repo
- `scripts/scan_longitudinal_event_ids.ps1`
- analysis summary CSV：保留已整理、可分享的摘要

## 方法摘要

- 以 `0x260` 作為目前最重要的 longitudinal command anchor。
- 對 candidate CAN ID 計算 transition window 內的變化比例。
- 分別觀察 `accel_like` 與 `brake_like` 事件。
- 比較 `0x116`、`0x131`、`0x2E4`、`0xD8`、`0x90`、`0x191`、`0x371` 等候選 ID 的同步程度。

## 主要結論

- `0x260` 仍是目前最佳的 longitudinal command anchor。
- `0x116 / 0x131 / 0x2E4` 比較像 steering / TSK / SecOC 相關 backbone，不是單純油門或煞車 ID。
- `0x90` 有參考價值，但較像 contextual neighbor。
- `0x191 / 0x371` 更像 response / feedback side candidate。
- `0xAA` 與 `0x127` 對直接 event semantics 的支持較弱。

## 公開版處理

`longitudinal_event_detail.csv` 不放入 public repo。若需要重跑，應使用本機 raw logs 搭配 `scripts/scan_longitudinal_event_ids.ps1` 重新產生 detail output。
