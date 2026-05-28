# 2026-05-22 Toyota Sienna SecOC 方向控制驗證完整中文報告

日期：2026-05-22  
專案：2024 Toyota Sienna + comma 3X / openpilot / Toyota SecOC  
主題：`0x2E4 / STEERING_LKA`、`0x131 / STEERING_LTA_2`、SecOC key 驗證與 LKAS Failure 排查

## 摘要

若只想閱讀「最後 SecOC key 是如何分析出來、如何驗證並確認生效」，請先看獨立整理：

- [SecOC Key 最終分析方法與驗證流程](./secoc-key-final-analysis-method-zh.md)

本次分析的核心結論是：

```text
0x2E4 已確認是 Toyota STEERING_LKA，也就是 LKA 方向盤扭力控制命令。
```

它不是未知 frame，也不是一般 checksum frame，而是 Toyota SecOC 保護的 steering command frame。

我們已用現有 passive raw CAN logs 驗證出 `0x2E4` 的 Toyota SecOC MAC 計算方式，並找到一把 candidate key，可成功驗證 steering 相關 protected frames：

```text
0x2E4 / STEERING_LKA
0x131 / STEERING_LTA_2
```

為了安全與公開分享，key 本體不寫入 GitHub、不寫入報告、不寫入 memory files。公開文件只記錄 fingerprint：

```text
candidate binary sha256[:16]     = xxxxxx
candidate hex-string sha256[:16] = xxxxxx
```

目前 key 已寫入並在 C3X 的 `SecOCKey` 路徑生效。接下來的重點不再是「找 key」，而是把 live control path 的驗證做完整：確認 `sendcan` 送出的 protected frames、freshness、fault recovery 與回歸條件都可重複成立。

## 目前最重要結論

### 已確認

- `0x2E4` 是 Toyota `STEERING_LKA`
- `0x131` 是 Toyota SecOC DBC 裡的 `STEERING_LTA_2`
- `0x2E4` 的 bytes 0-3 是 clear payload
- `0x2E4` 的 bytes 4-7 是 SecOC flags + 28-bit MAC
- Toyota SecOC steering frame MAC 使用 AES-CMAC-128
- candidate key 可驗過現有 log 裡的 `0x2E4`
- candidate key 也可驗過現有 log 裡的 `0x131`
- C3X 已安裝 `SecOCKey`，目前結論停在 key 已生效
- 遠端 C3X openpilot 程式碼目前看起來走正常 `STEERING_LKA + add_mac(...)` 路徑

### 接下來驗證重點

- live `sendcan` 輸出與 passive log 的 SecOC tail 一致性
- stationary / low-speed validation 的 ECU acceptance
- `0x0F / SECOC_SYNCHRONIZATION`、freshness 與 protected frames 的同步關係
- fault recovery 後是否仍能穩定回到 accepted control path

## 里程碑 1：從 LKAS Failure 開始

最初的現象是 C3X 上車後出現 `LKAS Failure`。

使用者貼出的 `carState` log 顯示：

```text
latActive = False
longActive = False
vehicle stationary / parked
canValid = True
canErrorCounter = 0
steerFaultTemporary 先出現
steerFaultPermanent 後續出現並維持
```

這裡的重點是：

- 車子沒有在動
- openpilot lateral 沒有啟用
- steering command torque 沒有輸出
- CAN 本身不是一般 bus invalid
- fault 是 EPS/LKAS 狀態層面的 steering fault

因此初步判斷：

```text
這不像是方向盤扭力過大造成，而更像是 steering control CAN frame 格式或 SecOC 驗證失敗。
```

## 里程碑 2：carControl 證明當時沒有主動轉向

使用者貼出的 `carControl` log 顯示：

```text
enabled = False
latActive = False
longActive = False
actuators.torque = -0.0
actuators.torqueOutputCan = 0.0
```

這排除了幾個方向：

- 不是 openpilot 正在主動打方向
- 不是扭力命令過大
- 不是 driver override
- 不是 ACC/LKAS active 後的控制不穩

所以問題焦點轉為：

```text
即使 torque = 0，只要 C3X 發出的 SecOC-protected steering frame MAC 錯，就可能觸發 EPS/LKAS fault。
```

## 里程碑 3：確認 `0x2E4` 的真實身份

WSL openpilot / opendbc 檢查到 Toyota SecOC DBC：

