# 第二輪採集檢查表

## 出發前

- [ ] 裝置與供電穩定
- [ ] 腳本完整部署
- [ ] 知道今天要錄哪一個 batch
- [ ] 知道今天只改哪一個變因
- [ ] 準備好記錄時間點

## 現場

- [ ] 記錄開始時間
- [ ] 記錄車輛狀態
- [ ] 記錄是否接上 comma 3X
- [ ] 記錄 bus
- [ ] 記錄目標 ECU
- [ ] 記錄是否有跑 UDS / seed hunter
- [ ] 記錄錯誤訊息

## 收工前

- [ ] 確認 log 檔已生成
- [ ] 確認 `events.jsonl` 已生成
- [ ] 確認 `uds_events.jsonl` 已生成
- [ ] 確認檔名符合規則
- [ ] 確認本次只有一個主要變因

## 當天回來先檢查

- [ ] `events.jsonl` 是否出現 `uds_enabled: true`
- [ ] `uds_events.jsonl` 是否還是全 timeout
- [ ] 是否有 request / response 配對
- [ ] 是否有比第一輪更明確的可疑 ECU
