# 拿到 SecOC Key 後：剩餘項目清單

## 目的

這份文件回答一個很實際的問題：

- **如果我們已經拿到 `SecOC Key`**
- 那距離真正讓 `2024 Toyota Sienna` 使用 `C3X`
- 還差哪些項目

最重要的前提是：

- **拿到 `SecOC Key` 不等於整個問題已經解完**

它代表的是：

- 我們可能已經打開最硬的 secure/auth 大門之一

但後面還有：

- sync
- MAC
- message set
- control mapping
- safety
- integration

要一起收斂。

## 一句話總結

**拿到 `SecOC Key` 之後，我們才算從「門外」走到「門口」；要真正讓 `2024 Sienna` 用上 `C3X`，還必須把 `freshness/sync + MAC + protected message set + control mapping + safety/integration` 這整套走完。**

## 一、Secure/Auth 層剩餘項目

### 1. Key 真實有效性確認

要確認：

- 這把 key 是不是目前目標 ECU 真正在用的 key
- 不是：
  - 舊 key
  - 錯 slot
  - 錯 ECU
  - 只在某種暫時狀態下有效的 key

要看的結果：

- 使用這把 key 後
- secure/auth path 的錯誤是否明顯下降
- 不再持續報：
  - `missing`
  - `wrong key`
  - `MAC mismatch`

### 2. Freshness / Synchronization 閉合

這是最重要的剩餘 secure/auth 問題之一。

要確認：

- freshness counter 怎麼來
- synchronization frame 是哪個
- counter 怎麼遞增
- 什麼情況要 resync
- ignition cycle / power-state 會不會影響 freshness 狀態

因為：

- **有 key 但 sync/freshness 不對，ECU 仍然會拒絕**

### 3. MAC / Authenticator 計算規則

要確認：

- 哪些 byte 參與 MAC
- `DataId` 是什麼
- truncation 長度是多少
- packing 順序是什麼
- endian / field order 是否正確

因為：

- **有 key 但 MAC 打包錯，仍然不會通過驗證**

### 4. Secure/Auth 錯誤回退策略

要確認：

- key 錯時會怎樣
- sync 錯時會怎樣
- freshness 漏掉時會怎樣
- ECU 是：
  - 忽略
  - 直接 fault
  - latched fault
  - 還是會進入某種降級模式

這會直接影響：

- bench 測試方式
- on-road 風險控制
- 自動回退策略

## 二、Protected Message / TSK 層剩餘項目

### 5. 真正要送的 protected message set

不能只停在：

- `0x260`

還要確認真正要送的集合包含哪些：

- 主控制 payload
- companion/context frames
- enable/mode frames
- heartbeat / side-channel
- 是否有前置喚醒或狀態對齊訊息

也就是：

- **不是一個 key + 一個 frame 就等於可控**

### 6. 訊息時序與節奏

要確認：

- 發送頻率
- 周期抖動容忍度
- synchronization 與主 payload 的前後關係
- 哪些 frame 要先送
- 哪些 frame 要保持同時活躍

因為很多 ECU 問題不是：

- 值錯

而是：

- 時序錯
- 節奏錯
- 上下文不完整

### 7. `0x2E4` 的 operational meaning

目前我們知道：

- `0x2E4` 很重要
- 常和高價值 protected window 同場

但還要確認它在實作裡到底是：

- 只是 protected-family side channel
- 還是更強的 operational prerequisite
- 或者與 sync / enable / mode 有更直接關係

## 三、Control-Side 層剩餘項目

### 8. `0x260` 最終控制映射定稿

目前我們已有 working branch：

- `no_b1_flip + identity + higher slew`

但還沒到 implementation-grade final mapping。

還要定：

- normalized input 範圍
- raw setpoint 對應
- 飽和邊界
- 正負側不對稱處理
- 不同 regime 的 shaping

### 9. Slew / smoothing / regime handling

要確認：

- 高 slew 真的可接受嗎
- 不同路況是否需要不同 shaping
- city transition/settle 規則是否要保留為局部規則
- freeway / bridge-tier / hold / settle 是否需要分群控制

