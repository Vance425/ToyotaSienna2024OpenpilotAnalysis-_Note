# 被動式 TSK-Nearest 路線總覽

## 這份在講什麼

這份是目前整條被動式 `TSK-nearest` 路線的中文總覽。

目的不是解釋所有細節，而是把現在最重要的結論收成一頁：

- 我們離 TSK 最近的是哪條線
- 目前已經有哪幾個關鍵樣本
- 現在真正缺的是什麼
- 下一次該錄什麼才最有機會再往前一步

## 目前離 TSK 最近的主線

不是：

- `0x260 / 0x191`
- city stop-go 控制模型
- assist curve / deadband

而是：

- `0x116` 的 protected tail
- `0x131 / 0x116` 的 lifecycle
- `0x2E4` 作為次級 protected-family side channel

最短理解：

- `0x260 / 0x191` 比較像 control-path
- `0x116 / 0x131 / 0x2E4` 才是目前最接近 `TSK-nearest` 的被動證據鏈

## 目前最關鍵的樣本梯子

現在已經可以把舊樣本排成一條很清楚的梯子：

1. [toyota_seg_IGN_ON_20260312_185520_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_185520_000.ndjson)
   - `seed-touch only`
   - 最乾淨的 early partial-seed 參考

2. [toyota_seg_IGN_ON_20260314_173834_000.ndjson](../logs/toyota_seg_IGN_ON_20260314_173834_000.ndjson)
   - `ramping bridge`
   - 重複出現 local seed touch 與 local ramp

3. [toyota_seg_IGN_ON_20260311_184921_000.ndjson](../logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)
   - `compact ramping partial`
   - 比 `185520` 更有爬升，但還不夠完整

4. [toyota_seg_IGN_ON_20260315_171414_000.ndjson](../logs/toyota_seg_IGN_ON_20260315_171414_000.ndjson)
   - `strongest older partial-ramp`
   - 舊樣本裡最好的 seed-heavy entry-side 參考

5. [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)
   - `top-tier joined lifecycle anchor`
   - 目前唯一確認的 `Grade A` / 完整 joined lifecycle 樣本

對應資料：

- [tsk-nearest-ladder-entry-to-anchor.md](./tsk-nearest-ladder-entry-to-anchor.md)
- [tsk-nearest-old-sample-priority-table.md](./tsk-nearest-old-sample-priority-table.md)

## 這條梯子真正告訴我們什麼

現在最重要的缺口不是：

- 再找一個泛泛的 `Grade B`
- 再做一個 whole-log 的 control fit

而是：

- 找到一個樣本，能夠落在：
  - `171414_000`
  - 和
  - `190101_000`
  之間

也就是說，最值得找的不是普通 partial-seed，而是：

- 比 `171414` 更完整
- 但還沒有完全到 `190101`
- 真正的中間橋接態

## 已經確認過的事

### 1. 舊資料裡最像的 bridge 候選，大多已經掃過了

我們已經把剩下那批舊 `Grade C / corridor-only` 候選快速掃過：

- 最像的剩餘舊候選是：
  - $label (local-only source path)

但它目前看起來更像：

- corridor / promotion-side branch

不是：

- 真正夾在 `171414 -> 190101` 中間的 bridge sample

對應資料：

- [remaining-old-candidate-bridge-scan.md](./remaining-old-candidate-bridge-scan.md)

### 2. `0x2E4` 很重要，但不是主 lifecycle 判據

在 `185520 / 173834 / 171414 / 184921` 這些舊樣本裡，`0x2E4` 都很活。

它的角色比較像：

- protected-family side channel
- 結構活性參考線

不是：

- 單獨拿來決定哪個窗口最接近 `TSK` 的主判據

主判據還是：

- `0x116`
- `0x131`
- family context

### 3. `city` 樣本對 control 很有用，但對 TSK 比較遠

像 `2026-04-18` 這批城市 stop-go 樣本，對：

- `0x260`
- `0x191`
- `b4-b5 / b6-b7`

很有價值。

但對：

- protected-lifecycle 深化
- `TSK-nearest` bridge

幫助有限。

所以如果目標是接近 `TSK`，城市樣本不是第一優先。

## 現在最實用的工作句

如果要用一句話描述目前狀態，可以這樣說：

> 被動式 TSK-nearest 路線已經有一條清楚的樣本梯子，但目前仍缺少一個介於 `171414_000` 與 `190101_000` 之間的真正橋接樣本。

## 下一步最應該做什麼

不是再深挖城市 short stop-go。

而是：

- 錄一段連續 `IGN_ON`
- 城市出發
- `ACC_ON / LKAS_ON`
- 上快速道路或高速
- 維持一段 assisted follow
- 最好同一段 session 裡同時包含：
  - entry-side seed 行為
  - 後段 promoted-side 行為

對應錄制目標：

- [tsk-bridge-capture-target.md](./tsk-bridge-capture-target.md)

## 最後一句

現在被動式路線不是沒有方向。

相反地，方向已經很明確：

- 主線不是再找更多普通 `Grade B`
- 而是專門去打那個：
  - `171414_000 -> 190101_000`
  中間缺掉的 bridge state
