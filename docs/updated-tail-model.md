# Updated Tail Model

## 目前對 `0x116 tail` 的最新模型

根據 nibble transition 檢查，`0x116.b4-b7` 現在比較像三層混合：

- `n0`: 相對最有規律的 rolling 候選
- `n1-n3`: 過渡混合區
- `n4-n7`: 較高熵區

## 這代表什麼

這代表我們不應再把 `0x116 tail` 想成：

- 單一 checksum
- 單一 counter
- 或全 32-bit 等價高熵輸出

更合理的是：

- tail 內部可能有分工
- 有些 nibble 比較像短週期 rolling 元件
- 有些 nibble 比較像真正 auth-heavy 區

## 目前最值得優先盯的 tail 位置

1. `n0`
2. `n1`
3. `n3`

這三個位置現在比其他 nibble 更值得看。

## 現在可以先降權的

- 想直接從整個 32-bit tail 逆推出固定公式
- 把 `n4-n7` 當成簡單 counter

這兩條路目前看起來都不像高勝率入口。

## 下一步主線

下一輪最值得做的是：

- 檢查 `n0` 是否在 phase 邊界前後有固定轉折
- 檢查 `n1/n3` 是否在某些 family state 下停住或重複
