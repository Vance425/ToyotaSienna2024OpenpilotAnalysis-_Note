# Nibble / Counter Hypothesis

## 為什麼現在該看 nibble

現在已知：

- `0x116` 的 tail 不會因為 phase 固定就停止變化
- 也不會因為 state base 固定就停止變化

所以下一步最值得看的，是 tail 裡面是否藏著：

- nibble-level counter
- rolling low bits
- 或可切分的短週期欄位

## 接下來最值得做的檢查

1. 把 `0x116.b4-b7` 拆成 8 個 nibble
2. 看哪幾個 nibble 變化頻率比較穩
3. 看是否有 nibble 在固定 phase 內呈現單步遞進或循環
4. 把高頻 nibble 和低頻 nibble 分開

## 目標

不是直接解 tag，而是先回答：

- tail 裡有沒有「看起來像 counter」的部分
- 哪些 nibble 比較像純高熵區

## 如果結果成立

那我們就能把 `0x116 tail` 再拆成：

- candidate rolling bits
- candidate auth-heavy bits

這會比現在直接把 4 bytes 整塊看待更有效。
