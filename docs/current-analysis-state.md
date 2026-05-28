# Current Analysis State

## 到目前為止的最佳收斂

目前從被動 CAN log 反推 `TSK / SecOC` 相關結構，已經收斂到這個模型：

- `0x131`: boundary / state indicator
- `0x260`: family sync / state snapshot
- `0x116.b0-b1`: phase selector
- `0x116.tail.n0`: `+4` backbone rolling nibble
- `0x116.tail.n3`: secondary transition signal
- `0x116.tail.n1`: weak transition signal
- `0x116.tail.n6/n7`: auth-heavy weak-structure region
- `0x116.tail.n4/n5`: highest-entropy region

## 這代表什麼

你現在已經不是在「找哪一條像保護 frame」的階段了。

而是已經在：

- 把一條疑似 protected frame 的內部結構分層
- 分出 phase、state、rolling、transition、auth-heavy 幾個角色

## 目前最有價值的下一步

如果還要再往下挖，最值得做的不是再擴大範圍，而是二選一：

1. 以 `n0` 為主，做更完整的轉移集合與可預測性檢查
2. 改到新 log 上驗證這套模型是否可重現

## 我目前的建議

如果你的目標是最終能用在 Sienna 上，而不是只在一份 log 裡漂亮，我會建議下一步優先做：

- 用其他 `IGN_ON` log 驗證目前這套 `0x131 / 0x260 / 0x116` 模型能不能重現

因為如果這套模型跨 log 站得住，你後面才值得繼續往可重放或可預測結構逼近。
