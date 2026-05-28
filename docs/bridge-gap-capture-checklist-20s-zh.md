# Bridge-Gap 錄製清單 20s 版

## 目標

不是再錄一段短 burst。

要錄到的是：

- 比 `20260426 Tier A` 更完整
- 有機會高於 `171414`
- 但還沒到 `190101`

## 路線

照這個順序最有機會：

1. 市區出發
2. 早點開 `ACC`
3. 早點開 `LKAS`
4. 上快速道路 / 高速
5. 有前車可跟
6. 連續 assisted follow 幾分鐘
7. 不要剛起來就解除

## 時長

- 最低可用：
  - `8` 分鐘
- 最好：
  - `10-20` 分鐘
- 一定要：
  - `連續 IGN_ON`

## 最重要的 marker

只記大概時間就夠：

- `ACC_ON`
- `LKAS_ON`
- `FREEWAY_ENTRY`
- `FREEWAY_EXIT`

如果有再補：

- 明顯長時間跟車開始
- 明顯踩煞車解除
- `C3X_WARNING`
- `C3X_ERROR`

## 避免

這幾種最容易又只錄到次級樣本：

- 純市區 stop-go
- 空高速，前面沒車
- 很短的 assisted follow
- 一直人工解除 / 反覆接管
- 只錄到晚段 recovery burst

## 成功樣子

錄完如果大致像這樣，就值得優先分析：

- 同一趟裡有：
  - entry-side rise
  - freeway assisted follow
  - 後段還有穩定路段
- 不是只有 seed + ramp 的短 burst

## 一句話

**市區起步，早開 ACC/LKAS，上快速道路後跟車幾分鐘，整趟連續錄，盡量不要很快手動解除。**