### 10. Longitudinal / lateral context separation

要小心確認：

- `0x260` 在哪些區間更像控制量
- 哪些時候混入狀態上下文
- 大轉向 / lane-change / follow / exit-near 調整時
  是否需要不同解讀

## 四、ECU 接受與實車控制層剩餘項目

### 11. ECU 實際接受路徑驗證

要確認：

- ECU 會不會接受我們送出的 protected control
- 接受後是否真的執行
- 是短暫接受還是可穩定持續
- 是否有 mode/state prerequisite

### 12. 故障保護與回退

要確認：

- secure/auth 出錯時的行為
- 控制被拒絕時的回退
- 是否會引發：
  - `LKAS Failed`
  - EPS fault
  - persistent fault
  - restart required

### 13. 有界實車測試策略

要依序做：

1. bench / dry-run
2. 短時 active validation
3. bounded parking-lot / low-speed validation
4. 短時直線跟隨
5. 漸進式加入：
   - 跟車
   - 減速
   - 匝道
   - target-switch
   - 長時間持續控制

## 五、Openpilot / C3X 整合層剩餘項目

### 14. Fingerprint / CarParams / 車型識別

要確認：

- `2024 Sienna` fingerprint
- `CarParams`
- firmware identity
- 啟動後的車型狀態一致性

### 15. Panda safety / message ownership

要確認：

- 哪些訊息由誰送
- panda safety 是否允許
- bus ownership / arbitration 是否正確
- 是否會和原車訊息衝突

### 16. Car interface / packer / sender

要完成：

- control command packer
- secure/auth sender
- state parser
- fault handling path
- startup / shutdown / ignition-cycle handling

### 17. 長時間穩定性

最後真正要驗證的是：

- 不只“能動”
- 而是：
  - 能持續
  - 能恢復
  - 不會累積 fault
  - 不會在重啟後失效

## 六、如果只看最關鍵的剩餘 5 項

如果現在只問：

- 拿到 `SecOC Key` 之後
- 最關鍵還差哪幾件

那我會排這 5 個：

1. **freshness / synchronization**
2. **MAC / authenticator 計算與封包**
3. **真正的 protected message set 與時序**
4. **`0x260` 最終 control mapping**
5. **ECU 接受後的 fault handling / safety 回退**

## 七、建議的最短執行順序

拿到 key 之後，最短建議順序是：

1. 先驗證 key 是否真有效
2. 再閉合 sync / freshness
3. 再確認 MAC / packing
4. 再驗證最小 protected message set
5. 再做 bounded ECU acceptance test
6. 最後才進 openpilot/C3X 整合

## 八、現在不該做的事

### 1. 不該把拿到 key 當成專案完成

因為這只代表 secure/auth 最難的一層可能有突破，
不是整條控制鏈都已經可用。

### 2. 不該在 sync / MAC 未閉合前直接做長時間實車控制

因為這樣最容易造成：

- 控制間歇性失效
- fault 累積
- 誤判 control mapping 問題

### 3. 不該把 replay-working assumptions 直接升成 implementation truth

例如：

- `no_b1_flip + identity + higher slew`

它目前是強 working branch，
但還要經過 secure/auth acceptance 才能升級。

## 九、最終專案語言

如果未來要對外或對內簡短描述目前狀態，可以用這句：

**拿到 `SecOC Key` 之後，專案將從「是否能打開 secure/auth 大門」進入「如何完成 sync、MAC、protected message set、control mapping、safety 與 openpilot 整合」的階段；這才是 `2024 Sienna` 真正用上 `C3X` 的最後主路徑。**

## 參考

- [current-findings-summary-v2.md](current-findings-summary-v2.md)
- [OPENPILOT_INTEGRATION_PROGRESS_REPORT.md](../OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)
- [implementation-prerequisite-checklist.md](implementation-prerequisite-checklist.md)
- [openpilot-control-side-working-note.md](openpilot-control-side-working-note.md)
- [passive-line-vs-key-sync-limitations-zh.md](passive-line-vs-key-sync-limitations-zh.md)
