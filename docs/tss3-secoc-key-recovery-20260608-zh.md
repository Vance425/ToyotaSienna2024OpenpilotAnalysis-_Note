# TSS3 SecOCKey 找出過程與重點紀錄

日期：2026-06-08  
對象：Toyota Sienna 4TH_GEN / TSS3  
狀態：已找到並經車上驗證成功  

> 本文件只記錄分析流程、驗證方法與 redacted 結果。  
> 不包含 raw SecOCKey，不包含可公開外流的私密 key 內容。

## 1. 最終結論

這次 TSS3 SecOC 研究已成功找出可用的 SecOCKey。

我們不是從 openpilot params、log 文字或舊 artifact 直接拿到 key，而是透過以下流程完成：

1. 取得伙伴車 EPS DataFlash dump。
2. 從 dump 中產生 16-byte candidate windows。
3. 使用修正版 `0x0f` sync AES-CMAC verifier 篩選 candidate。
4. 使用 `0x131 / 0x2e4 / 0x344` protected-frame oracle 交叉驗證。
5. 安裝到車上測試，確認成功。

本次 key 只以 hash 追蹤：

- key hash：`1d1c53a6d634016a`
- 來源 ECU：EPS
- EPS application / firmware string：`8965B4514000`
- DataFlash range：`0xff200000 - 0xff208000`
- candidate 位址：`0xff206e14`
- candidate offset：`28180`

## 2. 一開始的限制與原則

研究開始時，TSS3 車上沒有可直接讀出的已知 `SecOCKey`。

早期資料曾出現一組 31 字元 artifact，但它不是合法 16-byte hex key，因此只能列為 malformed / unproven artifact。除非通過 MAC 驗證，否則不能把它當作 SecOCKey。

本次最重要的原則是：

- 任何 key-like bytes 都只能叫 candidate。
- candidate 必須通過真實 CAN frame 的 AES-CMAC 驗證，才可以升級為 SecOCKey。
- 報告與 README 不保存 raw key。

## 3. 使用到的資料

### 3.1 LKAS Failed 長 log

最有價值的 CAN oracle 是一份長時間 LKAS Failed log。  
它包含足夠多的：

- `0x0f`：SecOC synchronization / freshness frame
- `0x131`：TSS3 protected steering / LTA-related frame
- `0x2e4`：TSS3 protected steering / LKA-related frame
- `0x344`：TSS3 protected frame

這些 frame 讓我們能離線驗證 candidate 是否真的能簽 Toyota SecOC MAC。

### 3.2 EPS DataFlash dump

伙伴車成功 dump EPS DataFlash：

- range：`0xff200000 - 0xff208000`
- size：`32768` bytes
- coverage：`100%`
- frames：`8192/8192`

這個 dump 成為 candidate extraction 的來源。

## 4. 分析流程

### 4.1 先排除「直接從 log 找 key」

早期 LKAS / LTA / EPS / UDS log 中可以看到：

- LKAS failed / invalid / fault 類訊息
- UDS negative response，例如 `7f 10 78`、`7f 10 22`
- SecOC / missing key 相關跡象

但 log 中沒有直接出現 raw key。  
因此方向轉成：

- 從 ECU memory dump 找 candidate
- 用 CAN frame oracle 驗證 candidate

### 4.2 借用 TSS2.5 的 SecOC layout 經驗

TSS2.5 的結論指出 Toyota protected steering frame 大致使用：

- bytes `0..3`：明文 payload
- byte `4 high nibble`：message counter lower bits / reset flag
- byte `4 low nibble + bytes 5..7`：28-bit authenticator
- freshness：trip counter、reset counter、message counter 組成

因此 TSS3 的初始 protected-frame hypothesis 是：

```text
AES-CMAC(key, addr_be_16 + payload_byte0_3 + freshness) -> first 28 bits
```

這個 hypothesis 最後被證明是正確方向。

### 4.3 確認 remote EPS 目標

伙伴車 EPS UDS path：

- bus：`0`
- tx：`0x7a1`
- rx：`0x7a9`
- EPS application string：`8965B4514000`

這確認我們研究的是正確 ECU。

### 4.4 建立 remote dump kit

因為車不在本地，所以先提供伙伴 remote dump kit：

1. read-only probe，確認 Panda / UDS / application version。
2. 停 openpilot / boardd。
3. 進入 programming session。
4. security access。
5. 上傳已知可用 DataFlash dump payload。
6. 執行 routine。
7. 收 `0xff200000 - 0xff208000` dump。

成功後取得完整 32 KB DataFlash。

### 4.5 Payload patchability 檢查

我們也檢查過能否直接修改 encrypted payload 去 dump 更大 range。

結論：

- payload 的 dump range 寫死在 shellcode。
- payload 經 AES-CBC / AES-CMAC 保護。
- 沒有 payload build secret 或 derived key 時，不適合直接 bit patch。

因此後續不走「盲目 patch payload」路線，而是先分析已取得的完整 `0xff200000 - 0xff208000` dump。

## 5. Candidate extraction

