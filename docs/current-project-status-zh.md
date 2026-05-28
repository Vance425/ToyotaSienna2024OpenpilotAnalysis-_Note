# 目前專案進度總表

更新時間：

- `2026-05-07`

## 目的

這份文件把目前專案狀態壓成一頁，回答三件事：

1. 目前已完成什麼
2. 目前還缺什麼
3. 接下來最應該怎麼做

主要參考：

- [current-findings-summary-v2.md](./current-findings-summary-v2.md)
- [implementation-prerequisite-checklist.md](./implementation-prerequisite-checklist.md)
- [blocked-priority-and-bridge-shortlist.md](./blocked-priority-and-bridge-shortlist.md)
- [OPENPILOT_INTEGRATION_PROGRESS_REPORT.md](../OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)

## 一句話總結

目前專案已經完成：

- 被動 `TSK-nearest` 主 backbone 收斂
- control-side replay 主分支收斂
- city `transition / settle` 本地 shaping rule 驗證

但仍然缺：

- `171414 -> 190101` 之間的 **bridge-gap closure**
- `0x2E4` 的 operational meaning
- secure/auth closure

所以現在最正確的狀態是：

- **可以做 bounded 的 implementation-side planning**
- **還不能做 implementation-grade claims**

## 已完成項目

### 1. 被動主 backbone 已穩定

目前最穩的 `TSK-nearest` 主線是：

- `0x116`
- `0x131`
- `0x2E4`

這條線已經足夠穩定，可作為後續所有判讀的主 backbone。

### 2. `TSK-nearest` 梯子已建立

目前固定梯子為：

1. `20260312_185520_000`
   - seed-touch only
2. `20260314_173834_000`
   - ramping bridge
3. `20260311_184921_000`
   - compact ramping partial
4. `20260315_171414_000`
   - strongest older partial-ramp
5. `20260312_190101_000`
   - top-tier joined lifecycle anchor

其中：

- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)
  仍然是目前最重要的 anchor。

### 3. `Virtual TSK` 已重新定位

目前不是把 `VIRTUAL_TSK` 當成最終權威。

正確定位是：

- [VIRTUAL_TSK_SPEC_v2.md](./VIRTUAL_TSK_SPEC_v2.md)
  = **working spec**

目前較站得住的是：

- `0x260` 控制側分支
- `0x371` 在部分 regime 下像 feedback

目前較不站得住的是：

- 嚴格的 `0xAA -> 0x90/0x260 -> 0x127 -> 0x371` 完整握手鏈

### 4. longitudinal candidate map 已建立

目前最穩的 longitudinal/control-side 角色是：

- `0x260`
  - control-side anchor
- `0x116 / 0x131 / 0x2E4 / 0xD8 / 0x90`
  - 重要同步移動群
- `0x191 / 0x371`
  - response-side / companion-side 候選

### 5. replay 主分支已收斂

目前最強的 replay-backed working branch 是：

- `decode_mode = no_b1_flip`
- `mode = identity`
- `higher slew`

現在：

- `legacy_ff_negative`
- `bounded`

都已降為 comparison branch，不再是主候選。

### 6. city-side replay 難點已拆清楚

目前已經分清：

- `active-core`
- `late-stop approach`
- `transition / settle`
- `final hold`

其中：

- `active-core` 已可接受
- `final hold` 已可接受
- 真正難的是：
  - `transition / settle`

### 7. city-side local working rule 已建立

目前最強本地 rule 是：

- `low-band catch-up 5.5x`
- `deeper-negative helper 2.5x`
- 只在 `transition / settle` 子相位啟用

而且這條 rule：

- 已在原始窗口成立
- 已在第二個城市 `transition/settle` 窗口復現
- 沒有傷到相鄰 `approach` 或 `final hold`

### 8. `20260426` 這批已完整定位

這批資料現在的定位很清楚：

- 很有價值
- 主要補的是：
  - partial-seed
  - entry-side
  - mixed-route burst 參考
- 但沒有補上 bridge-gap

其中：

- `Session 1`
  - 穩定 repeated entry-side / partial-seed
- `Session 2`
  - mixed route / 最適合 pocket hunting
- `Session 3`
  - compact entry-side

## 尚未完成項目

### 1. bridge-gap closure

目前仍然缺：

- 一個比 `171414` 更完整
- 但還沒到 `190101`

的真正 bridge-target 樣本。

這是現在最重要的未完成項目。

### 2. `0x2E4` operational meaning

目前已知：

- `0x2E4` 分析上非常有價值
- 常常和高價值窗口同場

但還不知道：

- 它是不是只能當 side channel
- 還是有更強的 operational meaning

### 3. secure/auth closure

目前 replay/control-side 再強，也還不等於：

- freshness closure
- auth closure
- injection closure

這一層還沒完成。

### 4. final normalized mapping

目前已經有很強的 replay 分支，
但還沒有：

- implementation-grade 的 normalized control mapping

所以還不能說：

- 已經完成 openpilot -> ACU setpoint 的最終映射

### 5. final global slew gate

目前知道：

- 高 slew 分支在 replay 裡表現更好

但還不知道：

- 哪個 slew 值具有 deployment-level 的意義

## 當前阻塞項目優先級

目前 blocked priority 是：

1. `bridge-gap closure`
2. `0x2E4 operational meaning`
3. `secure/auth closure`

這個順序現在很重要，因為：

- 如果 bridge-gap 不補上
- 後兩項會一直處在 underconstrained 狀態

## 接下來怎麼做

### 第一優先：錄新的 bridge-target log

現在邊際價值最高的，不是再挖同一批舊 log，  
而是錄一段更像 bridge-gap 的新樣本。

直接照這兩份做：

- 詳細版：
  - [bridge-gap-capture-plan-v2.md](./bridge-gap-capture-plan-v2.md)
- 超短版：
  - [bridge-gap-capture-checklist-20s-zh.md](./bridge-gap-capture-checklist-20s-zh.md)

最理想路況：

1. 市區出發
2. 早點開 `ACC`
3. 早點開 `LKAS`
4. 上快速道路 / 高速
5. 前方有車可跟
6. 持續 assisted follow 幾分鐘
7. 不要剛起來就手動解除

### 第二優先：新 log 回來後直接按模板判

新 log 一到，就按這份跑：

- [next-log-analysis-template.md](./next-log-analysis-template.md)

順序是：

1. 先切 session
2. 看是否命中 bridge candidate
3. 看落在 ladder 哪一層
4. 看 `0x191` 該怎麼讀
5. 再決定是不是值得深切

### 第三優先：如果新 log 還補不上 bridge-gap

才往下一層推：

- `0x2E4` operational meaning
- 更強的 secure/auth 邏輯閉合

也就是說：

- **bridge-gap 還是主線**
- 不是現在就直接跳去 implementation claim

## 現在不該做什麼

目前不該直接宣稱：

- `VIRTUAL_TSK_SPEC_v2` 已定案
- `0x2E4 -> 0x260` 已是嚴格 trigger/heartbeat
- replay 分支已經等於實車 implementation
- 目前 corpus 已足夠推出真正 `TSK`
- 已經可以做 implementation-grade injection claim

## 最短收尾

目前專案已經把：

- passive backbone
- replay 主分支
- city-side 難點

都收斂得很清楚了。

現在真正最缺的，不是再多一份總結，  
而是：

- **一段比 `171414` 更深、但還沒到 `190101` 的新 bridge-target log**
