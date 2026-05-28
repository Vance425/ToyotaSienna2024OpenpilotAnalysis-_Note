# 2026-05-09 SecOC Direct Branch 改造方法

## 目的

這份文件整理如何把原本的 `extract_keys.py` 改造成適合 `2024 Toyota Sienna` 的 SecOC key 研究工具。

核心判斷是：

- 舊腳本不是完全不能用
- 但它不能再被當成「固定 dump 位址 + 固定 key table parser」的成品工具
- 對 `2024 Sienna`，它更適合改造成：
  1. `dump-only` 擷取工具
  2. 離線 key layout discovery 工具
  3. 候選 key 驗證工具

## 目前已知狀態

原始腳本：

- extract_keys.py (local-only external source path)

對應舊輸出：

- secoc_getKey_result20241124.txt (local-only external source path)

分析筆記：

- [2024-sienna-extract-keys-failure-layer-analysis-zh.md](./2024-sienna-extract-keys-failure-layer-analysis-zh.md)
- [passive-line-vs-key-sync-limitations-zh.md](./passive-line-vs-key-sync-limitations-zh.md)

舊腳本已經包含 `2024 Sienna EPS` 版本：

```python
b'\x018965B4514000\x00\x00\x00\x00': b'\x02!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
```

這表示它不是卡在車型版本表完全不認得。

## 哪些部分可以沿用

### 1. 目標 ECU 與版本識別

目前舊輸出顯示：

- `0x7A1 -> 0x7A9` 有回應
- application version 可讀到：
  - `8965B4514000`
- bootloader version 可讀到：
  - `\x02!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!`

這一段可以保留，但要改成 profile 化。

建議：

- 新增 `profiles/sienna_2024_eps_8965B4514000.json`
- 把以下項目從程式常數移到 profile：
  - `tx_addr`
  - `rx_addr`
  - `bus`
  - application version
  - bootloader version
  - download address
  - payload size
  - dump range list

### 2. Diagnostic Session Flow

舊輸出中：

- `0x1001`
- `0x1003`
- `0x1002`

都有正回應。

這表示 session 切換路徑目前可保留。

要改的是：

- 每一步都記錄 transcript
- 遇到 `0x7F xx 78` 時不要直接視為失敗
- timeout 參數應獨立可調

### 3. SecurityAccess Flow

舊輸出中：

- seed 有拿到
- key 有送出
- ECU 回 `0x6702`

所以第一輪不應把失敗歸因於 `SecurityAccess`。

建議保留：

- request seed
- derive key
- send key

但要新增：

- seed / key / response transcript 輸出
- 可重跑比對 seed 是否每次不同
- 不要把這裡的成功等同於已取得 SecOC key

### 4. Payload Upload Flow

舊輸出中：

- DID `0x203`
- DID `0x201`
- DID `0x202`
- `RequestDownload`
- `TransferData`
- `RequestTransferExit`
- routine `0x10F0`

都有成功跡象。

這表示 payload path 可能仍可用。

但要注意：

- payload 有上傳成功，不等於 dump 到正確 key table
- routine 成功，不等於 payload 已經完整執行目標邏輯
- dump 回來的 bytes 才是後續判斷核心

## 哪些部分必須重寫

## 1. 不要自動解析成 KEY_1 / KEY_4

舊腳本目前假設：

```python
KEY_STRUCT_SIZE = 0x20
CHECKSUM_OFFSET = 0x1d
SECOC_KEY_OFFSET = 0x0c
SECOC_KEY_SIZE = 0x10
```

並假設：

- `KEY_1` 是 ECU master key
- `KEY_4` 是 SecOC key

這些假設在 `2024 Sienna` 上目前沒有成立證據。

建議修改：

- dump 完後不要立刻 `verify_checksum(KEY_1 / KEY_4)`
- 不要立刻把 `KEY_4` 當 SecOC key
- 先輸出 raw dump
- parser 改成離線工具

## 2. 不要自動寫入 `SecOCKey`

舊腳本最後會嘗試：

```python
params.put("SecOCKey", key_4.hex())
```

這對 2024 Sienna 不安全，因為目前 parser 還不能證明 `key_4` 是真的 SecOC key。

建議：

- 預設永遠不寫 param
- 只有同時指定：
  - `--write-param`
  - `--force`
  - `--candidate <hex>`
  才允許寫入
- 寫入前輸出警告與摘要
- 寫入後立即備份原始 param 狀態

## 3. Dump range 要變成可配置與可比對

舊 range：

```text
0xFEBE6E34 -> 0xFEBE6FF4
```

在舊輸出中，這段 dump 的內容不像穩定 key table。

