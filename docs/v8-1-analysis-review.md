# v8.1 分析結果整合

## 來源

- $label (local-only source path)
- $label (local-only source path)
- $label (local-only source path)

## 一句話結論

這份 `v8.1` 分析很有幫助，因為它把候選 frame 開始分出角色：

- `0xD8` 比較像速度 / 車輛運動訊號
- `0x260` 很像高熵切換 frame，仍然值得觀察
- `0x115 / 0x116 / 0x131` 變成一組很值得優先追的候選群

## 我對結果的判讀

### 1. 0xD8 更像速度，不像 TSK 主角

`v8.1` 裡：

- `Top Drive-only Speed Detector` 幾乎被 `0xD8` 包辦
- `Speed Validation Top Rows` 也由 `0xD8` 主導
- `focus_bitflip` 也顯示 `0xD8` 某些 bit flip 很高

這代表：

- `0xD8` 非常可能是高價值的車速 / 運動相關 frame
- 但它更像 vehicle state input，不像 `TSK` 本體

所以：

- `0xD8` 要保留
- 但不要把它排成 `TSK` 第一優先

### 2. 0x260 仍然值得留在前排

`v8.1` 顯示：

- `Top Parked Toggle / High-Entropy Detector` 由 `0x260` 領先
- `Priority IDs Focus` 也把 `0x260` 擺在最前面
- `Top Rewritten Steering Detector` 也把 `0x260` 拉出來

這代表：

- `0x260` 對車輛狀態或控制切換非常敏感
- 它可能不是純 `TSK` frame
- 但很可能跟被保護的控制或狀態同步有關

### 3. 0x115 / 0x116 / 0x131 是這次最大的收穫

這組 ID 在 `toggle / entropy / bitflip / priority focus` 裡都持續出現。

尤其：

- `0x116` 之前在你自己的 `secoc_cracker_v5` 也已經很強
- `0x115` 與 `0x131` 現在補上來，形成一個相鄰群

這種結果很值得注意，因為：

- 它們可能屬於同一個功能群
- 可能是同一個控制域的多個相依 frame
- 其中一個不一定是 `TSK` 主 frame，但整組值得一起觀察

## 更新後的角色分類

### Group A: 高優先 SecOC 候選

- `0x116`
- `0x115`
- `0x131`

### Group B: 高熵 / 切換敏感候選

- `0x260`

### Group C: 車速 / 動態狀態參考

- `0xD8`

## 對研究方向的意義

這份 `v8.1` 幫我們做了兩件事：

1. 把 `0xD8` 從 `TSK` 主候選名單裡降成「參考訊號」
2. 把 `0x115 / 0x116 / 0x131` 明確升級成要一起追的候選群

## 目前最合理的優先順序

1. `0x116`
2. `0x115`
3. `0x131`
4. `0x260`
5. `0xD8` 作為速度 / 運動參考

## 下一步怎麼用這份結果

第二輪被動分析時，優先看：

- `0x115 / 0x116 / 0x131` 在狀態切換時的 tail bytes
- `0x260` 在 `comma 3X` 失敗前後是否出現模式改變
- `0xD8` 當作車輛真的有在動 / 有在切換狀態的對照訊號
