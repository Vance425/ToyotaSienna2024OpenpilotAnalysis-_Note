# SecOC Key 最終分析方法與驗證流程

本文件整理 `2024 Toyota Sienna + comma 3X` 專案中，最後如何從 steering protected frames 分析出可用 SecOC key path，並確認 key 已對 `0x2E4 / STEERING_LKA` 與 `0x131 / STEERING_LTA_2` 生效。

本文件是公開安全版本：不記錄 raw key、不記錄 private key file、不記錄可直接重建 key 的 material。公開文件只保留 fingerprint、驗證方法、驗證結果與後續 validation 重點。

## 最終結論

目前結論停在：

```text
Toyota Sienna steering SecOC key 已找到、已安裝，並已在 steering protected frames 上生效。
0x2E4 / STEERING_LKA 與 0x131 / STEERING_LTA_2 已可用同一 key 驗證。
下一階段重點轉為 live validation，而不是再找 key。
```

公開 fingerprint：

```text
candidate binary sha256[:16]     = xxxxxx
candidate hex-string sha256[:16] = xxxxxx
```

## 分析入口

最初的入口不是直接找 key，而是排查 `LKAS Failure`。

C3X 上車時出現的狀態是：

```text
latActive = False
longActive = False
vehicle stationary / parked
canValid = True
canErrorCounter = 0
steerFaultTemporary 先出現
steerFaultPermanent 後續出現並維持
```

這表示問題不像一般 CAN bus invalid，也不像 driver torque 或 lateral control 已啟動造成，而更像 steering control frame 格式、SecOC tail 或 ECU acceptance 失敗。

因此分析主軸轉成：

```text
確認 steering command frame 身份
確認 Toyota SecOC MAC packing
找出 candidate key
用 passive logs 驗證 MAC
把 key 安裝到 C3X
再做 live validation
```

## 第一步：確認 `0x2E4` 身份

`0x2E4` 最後確認為 Toyota `STEERING_LKA`，也就是 LKA steering torque command frame。

這一步的重點是把 `0x2E4` 從「未知 protected side channel」改判為「正式 steering command frame」。

判斷依據：

- Toyota DBC / openpilot path 對應到 `STEERING_LKA`
- panda safety 以 `0x2E4` 作為 Toyota steering torque command 檢查對象
- passive raw CAN logs 中 `0x2E4` 的 payload 形狀符合 protected steering command

`0x2E4` 的公開結構：

```text
bytes 0-3 = clear payload
bytes 4-7 = SecOC flags + 28-bit MAC
```

重要排除：

```text
create_sienna_setpoint_alt(0x2E4, angle)
```

這條路徑被列為錯誤且危險，因為它會把不屬於 `STEERING_LKA` 的 payload 形狀送到 `0x2E4`。

## 第二步：確認 Toyota SecOC MAC 方法

依 openpilot / opendbc 的 Toyota SecOC 實作，steering protected frame 的 MAC 計算方式整理為：

```text
to_auth = [addr:16][payload first 4 bytes][freshness:48]
mac     = AES-CMAC-128(key, to_auth) 的前 28 bits
```

freshness 結構：

```text
TRIP_CNT   = 16 bits
RESET_CNT  = 20 bits
MSG_CNT    = 8 bits
RESET_FLAG = RESET_CNT lower 2 bits
padding    = 2 bits
```

payload tail packing：

```text
[MSG_CNT lower2:2][RESET_FLAG lower2:2][MAC:28]
```

`TRIP_CNT` 與 `RESET_CNT` 由 `0x0F / SECOC_SYNCHRONIZATION` 解析取得。

這一步建立的是「驗證公式」，不是 key 本體。沒有這一步，即使拿到 candidate bytes，也不能證明它真的是 Toyota steering SecOC key。

## 第三步：candidate key 來源

candidate key 來源是本機 DATAFLASH candidate output。

公開文件不記錄：

- raw key
- private key file path
- 可逆推出 key 的 dump material
- 可直接複製到車上的 key value

公開文件只記錄：

- fingerprint
- 對哪些 frame 驗證成功
- match count
- MAC packing 方法
- C3X 安裝與生效狀態

## 第四步：用 `0x2E4` 驗證 candidate key

先用 `0x2E4 / STEERING_LKA` 做 primary validation。

驗證方法：

1. 從 passive log 讀出 `0x2E4` frame。
2. 取 bytes `0-3` 作為 clear payload。
3. 從附近 `0x0F / SECOC_SYNCHRONIZATION` 解出 freshness。
4. 用 candidate key 計算 `AES-CMAC-128`。
5. 取 MAC 前 28 bits。
6. 與 log 中 bytes `4-7` 的 SecOC MAC tail 比對。
7. 若 calculated MAC 與 log MAC 一致，視為 match。

初步驗證結果：

| frame | dataset | result |
|---|---|---:|
| `0x2E4` | 2026-05-17 core slice | `5000/5000` |
| `0x2E4` | 2026-05-09 dataset core slice | `5000/5000` |

