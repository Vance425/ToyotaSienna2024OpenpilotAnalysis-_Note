# Virtual TSK SPEC 參數分析方法與過程

本文件補上 `VIRTUAL_TSK_SPEC_v2.md` 缺少的一層：不是只列結論，而是說明每個主要參數是怎麼從 raw CAN log 被分析、驗證、降級或保留的。

本文件只描述分析方法與公開安全的統計結果；program、script、log spec、CAN ID、欄位名稱與檔名保留原文。

## 資料來源

主要使用的 reference logs：

- `toyota_seg_IGN_ON_20260312_190101_000.ndjson`
- `toyota_seg_IGN_ON_20260315_171414_000.ndjson`
- `toyota_seg_IGN_ON_20260311_184921_000.ndjson`
- `toyota_all_20260418_163135_000.ndjson`
- `toyota_all_20260418_175240_000.ndjson`
- 20260426 批次 logs

主要分析工具：

- `scripts/verify_virtual_tsk_spec.ps1`
- `scripts/generate_log_feature_table.py`
- `scripts/grade_can_logs.py`

主要輸出：

- `analysis-output/virtual_tsk_verify/virtual_tsk_verification.csv`
- `analysis-output/all_ndjson_feature_table.csv`
- `analysis-output/valuable_ndjson_feature_table.csv`
- `analysis-output/can_log_grades.csv`

## 總體分析流程

1. 先用 raw CAN log 依 `bus`、`addr`、`ts_ms`、`data` 解析每一筆 frame。
2. 對每個候選 CAN ID 建立 time series。
3. 對 `0x260` 建立 control-side 主軸值。
4. 對 `0x116 / 0x131 / 0x2E4` 建立 protected-lifecycle backbone。
5. 用 timing window 檢查 `0xAA / 0x90 / 0x127 / 0x371` 是否真的像 command / trigger / feedback。
6. 用 correlation 檢查 `0x371`、`0x191` 是否與 `0x260` 有穩定數值關係。
7. 用跨 log 結果決定每個參數是 `validated`、`partially validated`、`contextual` 還是 `unproven`。

## `0x260` control value

`0x260` 是目前最強的 control-side anchor。分析時不是只看 raw byte，而是先轉成一個連續 control value：

```text
fine = Int16LE(B2, B3)
coarse = Int8(B5) << 8
control = fine + coarse
if B1 == 0xFF:
  control = -control
```

分析方法：

- 取 `B2-B3` 作為 fine control。
- 取 `B5` 作為 signed coarse component。
- 用 `B1 == 0xFF` 判斷方向或符號翻轉。
- 對相鄰 `0x260.control` 做差分，若絕對變化大於 `500`，標記為 `large260 change`。

用途：

- 當作 timing 對齊的中心點。
- 當作 `0xAA / 0x90 / 0x127 / 0x371 / 0x191` 的驗證基準。
- 當作 replay / control-side branch 的主軸。

## `0x260.B1`

`B1` 的分析方式是符號層判斷，不是單獨控制量。

分析方法：

- 若 `B1 == 0xFF`，將計算出的 `control` 乘以 `-1`。
- 對照 replay branch 裡的 `no_b1_flip` / sign behavior。
- 若翻轉後與 event direction、companion correlation 更一致，保留此 sign interpretation。

目前判斷：

- `B1` 比較像 direction / sign gate。
- 不應獨立解讀成 TSK key material。

## `0x260.B2-B3`

`B2-B3` 以 `Int16LE` 解讀。

分析方法：

- 每筆 `0x260` 取 `Int16LE(B2,B3)`。
- 與 `B5` 組成 control value。
- 對不同 logs 檢查是否能產生連續、可重現的 control trajectory。

目前判斷：

- 是 `0x260` 裡最穩的 fine control component。
- 在 Virtual TSK SPEC 裡應保留為主參數。

## `0x260.B5`

`B5` 以 signed 8-bit 解讀，再左移 8 bits。

分析方法：

- `B5 >= 128` 時轉成負數。
- 計算 `Int8(B5) << 8`。
- 與 `B2-B3` 合成 control value。
- 觀察 `B5` 是否在 large transition、seed-heavy、highway rerun 中呈現 coherent band。