使用兩種 extractor：

1. legacy key-struct checksum extractor
2. high-entropy 16-byte sliding window extractor

結果：

- legacy checksum candidates 存在，但不是正解。
- 成功 key 出現在 high-entropy window pool 中。
- 成功 key 不符合舊 TSS2.5 strict key-struct rule。

這代表 TSS3 不能只依賴舊的 static key-struct heuristic。  
更好的方法是：

```text
DataFlash entropy candidates -> CAN MAC oracle promotion
```

## 6. 重要修正：0x0f sync verifier

一開始我們曾以為成功 candidate 不通過 `0x0f` sync，結果為 `0/512`。

後來用已成功 key 回頭檢查，發現不是 key 不對，而是早期 JS verifier 的 `RESET_CNT` packing 寫錯。

### 6.1 正確 0x0f sync input

正確公式：

```text
AES-CMAC(
  key,
  u16be(0x0f) + u16be(trip_cnt) + reset_cnt_20bits_with_4_padding_bits
) -> first 28 bits
```

其中 `reset_cnt_20bits_with_4_padding_bits` 等價於：

```text
3 bytes of (reset_cnt << 4)
```

也等價於 openpilot Python 寫法：

```python
struct.pack(">I", reset_cnt << 12)[:-1]
```

修正後，成功 key 對 `0x0f` sync：

- `1024/1024`

用修正版 verifier 跑候選池前 520 筆，也會自動把成功 key 排第一：

- best key hash：`1d1c53a6d634016a`
- result：`1024/1024`

這讓未來流程可以先用 `0x0f` sync 快速找 key，再用 protected-frame oracle 交叉確認。

## 7. Protected-frame oracle 驗證

protected-frame formula：

```text
AES-CMAC(
  key,
  addr_be_16 + payload_byte0_3 + freshness
) -> first 28 bits
```

freshness：

```text
trip_cnt_16 || reset_cnt_20 || msg_cnt_8 || reset_flag_2 || padding_2
```

驗證結果最關鍵的是 bus 0：

- `0x131`：`226/226`
- `0x2e4`：`225/225`
- `0x344`：`112/113`
- total：`563/564`

後續一鍵工具端到端測試時，protected-frame 驗證也達到：

- `730/750`

這證明 candidate 不只是符合 sync，也能簽 protected control/status frame。

## 8. 車上驗證

找到 candidate 後，製作 installer bundle：

- 依 key hash 從 candidate pool 找 key
- 不在 console 印 raw key
- 寫入 `SecOCKey`
- 備份舊 key

車上測試確認成功，代表本次 SecOCKey recovery 目標完成。

## 9. 後續成果：one-shot 自動 export 工具

找到 key 後，我們把流程收斂成一支 one-shot Python：

```text
tss3_one_shot_secoc_key_export.py
```

目的：

伙伴或後續同族 TSS3 車輛不需要先提供 dump / CAN log / candidate CSV。  
在 comma 上執行後，工具會自己：

1. stop openpilot / boardd
2. 連 Panda
3. 收 `0x0f / 0x131 / 0x2e4 / 0x344` CAN oracle frames
4. dump EPS DataFlash `0xff200000 - 0xff208000`
5. 從 dump 掃 entropy candidates
6. 用 corrected `0x0f` sync verifier 找 key
7. 用 protected-frame oracle 交叉驗證
8. export `SecOCKey.hex`
9. 若加 `--apply`，可直接寫入 params

注意：工具輸出與 repo 文件仍不包含 raw key。

## 10. 建議未來 TSS3 流程

未來遇到另一台 TSS3，可以使用以下順序：

1. 確認 EPS UDS path，例如 `0x7a1 -> 0x7a9`。
2. 收 `0x0f / 0x131 / 0x2e4 / 0x344` CAN。
3. dump EPS DataFlash `0xff200000 - 0xff208000`。
4. 掃 high-entropy 16-byte candidates。
5. 使用 corrected `0x0f` sync verifier。
6. 使用 protected-frame oracle。
7. 通過後才安裝測試。

建議 promotion rule：

- `0x0f` sync：接近或高於 `99%`
- bus 0 protected frames：接近或高於 `95%`
- raw key 不輸出，只使用 hash 追蹤

## 11. 為什麼這次成功

成功的關鍵不是找到某個名為 `SecOCKey` 的檔案，而是建立了一個可以驗證 key 的閉環：

```text
EPS DataFlash candidate
  -> corrected 0x0f sync MAC proof
  -> protected-frame MAC proof
  -> vehicle-side validation
```

這個閉環讓我們能把 candidate 從「像 key」升級成「已驗證可用 key」。

## 12. 安全與 repo 保存規則

本 repo 可以保存：

- 分析流程
- redacted key hash
- CAN ID / layout / verifier formula
- 工具用法
- 驗證比例

本 repo 不應保存：

- raw SecOCKey
- private key file
- raw candidate CSV
- 可公開外流的車上私密 dump

本次 key 僅以 hash 追蹤：

```text
1d1c53a6d634016a
```

