# `0x116 / 0x131` 對照: `184921` vs `185451`

## 目的

把目前最重要的兩段窗口並排，確認：

- `0x116` 的前段 bytes 到底是不是 phase 結構
- `0x131` 的 prefix 到底是不是 reset/state 邊界

比較對象：

- [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)
- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)

## `0x116` 比較

### `184921`

窗口內序列：

- `24000000...`
- `25000000...`
- `26000000...`
- `27000000...`
- `28000000...`
- `29000000...`

觀察：

- 第 1 byte 呈現非常乾淨的單步遞進
- 第 2-4 byte 固定為 `000000`
- 後 4 bytes 高熵持續變化

判讀：

這像是「phase byte + auth tail」的乾淨樣本。

### `185451`

窗口內序列：

- `09090000...`
- `090a0000...`
- `0a0c0000...`
- `0d0e0000...`

觀察：

- 這次不是只有第 1 byte 變
- 第 1-2 byte 一起形成 phase pair
- 第 3-4 byte 仍固定為 `0000`
- 後 4 bytes 同樣維持高熵變動

判讀：

這比 `184921` 更像多階段 phase 結構，不只是單 byte counter。

### `0x116` 合併結論

`0x116` 最穩的結構是：

- 前 2 bytes: phase / state 候選
- 第 3-4 bytes: 常數區
- 後 4 bytes: auth-like tail 候選

也就是說，目前最值得追的不是整個 `0x116` payload，而是：

- `byte0`
- `byte1`
- `byte4-7`

## `0x131` 比較

### `184921`

窗口內 prefix 變化：

- `0037003e`
- `0038003e`
- `003b003d`
- `003d003d`
- `003e003d`
- `0000003d`
- `0003003d`
- `0004003e`
- `0006003e`
- `0007003e`
- `0009003f`
- `000a003f`
- `000c003f`
- `000d0040`
- `000f0041`

觀察：

- 前 2 bytes 在事件中途發生明顯 reset
- 後 2 bytes 沒有一起歸零，而是持續在 `003d -> 003e -> 003f -> 0040 -> 0041`

判讀：

這很像兩組 state 同時存在：

- 前半組像 local phase/reset
- 後半組像較慢的狀態軸

### `185451`

窗口內 prefix 變化：

- `003cf9d3`
- `003ef9c7`
- `003ff9bc`
- `0001f9a8`
- `0004f99a`
- `0005f995`
- `0007f991`
- `0008f990`
- `000af98d`
- `000bf98d`
- `000df98d`
- `000ef98d`
- `0010f98b`
- `0011f98b`
- `0013f98a`

觀察：

- 這裡也是前 2 bytes reset，再往上遞進
- 但後 2 bytes 不像 `184921` 那樣正向累進
- 後 2 bytes 比較像另一個 slowly drifting state base：`f9d3 -> f9c7 -> f9bc -> f9a8 -> ... -> f98a`

判讀：

`0x131` 的前 2 bytes 很可能才是 reset/state 邊界主體，後 2 bytes 比較像背景狀態或 session base。

### `0x131` 合併結論

`0x131` 最該看的，是前 2 bytes 的 reset pattern：

- `003x -> 000x`

這個模式在兩段窗口都出現了，只是後 2 bytes 的背景軸不同。

## 目前最有價值的工作假設

### 假設 A: `0x116` 是 protected phase frame

理由：

- 兩段窗口都呈現穩定 phase 區 + 高熵 tail 區
- `184921` 比較像簡化版
- `185451` 比較像多 byte phase 版

### 假設 B: `0x131` 是 state-boundary indicator

理由：

- 兩段窗口都出現 `003x -> 000x` reset 風格
- reset 發生時，`0x116` 會同步進入新 phase

### 假設 C: `0x116 + 0x131` 應一起看，不應拆開看

理由：

- `0x131` 給你邊界
- `0x116` 給你 phase
- 兩者一起，才像一個完整事件模板

## 接下來要看什麼

下一輪最值得看的是：

1. `0x116` 的 `byte0-byte1` 是否在其他窗口也會形成 phase pair
2. `0x131` 的前 2 bytes reset 是否總是和 `0x116` phase change 同步
3. `0x260` 是否總是陪同這組 `0x116 + 0x131` 模板切換

如果之後要把工作再收斂，主線應該就是：

- `0x116`: phase
- `0x131`: boundary
- `0x260`: family sync