目前判斷：

- `B5` 是 coarse control component。
- 它能補上 `B2-B3` 不能表達的大尺度區間。

## `0x116`

`0x116` 是 protected-lifecycle backbone 的核心 frame。

分析方法：

- 取 `B0-B1` 作為 `phase_hex`。
- 計算 `phase_sum = B0 + B1`。
- 將每筆 `0x116` 與 250 ms 內最近的 `0x131`、`0x260` 做 family 對齊。
- 若 `0x131` family 與 `0x260` family 同時落在 corridor zones，視為 corridor match。

重要 zones：

```text
TOP_TIER_ZONE = fff4
EXIT_ZONE = fff0
CORRIDOR_ZONES = fff4 / fff0 / ffee / ffeb / ffe8 / ffe7
```

事件判斷：

- `phase_hex == 0000` 且 family 為 `fff4|fff4`：`seed_touch_present`
- `1 <= phase_sum < 130` 且 family 為 `fff4|fff4`：`ramp_present`
- `phase_sum >= 130` 且 family 為 `fff4|fff4`：`phase_plateau_present`
- plateau 後 `family131 == fff4` 且 `family260 == fff0`：`phase_exit_present`

目前判斷：

- `0x116` 是 TSK-nearest lifecycle 最穩定的觀察入口。
- 它比 Virtual branch 裡的 `0xAA / 0x90 / 0x127 / 0x371` 更接近 protected lifecycle。

## `0x131`

`0x131` 是 steering companion / protected backbone 的重要 family source。

分析方法：

- 取 `B2-B3` 作為 family value。
- 對每筆 `0x116` 找 250 ms 內最近 `0x131`。
- 與 `0x260.B3-B4` family 比對是否同區、同 corridor、或同步進入 `fff4`。

目前判斷：

- `0x131` 與 `0x116`、`0x2E4` 一起形成 protected-lifecycle backbone。
- 在 SecOC steering validation 後，`0x131 / STEERING_LTA_2` 的角色更明確。

## `0x2E4`

`0x2E4` 在早期 Virtual TSK SPEC 裡是 protected activity marker；後續已確認是 `STEERING_LKA`。

分析方法：

- 在 feature table 裡先計算 `id_2e4_activity_level`。
- 檢查其是否出現在 valuable windows、protected lifecycle windows、SecOC steering windows。
- 後續用 SecOC AES-CMAC 驗證其 protected frame 結構。

目前判斷：

- `0x2E4` 不只是 TSK-nearest marker，而是 steering command frame。
- 在 Virtual TSK SPEC 中應保留，但角色要改成 steering SecOC / protected command evidence。

## `0xAA`

`0xAA` 曾被視為可能的 trigger，但驗證後降級為 contextual co-activity。

分析方法：

- 對 `0xAA.B0` 建立 time series。
- 找出 `0xAA.B0` 發生變化的時間點。
- 檢查每筆 `0x260` 前 20 ms 內是否有 `0xAA`。
- 另外檢查 `large260 change` 前 20 ms 內是否有 `0xAA transition`。

驗證結果：

```text
aa_near_260_ratio:
190101 = 0.937
171414 = 0.947
184921 = 0.949

aa_transition_near_large260_ratio:
190101 = 0.020
171414 = 0.086
184921 = 0.241
```

判讀：

- `0xAA` 經常在 `0x260` 附近出現。
- 但真正發生 `large260 change` 時，`0xAA transition` 對齊比例很低。
- 因此它不像主 trigger，比較像同一控制情境裡的背景活動。

## `0x90`

`0x90` 也曾被視為可能 trigger 或 request channel，但目前也偏向 contextual。

分析方法：

- 對 `0x90.B0-B1` 以 `Int16BE` 解析。
- 檢查每筆 `0x260` 前 20 ms 內是否存在 `0x90`。
- 與 `0xAA` 的結果比較，判斷它是否比 `0xAA` 更像 direct trigger。

驗證結果：

```text
n90_near_260_ratio:
190101 = 0.937
171414 = 0.945
184921 = 0.950
```

判讀：

