# 研究任務定義

## 最終目標

讓 `2024 Toyota Sienna` 可以使用 `comma 3X`。

## 目前主線任務

找出 `Toyota Security Key (TSK)` 的取得方法。

## 目前已知限制

- 車端沒有現成可用的 TSK
- `comma 3X` 目前無法自動抓取成功
- 因此系統無法正常使用

## 現階段工作內容

現階段不是一般安裝，也不是主動 `seed -> key`，而是以被動研究為主：

- 收集 CAN log
- 分析 security 相關訊息
- 鎖定可能的 TSK 流程
- 形成可驗證假設

## 目前方法

由於主動送 `seed` 到 Sienna 不會回應，目前主線改為：

- 被動收集 CAN log
- 找出疑似 `SecOC/auth/counter` frame
- 比對狀態切換與 `comma 3X` 失敗時序

## 什麼算推進成功

- 從「不能用」推進到「知道卡在哪裡」
- 從「不知道 TSK 怎麼拿」推進到「有明確假設」
- 從「零散 log」推進到「可重現分析流程」
