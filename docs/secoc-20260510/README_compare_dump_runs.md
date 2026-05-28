# compare_dump_runs.py

離線比對多次 SecOC dump run 的工具。

這支工具不接車、不連 Panda、不送 CAN、不寫 `SecOCKey`。它只比較多次 raw dump 的 byte 穩定性，用來區分：

- 固定 key-like material
- session-specific freshness
- counter / status bytes
- 全零或 erased/fill pattern
- 可能 dump range 錯誤的區段

## 基本用法

至少給兩個 dump run 目錄：

```sh
python3 compare_dump_runs.py \
  /data/secoc_dumps/sienna2024_secoc_dump_20260509_120000 \
  /data/secoc_dumps/sienna2024_secoc_dump_20260509_121500
```

WSL 下如果 dump 放在 `<LOCAL_CODEX>\secoc\dumps`：

```sh
cd <LOCAL_CODEX_WSL>/secoc

python3 compare_dump_runs.py \
  <LOCAL_CODEX_WSL>/secoc/dumps/sienna2024_secoc_dump_20260509_120000 \
  <LOCAL_CODEX_WSL>/secoc/dumps/sienna2024_secoc_dump_20260509_121500 \
  --output-dir <LOCAL_CODEX_WSL>/secoc/out/compare_20260509_2runs
```

也可以直接指定多個 `.bin` 檔，但建議用整個 run 目錄，因為工具可以讀 `metadata*.json` 裡的 dump range。

## 輸出

```text
run_compare_report.md
run_compare_summary.json
stable_candidates.csv
variable_regions.csv
```

## stable_candidates.csv

這裡列出跨 run 完全一致、且看起來比較像 key material 的 16-byte windows。

重要欄位：

- `group_key`: dump range 分組，例如 `febe6e34_febe6ff4`
- `offset`: dump 檔內 offset
- `absolute_address`: 若 metadata/range 可解析，會換算成絕對位址
- `candidate_hex`: 16-byte 候選
- `old_checksum_all`: 所有 run 在舊 checksum 規則下都通過
- `notes`: 例如 `old_key_offset_all`、`aligned16`、`key_like_entropy`

`old_key_offset_all` 很重要，表示 candidate 剛好落在舊版假設的：

```text
struct size 0x20
key offset 0x0c
checksum offset 0x1d
```

但這仍然只是候選，不代表已驗證是 Sienna 2024 的 SecOC key。

## variable_regions.csv

這裡列出跨 run 會變的區段。

常見解讀：

- `all_runs_unique`: 可能是 freshness、session state、seed/random、counter-like material
- `partially_changing`: 可能是 counter/status field 靠近固定資料
- `mixed`: 有些 run 一樣、有些不一樣，需要更多 run 判斷

## 建議使用時機

1. 至少取得兩次正式 `SECOC DUMP`
2. 最好包含：
   - 同一次上電連續 dump
   - ignition cycle 後 dump
   - openpilot 狀態不同時 dump
3. 用這支工具找：
   - 每次都穩定的 16-byte candidate
   - 每次都變的 freshness-like 區段
   - 變動區旁邊是否有固定 key-like material

## 重要限制

穩定不變不等於 key 正確。

這支工具只回答：

```text
哪些 bytes 在多次 dump 之間穩定？
哪些 bytes 會變？
哪些穩定 bytes 比較像舊 SecOC key table 的候選？
```

真正驗證 candidate 是否可用，需要下一支工具 `validate_secoc_candidate.py` 或和 openpilot 錯誤層級一起比對。