擴大驗證結果：

| frame | dataset | result |
|---|---|---:|
| `0x2E4` | 2026-05-17 core slice | `14408/14408` |
| `0x2E4` | 2026-05-09 dataset core slice | `13367/13367` |

判斷：

```text
同一把 candidate key 可以正確算回現有 passive logs 裡的 0x2E4 MAC。
```

## 第五步：用 `0x131` 做 cross-frame validation

只驗過 `0x2E4` 還不夠，因為單一 frame 可能有誤判或 packing 假設碰巧成立。

第二個驗證 frame 是：

```text
0x131 = STEERING_LTA_2
```

`0x131` 同樣是 Toyota SecOC protected steering companion frame，包含：

```text
AUTHENTICATOR
RESET_FLAG
MSG_CNT_LOWER
```

驗證方法與 `0x2E4` 相同：

1. 取 `0x131` clear payload。
2. 用相同 freshness source。
3. 用同一 candidate key 計算 AES-CMAC。
4. 比對 log MAC tail。

驗證結果：

| frame | dataset | result |
|---|---|---:|
| `0x131` | 2026-05-17 core slice | `5000/5000` |
| `0x131` | 2026-05-09 dataset core slice | `5000/5000` |

判斷：

```text
candidate key 不是只碰巧符合 0x2E4，而是能通過多個 steering-related SecOC frames。
```

這是 confidence 明顯提高的關鍵點。

## 第六步：實際 MAC match 樣本

以下樣本只顯示公開安全欄位，不包含 raw key。

`0x2E4` match example：

```json
{
  "addr": "0x2e4",
  "raw_data": "cc000000717ea22c",
  "prefix": "cc000000",
  "sync_raw": "07140377355765fc",
  "trip_cnt": 1812,
  "reset_cnt": 14195,
  "flags_nibble": "0x7",
  "msg_cnt_lower2": 1,
  "reset_flag_low2": 3,
  "matched_msg_cnt": 1,
  "log_mac": "0x17ea22c",
  "calculated_mac": "0x17ea22c",
  "match": true
}
```

`0x131` match example：

```json
{
  "addr": "0x131",
  "raw_data": "0927fffab3b3f7bd",
  "prefix": "0927fffa",
  "sync_raw": "07140377355765fc",
  "trip_cnt": 1812,
  "reset_cnt": 14195,
  "flags_nibble": "0xb",
  "msg_cnt_lower2": 2,
  "reset_flag_low2": 3,
  "matched_msg_cnt": 2,
  "log_mac": "0x3b3f7bd",
  "calculated_mac": "0x3b3f7bd",
  "match": true
}
```

這兩個樣本的意義是：

```text
同一 freshness 解讀、同一 SecOC packing、同一 candidate key，
能分別算回 0x2E4 與 0x131 的 log MAC。
```

## 第七步：C3X 安裝與生效

candidate key 已安裝到 C3X：

```text
/cache/params/SecOCKey
/data/params/d/SecOCKey
```

遠端檢查的公開資訊：

```text
length = 32 chars
mode   = 600
hex-string sha256[:16] = xxxxxx
```

目前文件口徑：

```text
key 已找到、已安裝，並已在 steering protected frames 驗證鏈上生效。
```

接下來不是再找 key，而是驗證 live control path 是否穩定重現 passive validation 的結果。

## 尚未完全關閉的點

### `0x0F / SECOC_SYNCHRONIZATION`

同一把 candidate key 目前不能驗過 sync MAC：

```text
0x0F sync MAC match = 0/512
```

目前判斷：

- `0x0F` 可能使用不同 key 或 variant。
- 也可能是 sync MAC packing 與目前 probe 假設不同。
- 這不改變 `0x2E4 / 0x131` steering protected frames 已驗證的結論。
- 因為從 `0x0F` 解出的 `TRIP_CNT / RESET_CNT` 已成功用於 `0x2E4 / 0x131` MAC validation。

### live `sendcan`

passive logs 可以證明：

```text
key + MAC method 對 stock steering protected frames 是正確的。
```

但下一階段要驗證：

```text
C3X live sendcan 送出的 0x2E4 / 0x131
是否具有正確 clear payload、freshness 與 SecOC MAC tail。
```

## 後續 validation 重點

下一階段應集中在：

- live `sendcan` 輸出與 passive log SecOC tail 的一致性
- stationary validation 的 ECU acceptance
- low-speed validation 的可重複性
- freshness / synchronization 是否在實車流程中持續一致
- fault recovery 後是否能穩定回到 accepted control path
- 確認沒有把 `0x260`-style payload 送到 `0x2E4`

## 相關文件

- [2026-05-22 Toyota Sienna SecOC 方向控制驗證完整中文報告](./secoc-20260522-steering-lka-key-validation-full-zh.md)
- [Post SecOC Key Remaining Checklist](./post-secoc-key-remaining-checklist-zh.md)
- [Public Redaction Policy](./public-redaction-policy-zh.md)