```text
BO_ 740 STEERING_LKA: 8
```

也就是：

```text
0x2E4 decimal 740 = STEERING_LKA
```

DBC signals 包含：

```text
STEER_REQUEST
COUNTER
SET_ME_1
STEER_TORQUE_CMD
LKA_STATE
AUTHENTICATOR
RESET_FLAG
MSG_CNT_LOWER
```

panda safety 也用 `0x2E4` 當 Toyota steering torque command 檢查：

```text
bytes 1-2 = desired steering torque
bit0      = steer request
```

openpilot Toyota controller 正常產生流程為：

```text
toyotacan.create_steer_command(...)
secoc.add_mac(...)
```

因此正式結論：

```text
0x2E4 是 Toyota STEERING_LKA，不應再被視為未知 protected side channel。
```

## 里程碑 4：raw log 形狀符合 SecOC-protected steering frame

現有 passive raw CAN logs 裡，`0x2E4` payload 呈現這種形狀：

```text
byte0-3 = clear steering command/status payload
byte4-7 = SecOC flags + 28-bit authenticator
```

樣本：

```text
cc000000717ea22c
d0000000b9be223c
a4000000fc29066d
b000000084619c14
```

特徵：

- DLC = 8
- byte4-7 high entropy
- byte0-3 有清楚 control/counter 型態
- `bus0` 和 `bus2` 是高度鏡像，不應重複當成兩個獨立 ECU source

## 里程碑 5：發現一條危險的錯誤路徑

本機 WSL openpilot 裡曾存在 experimental helper：

```python
create_sienna_setpoint_alt(can_id, angle)
```

註解中曾列出：

```text
0x116
0x131
0x2E4
```

它使用的是類似 `0x260` 的 setpoint layout：

```text
byte0-2 = angle/setpoint little-endian
byte3-7 = 0
```

但正確的 `0x2E4` 應該是：

```text
byte0   = request / counter / set_me_1
byte1-2 = steering torque command
byte3   = LKA state
byte4-7 = SecOC flags + authenticator
```

所以：

```text
create_sienna_setpoint_alt(0x2E4, angle) 是錯誤且危險的。
```

目前檢查結果：

- WSL openpilot：只看到定義，沒有 caller
- C3X `/data/openpilot`：沒有 grep 到 caller

這條仍列為禁止使用路徑。

## 里程碑 6：確認 Toyota SecOC 計算方式

openpilot `opendbc/car/secoc.py` 的 `add_mac(...)` 顯示計算方式為：

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

最後 payload tail：

```text
[MSG_CNT lower2:2][RESET_FLAG lower2:2][MAC:28]
```

`TRIP_CNT` 與 `RESET_CNT` 由 `0x0F / SECOC_SYNCHRONIZATION` 解出。

## 里程碑 7：找到並驗證 candidate key

candidate key 來源是本機 DATAFLASH candidate output。

公開報告不記錄 key 本體，只記錄 fingerprint：

```text
binary sha256[:16]     = xxxxxx
hex-string sha256[:16] = xxxxxx
```

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

這代表：

```text
同一把 candidate key 可以正確算回現有 log 裡的 0x2E4 MAC。
```

## 里程碑 8：同一把 key 也驗過 `0x131`

Toyota SecOC DBC 裡：

```text
0x131 = STEERING_LTA_2
```

它也是 SecOC-protected steering companion frame，包含：

```text
AUTHENTICATOR
RESET_FLAG
MSG_CNT_LOWER
```

驗證結果：

| frame | dataset | result |
|---|---|---:|
| `0x131` | 2026-05-17 core slice | `5000/5000` |
| `0x131` | 2026-05-09 dataset core slice | `5000/5000` |

這使 confidence 明顯提高：

```text
candidate key 不是只碰巧符合 0x2E4，而是能通過多個 steering-related SecOC frames。
```

## 里程碑 9：實際 MAC 比對樣本

### `0x2E4` 樣本

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

### `0x131` 樣本

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

## 里程碑 10：C3X 安裝 `SecOCKey`

candidate key 已安裝到 C3X：

```text
/cache/params/SecOCKey
/data/params/d/SecOCKey
```

遠端檢查：

```text
length = 32 chars
mode   = 600
hex-string sha256[:16] = xxxxxx
```

重要 runtime note：

