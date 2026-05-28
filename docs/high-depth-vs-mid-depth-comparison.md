# High-Depth vs Mid-Depth Comparison

## 目的

比較：

- 高深度爬升樣本：`max_phase = 44 48`
- 中深度爬升樣本：`max_phase = 1e 1e`

看 `0x131 / 0x260` 的 family state 到底差在哪。

樣本：

- 高深度：[toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson) around `1773342250643`
- 中深度：[toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson) around `1773342062899`

## 中深度樣本 (`1e 1e`)

`0x116` phase：

- `00 05 -> 00 09 -> 00 0c -> 00 0e -> 00 10 -> 00 11 -> 01 12 -> 02 13 -> ... -> 12 18`

`0x131` family state：

- 後半軸大致從 `0069` 展到 `0093`

`0x260` family state：

- 後半軸大致從 `0069` 展到 `0098`

### 特徵

- family state 深展開
- 但仍在單一正向上升族群中

## 高深度樣本 (`44 48`)

`0x116` phase：

- `04 0b -> 10 1e -> 20 31 -> 2a 3a -> 43 48 -> 44 46`
- 然後回落到 `42 40 -> 3e 3c -> 3c 3a -> 3b 3b -> 3a 3a -> 38 35 -> 36 34 -> 35 33 -> 34 33`

`0x131` family state：

- 一開始維持在 `fff4` 基底群
- 後續逐步轉到 `fff0 / ffeb / ffe7 / ffe3 / ffde / ffd2 / ffbd / ffb5` 這種連續下降族群

`0x260` family state：

- 一開始也維持在 `fff4` 基底群
- 後續同步轉到 `fff2 / fff0 / ffee / ffeb / ffe8 / ffe6 / ffe3 / ffde / ffd9 / ffbd / ffb6`

### 特徵

- 不是單純更高的 phase 而已
- 而是進到一個完全不同的 family state 基底群
- 這組 family state 整體是沿著 `fff4 -> ffb5` 這類下降軸在跑

## 最重要的差異

### 中深度樣本

- family state 基底群是正向上升：
  - `0069 -> 0098`

### 高深度樣本

- family state 基底群是高位負向下降：
  - `fff4 -> ffb5`

## 這代表什麼

高深度爬升和中深度爬升，不只是 phase 深度不同，而是：

- family state 所在的區域不同

這點很重要，因為它代表：

- 某些高深度爬升可能不是一般 driving phase 的延長版
- 而是 family 已經切進另一種狀態區

## 目前最重要的工作假設

### 假設 A

`0x116` 的 phase 深度必須和 `0x131 / 0x260` 的 family state 區域一起看。

### 假設 B

高深度樣本若落在和一般 driving 不同的 family state 區域，才值得優先當「接近 security gate」候選。

### 假設 C

`44 48` 這段比 `1e 1e` 更接近高價值事件帶，因為它不只是爬得高，而是整個 state family 都切到不同區域。

## 下一步

最值得做的是：

1. 在 `190101` 裡批次找所有落在 `fffx` 降階 family 區域的深爬升
2. 看它們是否總是伴隨 `35+` 或 `44+` 的高 phase
3. 如果是，就把這組 family 區域列成高優先級 security-like 候選
