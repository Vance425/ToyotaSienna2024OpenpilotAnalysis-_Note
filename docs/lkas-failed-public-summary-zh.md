# LKAS Failed 公開版一頁摘要

這頁只回答一件事：

- **我們公開版裡，到底寫了什麼 `LKAS Failed` 相關結果？**

## 1. 這段事件是什麼

目前公開版裡的 `LKAS Failed` 事件，指的是一段：

- `fingerprint` 已啟用
- 有跑 `LKAS Context`
- 然後出現 `LKAS Failed`

在專案裡，這段不是被當成普通故障，而是被當成：

- **`SecOC / key-state / synchronization failure-context sample`**

也就是：

- 它最有價值的地方，不是「車子報錯了」
- 而是它把：
  - `SecOCKey`
  - synchronization
  - MAC mismatch
  這些真正後段實作會卡住的問題暴露出來

## 2. 公開版裡的主結論

公開版目前對這段的主要解讀是：

1. 這不是單純一般控制值錯誤
2. 它更像是：
   - `SecOCKey missing`
   - `SecOC synchronization MAC mismatch`
   - `SECOC_SYNCHRONIZATION not valid`
3. 所以 `LKAS Failed` 在這裡比較像：
   - **後續症狀**
   - 不是最原始的原因

換句話說：

- 前面 passive / lifecycle 地圖告訴我們「路在哪」
- 這段 `LKAS Failed` log 則第一次明顯告訴我們：
  - **門口卡在 key / sync / auth 這一層**

## 3. 公開版哪裡有寫

最推薦先看：

- [lkas-context-quick-read-20260508-zh.md](./lkas-context-quick-read-20260508-zh.md)

再看公開安全版原始 context log：

- [lkas_context_20260508_185557.log](../lkas_context_20260508_185557.log)
- [collect_lkas_fault_context_20260508_185557.log](../collect_lkas_fault_context_20260508_185557.log)

總報告裡也有提到這段的專案意義：

- [OPENPILOT_INTEGRATION_PROGRESS_REPORT.md](../OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)

## 4. 原始 log 裡能看到什麼

公開安全版原始 context log 裡，可以直接看到這類訊息：

- `SecOCKey missing`
- `SecOC synchronization MAC mismatch, wrong key?`
- `SECOC_SYNCHRONIZATION not valid`

所以這段的價值很直接：

- 不是抽象推論
- 而是 fault 附近真的留下了：
  - key-state
  - sync-state
  - authentication failure
  的痕跡

## 5. 這段在專案裡的地位

這段 `LKAS Failed` log 對專案的重要性在於：

1. 它把問題從「哪個 frame 重要」推進到「為什麼 ECU 不接受」
2. 它讓後段 `SecOC / direct / key-state` 線加速
3. 它讓我們更有底氣把焦點放在：
   - key
   - sync
   - MAC
   - acceptance

## 一句話結論

**公開版已經明確寫出：這段 `LKAS Failed` 不是普通控制失敗，而是一個把 `SecOCKey / synchronization / MAC mismatch` 問題暴露出來的關鍵 failure-context sample。**