可能原因：

- dump 區間錯了
- key table layout 改了
- payload 只 dump 到鄰近區
- 2024 版本 key 被包裝或間接引用

建議：

- 支援多個 dump range
- 每個 dump range 都輸出獨立檔案
- 每個 dump 檔都附 metadata：
  - ECU version
  - bootloader version
  - session flow result
  - seed response
  - payload checksum
  - dump start / end
  - timestamp

## 建議工具拆分

## 工具 1：`secoc_dump_capture.py`

用途：

- 只負責和 ECU 溝通
- 只負責 unlock / upload / trigger / dump
- 不直接判斷 key

輸出：

```text
out/secoc_dump_YYYYMMDD_HHMMSS/
  transcript.jsonl
  metadata.json
  dump_febe6e34_febe6ff4.bin
  dump_summary.txt
```

必備功能：

- `--profile sienna_2024_eps`
- `--dump-range 0x...:0x...`
- `--output-dir ...`
- `--no-write-param`
- `--dry-run-profile`

安全預設：

- 不寫 `SecOCKey`
- 不改 openpilot 檔案
- 不自動重啟 openpilot
- 檢查 `boardd` / openpilot 是否在跑

## 工具 2：`parse_secoc_dump_candidates.py`

用途：

- 離線解析 dump
- 掃可能的 key-like candidate
- 不接車

可以掃的項目：

- 非零區塊
- 高 entropy 區塊
- 16-byte aligned candidates
- repeated 0x20 / 0x30 / 0x40 struct pattern
- 舊 checksum 規則
- 可能的新 checksum offset
- fixed marker 附近的候選資料
- `00 00` / `5A 5A` / `22 22` / `01 00 00 00` 這類狀態字附近結構

輸出：

```text
candidate_report.md
candidate_keys.csv
layout_hypotheses.json
```

候選欄位建議：

```text
dump_file
offset
candidate_hex
entropy
near_marker
old_checksum_ok
struct_size_guess
notes
```

## 工具 3：`compare_dump_runs.py`

用途：

- 比對多次 dump 是否穩定
- 區分固定 key material、session-specific freshness、狀態字、亂數

判斷邏輯：

- 每次都一樣：
  - 可能是固定 key 或固定 table
- 每次都不同：
  - 可能是 seed / freshness / runtime state
- ignition cycle 後不同：
  - 可能是 sync/freshness state
- 完全零值：
  - 可能是錯區、未初始化、或 parser 偏移錯

## 工具 4：`validate_secoc_candidate.py`

用途：

- 不直接證明 key 正確
- 只做低風險候選驗證

驗證方向：

- candidate 是否長度正確
- candidate 是否非全零
- candidate 是否跨 dump 穩定
- candidate 是否符合已知 checksum / wrapper pattern
- candidate 寫入前後，openpilot log 是否從：
  - `SecOCKey missing`
  變成：
  - `MAC mismatch`
  - `sync failed`
  - 或其他更進一步錯誤

注意：

- `missing -> mismatch` 不代表 key 正確
- 但它代表系統可能已經從「沒有 key」推進到「有 key 但不接受」
- 這對定位 failure layer 有價值

## 建議改造流程

## Step 1：保留原始腳本，另開新檔

不要直接覆蓋舊的 `extract_keys.py`。

建議新增：

```text
<LOCAL_CODEX>\secoc\extract_keys_sienna2024_dump_only.py
```

理由：

- 舊腳本是歷史參考
- 新工具應該明確表示它是 2024 Sienna 專用實驗工具
- 避免不小心把舊 parser 成功條件當成通用真理

## Step 2：先做 `dump-only`

第一版只做：

1. version check
2. session flow
3. SecurityAccess
4. payload upload
5. payload trigger
6. dump raw bytes
7. 寫出 transcript

不要做：

- checksum fail 就退出
- 自動取 `KEY_4`
- 自動寫 `SecOCKey`

## Step 3：離線重跑舊 parser

把舊 parser 改成離線模式：

```text
parse_old_layout.py dump.bin
```

它只輸出：

- old key 1 candidate
- old key 4 candidate
- checksum result
- struct dump table

如果失敗，也保留報告，不要直接中斷整個流程。

## Step 4：擴展 layout search

掃描：

- struct size:
  - `0x10`
  - `0x20`
  - `0x30`
  - `0x40`
- key offset:
  - 每 4 bytes 一格
- checksum offset:
  - struct 末端附近
- key index:
  - 不固定假設 `KEY_4`

目標不是一次找到唯一答案，而是縮小候選。

## Step 5：多次 dump 比對

至少收集：

