# ToyotaSienna2024OpenpilotAnalysis_Note 範圍說明

本 repo 是 `ToyotaSienna2024OpenpilotAnalysis` 的整理版筆記，目標是保存 Toyota Sienna + comma 3X / openpilot 整合研究中可分享、可重跑、可延續的分析內容。

## Repo 名稱

GitHub repo 使用：

```text
ToyotaSienna2024OpenpilotAnalysis-_Note
```

本機資料夾使用：

```text
ToyotaSienna2024OpenpilotAnalysis_Note
```

## 保留內容

- root-level project docs
- `docs/` 內的研究筆記與中文化報告
- SecOC key 分析方法、驗證結果與已遮罩的 key 相關內容
- Virtual TSK SPEC 參數分析方法與驗證表
- CAN log 收集 workflow、log spec 與分析 scripts
- `scripts/`
- `analysis-output/` 內已整理、可分享的分析輸出
- `sim/` 模擬工具與模擬結果
- 小型 `.csv` / `.json` 輔助資料

## 不保留內容

以下資料不放進公開版 repo：

- raw CAN `.ndjson` logs
- C3X context log / swaglog / device status 原始輸出
- 實際 `SecOCKey`
- private key file
- dataflash / memory dump material
- token、credential、private IP、dongle id、VIN 等可識別資訊
- 本機絕對路徑或只對本機有效的暫存檔

## 公開前原則

這份 repo 只保留可重跑的方法、分析結果摘要與已遮罩的驗證紀錄。原始資料與敏感識別資訊保留在本機備份或私有 archive，不作為 public repo 的一部分。
