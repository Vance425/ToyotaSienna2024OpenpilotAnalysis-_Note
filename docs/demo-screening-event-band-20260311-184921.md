# 第四輪示範: 事件帶分析

## 為什麼要做事件帶

第三輪之後可以看出來：

- `0x610` 不是只跳一次
- 它從某個時間點開始進入連續變化

這代表我們不能只把它看成單點事件，應該把它看成：

`一段持續的 steering/state event band`

## 先看 0x610 的變化帶

在 [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson) 中，`0x610` 從以下時間開始連續變化：

- `1773255027173`
- `1773255027667`
- `1773255027782`
- `1773255028267`
- `1773255028771`
- `1773255029270`
- `1773255029768`
- `1773255029871`
- `1773255030370`
- `1773255031370`

這說明：

- 這不是單一瞬間異常
- 這是一段持續中的狀態 / steering session

## 用 anchor 判斷哪些點最像高價值窗口

我以每個 `0x610` 變化點當 anchor，檢查附近小窗口裡是否同時出現：

- `0x131 resetlike`
- `0x116 phase change`
- `0x260 prefix change`
- 且 `0xD5` 不變

## 目前最漂亮的 anchor

### Anchor: `1773255027173`

在這個 anchor 附近：

- `0x131 resetlike`: `True`
- `0x116 phase change`: `True`
- `0x260 prefix change`: `True`
- `0xD5 changed`: `False`

這是目前最乾淨、最值得當示範與後續對照的窗口。

## 次級 anchor

### `1773255028267`

- `0x131 resetlike`: `True`
- `0x116 phase change`: `True`
- `0x260 prefix change`: `True`
- `0xD5 changed`: `False`

這也是很有價值的候選點。

### `1773255031370`

- `0x131 resetlike`: `True`
- `0x116 phase change`: `False`
- `0x260 prefix change`: `True`
- `0xD5 changed`: `False`

這比較像部分候選同步，而不是最完整的組合。

## 目前最有利的判讀

### 1. 真正值得找的不是單一故障點，而是一段事件帶

這段 log 告訴我們：

- steering/state 相關事件會延續一段時間
- 候選線會在這段帶內反覆出現結構性變化

### 2. 不是每個 0x610 變化點都一樣有價值

有些 anchor 只有：

- `0x260` 在變

但比較好的 anchor 會同時有：

- `0x131 resetlike`
- `0x116 phase change`
- `0x260 prefix change`
- `0xD5` 不動

### 3. 目前最佳候選事件帶入口仍然是 1773255027173

所以：

- 如果後面要做更深人工篩選
- 或要和其他 log 比較
- 這個 anchor 最適合當第一個模板

## 第四輪示範結論

目前這段 log 裡，最值得記住的不是「單一可疑 frame」，而是：

- 我們已經找到一個可重複使用的事件帶模板

模板條件是：

1. `0x610` 有明顯事件點
2. `0xD5` 不動
3. `0x131` 出現 resetlike
4. `0x116` 出現 phase change
5. `0x260` 出現 prefix change

這個模板之後可以拿去掃其他 log，找出更像 `comma 3X` 失敗的窗口。