- 安裝時 C3X manager 正在跑
- 當時沒有看到 `controlsd`
- 下一次 fresh car interface/controller initialization 應會載入 key
- 若 controller 已在 key 安裝前初始化，需重啟 manager 或重新初始化

## 里程碑 11：C3X 程式路徑檢查

遠端 `/data/openpilot` grep 結果顯示正常路徑：

```text
STEERING_LKA -> create_steer_command(...) -> add_mac(...)
```

沒有找到：

```text
create_sienna_setpoint_alt(...)
```

被接到現機控制路徑。

## 待驗證項目

### `0x0F / SECOC_SYNCHRONIZATION`

同一把 candidate key 目前不能驗過 sync MAC：

```text
0x0F sync MAC match = 0/512
```

目前判斷：

- `0x0F` 可能用不同 key 或 variant
- 或目前 probe 的 sync MAC packing 與 Toyota/openpilot 實作有差異
- 但這不改變目前 key 已對 steering protected frames 生效的結論，因為從 `0x0F` 解出的 `TRIP_CNT` / `RESET_CNT` 已成功用於驗證 `0x2E4` 和 `0x131`

### live `sendcan` 驗證

目前結論停在 key 已生效。下一步要驗證的是 live control path 是否把這個結果穩定重現：

```text
key + MAC method 對 stock steering frames 是正確的
```

驗證時要確認：

```text
C3X live sendcan 送出的 0x2E4 / 0x131
具有正確 clear payload、freshness 與 SecOC MAC tail
```

因此下一步是以 stationary / low-speed validation 收證，而不是再回到 key 搜尋。

## 實車 validation gate

啟用 lateral 前，建議照順序：

1. fresh start openpilot / car interface
2. 車輛保持靜止
3. P 檔或安全駐車狀態
4. 不先啟用 lateral control
5. 觀察是否還會立即 LKAS Failure
6. 抓 live `sendcan`
7. 檢查 `0x2E4`
   - DLC = 8
   - byte0-3 是 `STEERING_LKA` clear payload
   - byte4-7 是非零 SecOC flags / MAC tail
   - flags 會隨時間 rolling
8. 若 `0x131` 出現，也檢查同樣 SecOC tail
9. 確認沒有 `0x260`-style payload 被送在 `0x2E4`
10. 以上通過後，再做低風險 enable test

成功訊號：

```text
停車、未啟用 lateral 時不再出現 LKAS Failure，
且 live sendcan 裡 0x2E4 / 0x131 具有有效 SecOC tail。
```

若仍出現 LKAS Failure：

1. 檢查 live `0x2E4` payload 與 MAC
2. 確認 `SecOCKey` 是否真的載入到 `CC.secoc_key`
3. 檢查 `0x131` 是否 malformed
4. 對齊 `sendcan` 與 `carState.steerFaultTemporary` / `steerFaultPermanent`

## 新增工具

本次新增兩個不含 key 的驗證工具：

```text
scripts/secoc/secoc_key_probe.mjs
scripts/secoc/secoc_2e4_freshness_profile.py
```

用途：

- `secoc_key_probe.mjs`
  - 用 candidate key 或 private key file 驗證 SecOC MAC
  - 輸出 match counts 與 report
  - 不輸出 raw key

- `secoc_2e4_freshness_profile.py`
  - 分析 `0x0F` sync 與 protected frame freshness
  - 檢查 flags、counter low2、reset low2、sync age

## 目前最終結論

本階段結論停在：key 已找到、已安裝，並且在 steering SecOC 驗證鏈上已生效。重點不是再證明「有沒有 key」，而是把 key 生效後的 live validation 做完整。

- `0x2E4` 身份確認
- `0x131` steering companion frame 確認
- Toyota SecOC AES-CMAC 方法驗證
- candidate key 對 passive logs 驗證
- C3X `SecOCKey` 安裝
- C3X code path 初步檢查

目前結論應停在：

```text
Toyota Sienna steering SecOC key 已找到、已安裝，並已在 steering protected frames 上生效。
0x2E4 / STEERING_LKA 與 0x131 / STEERING_LTA_2 已可用同一 key 驗證。
下一階段重點轉為驗證：
live sendcan 是否穩定產生正確 SecOC tail、
freshness / synchronization 是否在實車流程中持續一致、
以及 ECU acceptance、fault recovery、低速 validation 是否可重複通過。
```