- 同一次 ignition 連續 dump 2 次
- 熄火/上電後 dump 1 次
- openpilot 未啟動狀態 dump
- openpilot 啟動到 LKAS failed 後 dump

比對：

- 哪些 bytes 固定
- 哪些 bytes 隨 session 變
- 哪些 bytes 只在 LKAS failed 後改變

## Step 6：候選 key 不直接上車控制

候選 key 的第一個用途不是控制車。

第一個用途應該是 failure-layer validation：

- 沒 key 時：
  - `SecOCKey missing`
- 放候選後：
  - 如果錯誤變成 `MAC mismatch` / `freshness mismatch`
  - 表示系統進到下一層
- 如果完全沒變：
  - candidate 可能不是有效 key
  - 或 key 路徑根本沒被使用

## 方法清單

## 方法 A：舊 dump range 重跑，但只保存 raw dump

適合第一步。

優點：

- 改動最小
- 可快速確認舊行為是否可重現

缺點：

- 如果 range 本來就錯，仍然只會拿到無效區域

判斷成功標準：

- dump 長度正確
- transcript 完整
- raw bytes 可重現

## 方法 B：多 range dump 掃描

把 dump range 從單一固定區間改成多個候選區間。

優點：

- 有機會找到 2024 Sienna 新 layout

缺點：

- 需要 payload 支援
- 需要嚴格限制範圍與紀錄
- 上車風險比單 range 高

判斷成功標準：

- 找到穩定非零、結構化、高 entropy 的區段
- 跨多次 dump 保持一致

## 方法 C：parser layout discovery

不動車，只處理已取得 dump。

優點：

- 風險最低
- 可大量嘗試 layout 假設

缺點：

- 如果 dump 區間不含 key，怎麼掃都不會有結果

判斷成功標準：

- 產生少量高可信候選
- 候選跨 dump 穩定
- 候選不是全零或明顯狀態字

## 方法 D：failure-layer validation

用 candidate 只測系統錯誤型態是否前進。

優點：

- 比直接控制安全
- 可判斷 `missing` / `wrong` / `sync` 差異

缺點：

- 不能單獨證明 key 正確
- 需要搭配 LKAS context / openpilot logs

判斷成功標準：

- 錯誤從 `missing` 變成更深層錯誤
- 或 openpilot SecOC 狀態有可解釋變化

## 方法 E：回頭修改 payload

如果確認 UDS / unlock / upload 都通，但 dump 區間錯，才進入這一步。

方向：

- payload 增加可配置 dump address
- payload 增加 marker
- payload 輸出更完整 pointer / status
- payload 將 dump 分段標號

優點：

- 最有機會突破錯區問題

缺點：

- 工程風險最高
- 需要理解 shellcode / build_payload
- 每次修改都要重新驗證 upload / trigger path

## 不建議的方法

### 不建議 1：只改 `APPLICATION_VERSIONS`

原因：

- 2024 Sienna 版本已經在表裡
- 舊輸出已證明版本識別成功

### 不建議 2：直接改 `KEY_4` offset 猜一個

原因：

- 可能會產生看似非零但完全錯誤的 candidate
- 容易誤寫入 openpilot

### 不建議 3：把 checksum 關掉就當成功

原因：

- checksum fail 不是小錯
- 它是在提醒 layout 假設不成立

### 不建議 4：候選 key 直接寫入並上路測

原因：

- key / freshness / sync 任一層錯，都可能造成控制失效
- 實車路測前必須先完成靜態 failure-layer validation

## 最小可行改造版本

第一版只需要做到：

```text
extract_keys_sienna2024_dump_only.py
  --profile sienna_2024_eps
  --output-dir out/secoc_dump_...
  --dump-only
```

功能：

- 走完舊 UDS path
- 觸發 payload
- dump raw bytes
- 保存 transcript
- 不解析 key
- 不寫 param

第二版再加：

```text
parse_secoc_dump_candidates.py
  dump.bin
```

第三版再加：

```text
validate_secoc_candidate.py
  --candidate <hex>
  --no-write
```

## 目前最重要的結論

原本的 SecOC 腳本可以作為基底，但不是因為它已經快成功，而是因為它前半段已經證明：

- ECU 會回
- session path 大致通
- SecurityAccess 至少曾成功
- payload upload path 至少曾成功

真正要解的是後半：

- dump range
- memory layout
- key table structure
- parser
- candidate validation

## 一句話總結

**2024 Sienna 的 direct branch 應該從「舊車固定 KEY_4 擷取器」改造成「dump-first、offline-parse、candidate-validate」的三段式工具；這是目前最合理、也最不容易誤判的 SecOCKey 取得路線。**
