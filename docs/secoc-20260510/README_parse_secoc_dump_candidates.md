# parse_secoc_dump_candidates.py

離線解析 SecOC dump candidate 的工具。

這支工具不接車、不連 Panda、不送 CAN、不寫 `SecOCKey`。它只讀取 dump-only 工具產生的 raw dump，掃描可能的 key-like byte ranges 與 layout hints。

## 基本用法

解析單一 dump 目錄：

```sh
python3 parse_secoc_dump_candidates.py /data/secoc_dumps/sienna2024_secoc_dump_YYYYMMDD_HHMMSS
```

指定輸出目錄：

```sh
python3 parse_secoc_dump_candidates.py \
  /data/secoc_dumps/sienna2024_secoc_dump_YYYYMMDD_HHMMSS \
  --output-dir /data/secoc_dumps/parse_YYYYMMDD_HHMMSS
```

解析多個 dump：

```sh
python3 parse_secoc_dump_candidates.py \
  /data/secoc_dumps/sienna2024_secoc_dump_20260509_120000 \
  /data/secoc_dumps/sienna2024_secoc_dump_20260509_121500
```

## 輸出

預設會產生：

- `candidate_report.md`
- `candidate_keys.csv`
- `layout_hypotheses.json`

## 掃描內容

目前會掃：

- 16-byte candidate windows
- entropy / unique byte count
- zero / ff / printable ASCII ratio
- marker 附近候選
- `0x20` / `0x30` / `0x40` struct layout
- 舊版 checksum 規則
  - struct size: `0x20`
  - checksum offset: `0x1d`
  - old key offset: `0x0c`
- 每個 dump 的 high-entropy regions

## 重要限制

`candidate_keys.csv` 裡的 candidate 只是「值得人工比對的候選」，不是已驗證的 Toyota Sienna 2024 SecOC key。

如果只看到：

- 全零
- 全 `ff`
- 很多 printable ASCII
- checksum hit 但 entropy 很低

通常不應直接視為 key。

真正比較有價值的是：

- 多次 dump 都穩定出現在同一 offset
- entropy 高
- 不是全零/全 ff/純 ASCII
- 周圍 layout 重複性合理
- 和舊 checksum 或新 checksum 假設能一致

下一步應交給 `compare_dump_runs.py` 類型工具做跨 run 穩定性比對。
