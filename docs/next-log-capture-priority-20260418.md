# 下一批 Log 錄製優先級

## 先講結論

目前最值得錄的，不是更多短段，也不是原地切開關。

最值得的是：

- 有明確 regime 變化
- 有可標記事件
- 有足夠長度的連續 `IGN_ON` session

一句話：

> 現在最缺的不是更多零碎 log，而是能切出乾淨 local band 的長 session。

## 錄製目標

下一批 log 的最低標準：

- 至少一段連續 `IGN_ON` 超過 `3-5` 分鐘
- 更理想是 `5-10` 分鐘
- 不要中途因 notebook / terminal 關閉而停掉
- 要打 manual marker

## 最值得保留的事件

至少要能標這幾種：

- `ACC_ON`
- `LKAS_ON`
- `FREEWAY_ENTRY`
- `FREEWAY_EXIT`
- `RED_LIGHT_STOP`
- `TURN_LEFT`
- `TURN_RIGHT`
- `U_TURN`
- `C3X_WARNING`
- `C3X_ERROR`

原因：

- 目前方法已經是 regime-first
- 沒有事件標記，後面切 band 會慢很多

## 最值得的路線類型

### 類型 A：城市 -> 快速道路 -> 穩定行駛

這是第一優先。

想要的結構：

1. 市區低速 / 停走
2. `ACC/LKAS` 開啟
3. 上快速道路
4. 保持一段穩定行駛
5. 再出現一次邊界事件

為什麼：

- 這種路線最容易同時看到：
  - boundary-rich
  - seed-heavy
  - promoted / plateau-heavy

### 類型 B：單一乾淨高速穩定段

這是第二優先。

用途：

- 專門看 promoted / stable regime
- 對 `0x191.b4-b5` 類 companion 很有用

### 類型 C：城市停走 / 多轉向 / 多邊界段

這是第三優先。

用途：

- 專門看 boundary / seed-heavy 行為
- 對 `0x131 / 0x116` lifecycle 很有用

## 不值得優先錄的內容

這些現在優先級低：

- 幾十秒就結束的短 session
- 原地開關 `ACC/LKAS`
- 沒有 marker 的混合長段
- 只錄到 `IGN_OFF` / `UNKNOWN`
- 啟動後馬上停止

原因：

- 這些通常只會得到：
  - `Grade D`
  - 無法切 regime
  - 無法做 local `v22`

## 目前最想看到的兩種樣本

### 樣本 1：`0311` 類局部乾淨 band

目標：

- 再找一次類似 `0311 Band B`
- 觀察 `0x191.b6-b7`

### 樣本 2：`0316 promoted` 類局部 band

目標：

- 再找一次 promoted positive slice
- 觀察 `0x191.b4-b5`

## 實際錄製建議

### 最小可用版本

- 啟動 logger
- 確認 pid 還在
- 保持錄製 `5` 分鐘以上
- 至少打一組 marker：
  - `ACC_ON`
  - `LKAS_ON`
  - `FREEWAY_ENTRY`
  - `FREEWAY_EXIT`

### 理想版本

- `IGN_ON` 全程連續
- `5-10` 分鐘
- 有城市段
- 有快速道路段
- 有穩定巡航段
- 有一到兩次邊界事件
- 有完整 marker

## 跑完後怎麼處理

下一批 log 進來後，照這個順序：

1. 看 `session_manifest / events / health_summary`
2. 跑 auto grading
3. 做 phenomenon map
4. 先切 band
5. 按 regime 選 `0x191` 字段
6. 最後才做 local `v22`

## 最短工作句

如果只留一句給錄製者：

> 請錄一段至少 5 分鐘的連續 `IGN_ON`，含城市到快速道路切換，並在 `ACC_ON`、`LKAS_ON`、`FREEWAY_ENTRY`、`FREEWAY_EXIT` 時打 marker。
