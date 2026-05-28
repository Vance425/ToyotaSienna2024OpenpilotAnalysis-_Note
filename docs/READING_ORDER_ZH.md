# 中文閱讀順序

這份文件是 `ToyotaSienna2024OpenpilotAnalysis` 的中文入口索引。建議先看主線結論，再看 SecOC / TSK 細節，最後才進入各 session review、scripts 與 raw log。

索引中的英文多半是檔名、script 名稱、frame 名稱或研究標籤，這些內容保留原文是為了方便直接搜尋與交叉比對。每一節都會用中文說明閱讀目的，讓讀者知道為什麼要看該組文件。

## 1. 先看專案狀態

1. [README.md](../README.md)
2. [PROJECT_STATUS.md](../PROJECT_STATUS.md)
3. [OPENPILOT_INTEGRATION_PROGRESS_REPORT.md](../OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)
4. [PROJECT_PROGRESS.md](../PROJECT_PROGRESS.md)

先讀這四份，可以知道目前不是單純 reverse engineering，而是已進入 implementation-stage bottleneck。

## 2. 看目前總結

1. [current-conclusion-20260525-zh.md](current-conclusion-20260525-zh.md)
2. [research-update-20260525-zh.md](research-update-20260525-zh.md)
3. [current-findings-summary-v2.md](current-findings-summary-v2.md)
4. [current-project-status-zh.md](current-project-status-zh.md)

這一組回答：

- `TSK` 到底確認到什麼程度
- `C3X` lateral / longitudinal 是否已工作
- `SecOCKey`、freshness、MAC packing 還缺什麼

## 3. 看 SecOC / TSK 主線

1. [secoc-20260522-steering-lka-key-validation-full-zh.md](secoc-20260522-steering-lka-key-validation-full-zh.md)
2. [secoc-20260510/dataflash-direct-dump-summary-zh.md](secoc-20260510/dataflash-direct-dump-summary-zh.md)
3. [passive-tsk-nearest-overview-zh.md](passive-tsk-nearest-overview-zh.md)
4. [tsk-nearest-ladder-entry-to-anchor.md](tsk-nearest-ladder-entry-to-anchor.md)
5. [VIRTUAL_TSK_SPEC_v2.md](VIRTUAL_TSK_SPEC_v2.md)

這一組回答：

- `0x2E4 / STEERING_LKA` 如何被確認
- `0x131 / STEERING_LTA_2` 如何成為 companion protected frame
- passive `TSK-nearest` ladder 如何建立
- direct DATAFLASH branch 做到哪裡、不能宣稱什麼

## 4. 看 control-side 與 replay-backed 分析

1. [openpilot-control-side-working-note.md](openpilot-control-side-working-note.md)
2. [final-frame-role-map.md](final-frame-role-map.md)
3. [replay-backed-simulation-plan.md](replay-backed-simulation-plan.md)
4. [replay-backed-simulation-round6.md](replay-backed-simulation-round6.md)
5. [transition-settle-shaping-experiment-round6.md](transition-settle-shaping-experiment-round6.md)

這一組回答：

- `0x260` 為何是目前最穩 control-side anchor
- `0x191` 為何是 regime-dependent companion
- replay-backed branch 目前支持哪些 working assumptions

## 5. 看 session / log review

建議先看：

1. [included-logs.md](included-logs.md)
2. [session-review-20260316.md](session-review-20260316.md)
3. [session-review-20260418-two-city-runs.md](session-review-20260418-two-city-runs.md)
4. [session-review-20260426-complete.md](session-review-20260426-complete.md)
5. [session-review-20260509-first-pass-zh.md](session-review-20260509-first-pass-zh.md)
6. [session-review-20260509-session3-high-region-detailed-zh.md](session-review-20260509-session3-high-region-detailed-zh.md)

再依需求進入各日期細節。

## 6. 看 workflow / checklist

1. [implementation-prerequisite-checklist.md](implementation-prerequisite-checklist.md)
2. [implementation-prerequisites-vs-working-assumptions.md](implementation-prerequisites-vs-working-assumptions.md)
3. [post-secoc-key-remaining-checklist-zh.md](post-secoc-key-remaining-checklist-zh.md)
4. [bridge-gap-capture-checklist-20s-zh.md](bridge-gap-capture-checklist-20s-zh.md)
5. [new-log-standard-workflow.md](new-log-standard-workflow.md)

這一組用來決定下一次實車 / log capture / implementation validation 要做什麼。

## 7. 看 public reference 與車輛資料

1. [public-references-map.md](public-references-map.md)
2. [public-references-map-zh.md](public-references-map-zh.md)
3. [vehicle-record-final.md](vehicle-record-final.md)
4. [vehicle-field-priority-map.md](vehicle-field-priority-map.md)

這一組用來補背景與 go/no-go 判斷。

## 8. 看 scripts

Scripts 保留英文原文，不做中文化改名。

常用入口：

```text
scripts/grade_can_logs.py
scripts/generate_log_feature_table.py
scripts/replay_backed_simulation.py
scripts/secoc/secoc_key_probe.mjs
scripts/secoc/secoc_2e4_freshness_profile.py
scripts/session_window_triage.py
```

執行 scripts 前，先確認 input path 是否指向本機實際 raw log 位置。

## 閱讀方式補充

這個 repository 不是一般線性教學文件，而是長期研究工作區整理出來的知識庫。許多文件名稱保留英文，是因為它們對應到既有 script、log、資料表或歷史分析批次。閱讀時建議不要從 `docs/` 隨機點開，而是先照本索引建立主線，再依照你要處理的問題進入對應群組。

如果目標是理解目前狀態，先看專案狀態與目前總結。如果目標是理解 SecOC key，先看 steering validation 與 DATAFLASH direct branch。如果目標是跑工具，先看 workflow / checklist，再確認 raw log 路徑。這樣比較不會把舊方法、passive 分析、direct validation 與實車 implementation 混在一起。

後續整理時也建議維持這個分層：入口文件負責說明目前判斷，主線文件負責保留證據與限制，session 文件負責保存歷史觀察，scripts 文件負責保留可重跑工具。這樣即使資料量很大，讀者仍能知道自己正在看的文件屬於哪一層，避免把某次中間觀察誤當成最終結論。
