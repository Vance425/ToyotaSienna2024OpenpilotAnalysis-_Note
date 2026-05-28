# `n0` Start vs State Base

## 目標

確認每次 `0x116 phase` 切換時，tail 的第一個 nibble (`n0`) 起始值是否能被 `0x131.b3 / 0x260.b4` 約束。

## `184921`

檔案：

- [toyota_seg_IGN_ON_20260311_184921_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_184921_000.ndjson)

### phase 起始點

| phase | `n0_start` | `0x131.b3` | `0x260.b4` |
| --- | --- | --- | --- |
| `24 00` | `1` | `3e` | `3e` |
| `25 00` | `9` | `3e` | `3d` |
| `26 00` | `a` | `3d` | `3d` |
| `27 00` | `2` | `3d` | `3d` |
| `28 00` | `2` | `3f` | `3f` |
| `29 00` | `e` | `40` | `41` |

### 判讀

- `n0_start` 不是固定值
- 同樣的 state base 也可能對應不同起始值
  - 例如 `3d / 3d` 對應過 `a` 和 `2`
- 但 phase 切到新段時，`n0_start` 會一起重定相

結論：

`184921` 支持「`n0` 會在 phase 切換時換起點」，但不支持「只靠 `b131/b260` 就能直接算出起點」。

## `185451`

檔案：

- [toyota_seg_IGN_ON_20260311_185451_000.ndjson](/D:/Codex/toyota-sienna-tsk-analysis/analysis-input/raw_can_logs/toyota_seg_IGN_ON_20260311_185451_000.ndjson)

### phase 起始點

| phase | `n0_start` | `0x131.b3` | `0x260.b4` |
| --- | --- | --- | --- |
| `09 09` | `1` | `d3` |  |
| `09 0a` | `5` | `c7` | `bc` |
| `0a 0c` | `e` | `91` | `90` |
| `0d 0e` | `6` | `8d` | `90` |

### 判讀

- `n0_start` 隨 phase 段切換
- `0a 0c` 和 `0d 0e` 的 `0x260.b4` 都接近 `90`
- 但 `n0_start` 卻是 `e` 和 `6`

結論：

這再次說明 `n0_start` 不是 `0x131.b3 / 0x260.b4` 的簡單一對一映射。

## 合併結論

目前比較合理的說法是：

- `n0_start` 會被 phase / state 邊界共同影響
- 但它不是 `state base` 的直接函數
- 更像某種「phase-aware re-seeding」結果

## 最新工作假設

### 假設 A

`n0` 是 rolling nibble。

### 假設 B

phase 切換時，`n0` 會重定相。

### 假設 C

重定相與 `0x131 / 0x260` 的 state base 有關，但不只由它們決定。

## 這對整體任務的意義

這個結果很重要，因為它把分析方向再縮小了一步：

- 不要試圖用 `b131/b260` 直接反推出 `n0_start`
- 反而要把 `n0` 當成「被 boundary 觸發、在新 phase 重新起跑的 rolling 候選」

## 下一步

下一輪最值得做的是：

1. 看 `n0` 在 phase 切換後的前兩三步是否比較穩
2. 確認 `n0` 的 `+4` 規律是不是主要出現在 phase 內穩定段
3. 把 phase 內穩定段和 phase 邊界段分開看
