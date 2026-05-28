# Current Confidence

## 目前相對有把握的事

- `0x131` 是 boundary/state indicator
- `0x260` 是同家族的 family sync frame
- `0x116` 的前 2 bytes 是 phase 區
- `0x116` 的後 4 bytes 是高熵 tail

## 目前還不能直接說的事

- 還不能說 `0x116` tail 就是可直接解出的 auth tag
- 還不能說已經找到 TSK 取得方法
- 還不能說某一條 frame 就能單獨推回安全材料

## 但已經很有價值的進展

我們現在已經不是在亂找候選：

- 已經有穩定的事件模板
- 已經有明確的 byte focus
- 已經把 `phase / boundary / family sync / tail` 分工拆開

這些都會讓後面的 tail 細查比較有方向。

## 下一步最值得驗證的事

`0x116 tail` 是否會被：

- `0x116 phase`
- `0x131.b3`
- `0x260.b4`

這三者共同約束。
