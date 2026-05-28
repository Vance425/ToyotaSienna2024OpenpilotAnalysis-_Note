# Public Redaction Policy

本文件規範 `ToyotaSienna2024OpenpilotAnalysis` 對外分享時，哪些內容可以公開，哪些內容必須 redacted 或保留 local-only。

## 原則

這個 repo 可以公開研究方法、frame 身份、validation result、workflow 與風險判斷，但不能公開會直接造成車輛安全風險或 key material 外洩的內容。

## 不公開

以下內容不得放入 public repo：

- raw `SecOCKey`
- private key file
- 可直接還原 key 的 full candidate bytes
- private IP / device credential
- SSH key / token / password
- 未 redacted 的 ECU memory dump binary
- 可直接照抄執行的 active ECU exploit / payload 操作教學

## 可公開

以下內容可以公開：

- `CAN ID`
- `DBC signal`
- frame role 判斷
- validation count
- candidate fingerprint
- high-level SecOC method description
- safety gate
- failure mode
- log analysis summary
- scripts 名稱與 offline validation workflow

## Candidate key 表示方式

只允許公開 fingerprint，例如：

```text
candidate binary sha256[:16] = ...
candidate hex-string sha256[:16] = ...
```

不要公開：

```text
actual key bytes
full key file content
private candidate list
```

## Direct branch 表示方式

舊 `extract_keys` / DATAFLASH / payload 類文件應以風險說明為主。

可以說：

- 這是 active ECU / diagnostic / programming path。
- 它可能依賴 firmware version、seed-key secret、memory layout。
- 它有 brick / EPS fault / steering rack replacement 風險。

不要把它寫成：

- 無風險操作手冊
- 一般使用者照做流程
- 對所有 Toyota 都通用的方法

## Logs

`logs/` 可以放 curated representative logs。

大型 raw archive 建議：

- local-only
- 或 Git LFS
- 或另建 archive 目錄並明確標示用途

不要把舊 raw archive 散放在 repo root。

## 文件語言

除以下內容外，其餘 human-facing markdown 應以中文為主：

- program
- script
- log spec
- CAN ID
- DBC signal
- command
- file path
- table column name
- raw log field

技術名詞保留英文原文，避免翻譯造成誤判。
