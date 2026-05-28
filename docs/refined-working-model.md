# Refined Working Model

## 目前最精煉的工作模型

根據目前所有被動分析，`0x116 / 0x131 / 0x260` 的最合理結構是：

- `0x131`: boundary / state indicator
- `0x260`: family sync / state snapshot
- `0x116.b0-b1`: phase selector
- `0x116.tail.n0`: rolling nibble with `+4` backbone
- `0x116.tail.n1/n3`: transition region
- `0x116.tail.n4-n7`: auth-heavy region

## `n0` 的最新描述

`n0` 現在不只是「像 rolling」而已，可以再具體一點：

- phase 內常以 `+4` 為主要步進
- phase 邊界附近會重定相
- 某些 phase 的 steady 段仍會插入修正步進

## 目前最好的高信心句子

如果要用一句話描述現在最有把握的發現，就是：

`0x116` 很像一條受 `0x131/0x260` family state 約束、並在 phase 內帶有 `+4` rolling nibble 的 protected frame。

## 接下來最值得做的事

下一步最有價值的不是再擴大候選，而是：

1. 以 `184921 / 27 00` 和 `185451 / 09 0a` 當乾淨基準
2. 檢查 `n1/n3` 在 steady 段是否也有弱規律
3. 再看 `n4-n7` 是否存在可切分的 auth-heavy 子區

## 現在可以放心先放下的事

- 把 `0x115` 當主角
- 回去做 UDS seed/key 主線
- 嘗試從整塊 `0x116 tail` 直接逆推出單一公式