- `0x90` 與 `0x260` 高度共現。
- 但目前缺少能證明它直接造成 `0x260` transition 的 evidence。
- 因此列為 partially validated / contextual support。

## `0x127`

`0x127` 曾被測試為 possible acknowledgment。

分析方法：

- 對 `0x127.B0-B1` 以 `Int16BE` 解析。
- 對每筆 `0x260` 找 20 ms 內下一筆 `0x127`。
- 檢查該 `0x127` 是否相對前一筆有變化。

驗證結果：

```text
n127_after_260_ratio:
190101 = 0.895
171414 = 0.893
184921 = 0.893

n127_changed_after_260_ratio:
190101 = 0.000
171414 = 0.000
184921 = 0.000
```

判讀：

- `0x127` 確實常跟在 `0x260` 後面。
- 但它幾乎不變，不像 active acknowledgment。
- 因此不能把它當作 command -> ack 的證據。

## `0x371`

`0x371` 曾被測試為 feedback channel。

分析方法：

- 對 `0x371.B2-B3` 同時以 `Int16BE` 與 `Int16LE` 解讀。
- 對每筆 `0x260` 找 50 ms 內下一筆 `0x371`。
- 計算 `0x260.control` 與 `0x371.B2-B3` 的 correlation。

驗證結果：

```text
corr_260_to_371_b23_be:
190101 = 0.063
171414 = 0.123
184921 = 0.859

corr_260_to_371_b23_le:
190101 = 0.032
171414 = -0.092
184921 = 0.198
```

判讀：

- `0x371` 在部分 sample 有強關聯，但跨 log 不穩。
- 它不能作為唯一 dominant feedback channel。
- 在 spec 中應標示為 sample-dependent feedback candidate。

## `0x191`

`0x191` 是 `0x260` 的 companion / side-channel 候選。

分析方法：

- 對 `0x191.B4-B5` 以 `Int16LE` 解讀。
- 對 `0x191.B6-B7` 以 `Int16BE` 解讀。
- 對 100 ms 內鄰近的 `0x260.control` 計算 correlation。

驗證結果：

```text
corr_260_to_191_b45:
190101 = -0.485
171414 = -0.151
184921 = -0.250

corr_260_to_191_b67:
190101 = 0.118
171414 = -0.025
184921 = -0.653
```

判讀：

- `0x191` 比 `0x371` 更像 companion context，但不同 sample 中主欄位不完全一致。
- `B4-B5` 與 `B6-B7` 都要保留觀察，不應只硬指定其中一組。

## Ladder / grade 參數

`ladder_level` 與 `grade` 用來把 log 的價值分層，不是車上原生 signal。

分析方法：

- 先看 `0x116` 是否出現 seed、ramp、plateau、exit。
- 再看 `0x131 / 0x260` family 是否進入 corridor 或 `fff4|fff4`。
- 最後依完整度分級。

分級邏輯：

```text
grade A = seed + ramp + plateau + exit
grade B = 有 seed，但缺完整 lifecycle
grade C = 有 corridor activity，但沒有 full seed state
grade D = 沒有 seed / corridor pattern
```

`ladder_level` 判斷：

```text
5 = grade A
4.5_candidate = seed + ramp + plateau，但 exit 尚未完整
3 = seed + ramp
2 = seed + corridor_ratio >= 0.20
1 = seed only
C_only = corridor_ratio >= 0.20
```

## 目前最重要結論

Virtual TSK SPEC 的參數不是同一層可信度：

- 最穩的是 `0x116 / 0x131 / 0x2E4` protected backbone。
- `0x260` 是最強 control-side anchor。
- `0x191` 是值得保留的 companion candidate。
- `0xAA / 0x90` 是 contextual co-activity，不應再被當作主 trigger。
- `0x127` 不支持 active acknowledgment 解讀。
- `0x371` 有 sample-dependent feedback 現象，但不能當唯一 feedback channel。

因此，後續整理 `VIRTUAL_TSK_SPEC_v2.md` 時，應把每個參數分成：

```text
validated backbone
control-side anchor
companion candidate
contextual co-activity
degraded / unproven hypothesis
```

這樣比較不會把早期假設、後期驗證結果與目前 SecOC key 已生效的狀態混在一起。
