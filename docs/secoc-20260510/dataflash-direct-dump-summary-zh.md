# 2026-05-10 Sienna 2024 EPS SecOC DATAFLASH Direct Dump Summary

本文件整理 2026-05-10 針對 Toyota Sienna 2024 EPS 進行的直接 SecOC / DATAFLASH dump 測試結果。

## 結論

- `sienna_2024_eps_dataflash` 路線已可從 EPS 端讀回大量 DATAFLASH 內容。
- 目前目標範圍是 `0xff200000` 到 `0xff208000`，總長 `32768` bytes。
- 單次有效 run 約可取得 `16724` 到 `17048` bytes。
- 最新 5 次有效 run 合併後覆蓋 `31916 / 32768` bytes，約 `97.4%`。
- 目前尚未取得可接受的穩定 TSK / SecOC key。
- 跨 run 比對顯示大量內容會變動，推測此區含 session state、freshness、counter、random 或 runtime material，不適合把單次高 entropy 片段直接當成 TSK。

## 工具狀態

已整理到 `scripts/secoc/`：

- `extract_keys_sienna2024_dump_only.py`
- `parse_secoc_dump_candidates.py`
- `compare_dump_runs.py`
- `validate_secoc_candidate.py`
- `convert_old_secoc_dump_log.py`
- `patch_secoc_payload_dump_range.py`

重要保護與功能：

- 非 dry-run DATAFLASH dump 需要明確 parked ack。
- timeout 時仍會保留 partial dump。
- metadata 會寫入 partial dump bytes / frames。
- 工具已改為更適合 sparse dump 的解析方向，避免把未回傳位置誤判成真實 zero。

注意：本 GitHub bundle 不包含原始車端 dump `.bin` 或 payload `.bin`。這些仍留在本機 / C3X，避免把車端原始資料直接公開。

## 有效樣本

來源目錄：`<LOCAL_TEMP>\secoc_dumps\NEW`

| run | profile | result | partial bytes | frames | note |
|---|---|---:|---:|---:|---|
| `20260510_050627` | `sienna_2024_eps_dataflash` | partial | `16824` | `4206` | idle timeout at `0xff200008` |
| `20260510_050727` | `sienna_2024_eps_dataflash` | partial | `17048` | `4262` | idle timeout at `0xff200000` |
| `20260510_050947` | `sienna_2024_eps_dataflash` | partial | `17016` | `4254` | idle timeout at `0xff200008` |
| `20260510_051107` | `sienna_2024_eps_dataflash` | partial | `16900` | `4225` | idle timeout at `0xff200008` |
| `20260510_051336` | `sienna_2024_eps_dataflash` | partial | `16724` | `4181` | idle timeout at `0xff200010` |

其他觀察：

- `20260510_050840` 與 `20260510_051133` 為 response timeout。
- `20260510_051422` 回覆 `DIAGNOSTIC_SESSION_CONTROL - conditions not correct`。
- 這支持目前現場 SOP：C3X 可不重啟，但車輛 IG OFF/ON 後再跑下一次 DATAFLASH，不建議同一次車端狀態連續跑多次。

## 覆蓋結果

已輸出：

- [coverage_summary.json](./coverage_summary.json)

重點：

- union slots: `7979`
- union bytes: `31916`
- intersection slots: `288`
- intersection bytes: `1152`
- conflict slots: `1084`
- first missing union: `0xff20005c`
- first conflicts include `0xff200018`, `0xff200040`, `0xff20006c`, `0xff20007c`

解讀：

- 多次 partial dump 的合併策略有效，可以接近完整覆蓋。
- 但交集很小、conflict 不少，表示同一 DATAFLASH 範圍內有不少資料不是穩定常數。

## Candidate Scan

已輸出：

- [candidate_report.md](./candidate_report.md)

merged coverage dump 的前幾名 high-entropy candidates：

| offset | candidate |
|---:|---|
| `0x6410` | `xxxxxx` |
| `0x4da8` | `xxxxxx` |
| `0x6c14` | `xxxxxx` |
| `0x6dd4` | `xxxxxx` |
| `0x6ed4` | `xxxxxx` |

這些只能視為候選材料，不能視為已取得 key。原因是跨 run 穩定性尚未通過。

## Cross-Run Compare

已輸出：

- [run_compare_report.md](./run_compare_report.md)
- [stable_candidates.csv](./stable_candidates.csv)
- [variable_regions.csv](./variable_regions.csv)

重點：

- compared size: `32764`
- changed bytes: `14938`
- changed ratio: `0.455927`
- stable non-zero bytes: `117`
- stable zero bytes: `17489`
- stable candidates: none matched threshold

最高變動區包含：

- `0xff2008f0`
- `0xff200db0`
- `0xff201270`
- `0xff2012b0`
- `0xff2013b0`
- `0xff2014f0`
- `0xff2015b0`
- `0xff201a70`
- `0xff201d70`
- `0xff201e30`

解讀：

- 目前不像是「直接 dump 一次就能拿到固定 key」。
- 下一步應把 variable regions 當成 session/freshness 候選區，而不是立即當 key。

## 下次收集 SOP

1. 車輛停妥，P 檔，安全位置。
2. C3X 可以保持開機，不必重啟。
3. 每次 DATAFLASH 前，車輛做一次 IG OFF/ON。
4. 一次車端 power cycle 只跑一次 `SECOC DATAFLASH`。
5. 跑完後保留 output folder，不覆蓋舊資料。
6. 收集至少 5 到 10 次獨立 power cycle 樣本。
7. 不要在行駛中跑；先前已觀察到 EPS power steering assist low 類型提示。

## 下一步

- 用最新工具重新收集，確保 metadata 帶有 partial dump 與 sparse coverage 資訊。
- 對新樣本重新跑 `parse -> compare -> validate`。
- 增加 coverage-aware compare：只比較各 run 確認有回傳的位置。
- 對 all-runs-unique variable regions 做 session/freshness 聚類。
- 若要驗證 candidate，必須先找到跨 power-cycle 穩定或可被 seed/session 解釋的材料。
