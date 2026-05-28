# v23 分析結果整合

## 來源

- $label (local-only source path)
- $label (local-only source path)
- $label (local-only source path)
- $label (local-only source path)
- $label (local-only source path)
- $label (local-only source path)

## 一句話結論

`v23` 把參考訊號和候選訊號切得更清楚：

- `0x610` 很像 steering reference
- `0xD5` 很像 speed reference
- `0x260` 仍然是跨表最常出現的核心候選
- `0x131` 仍然在前排
- `0xD8` 相比 `v8.1` 下降成次級速度候選

## 這批結果最重要的意義

### 1. 0x610 應視為 steering reference

`v23_report.json` 直接指出：

- `steering_ref = 0x610 u16be_b5_6 centered by 32768`

而且它在 steering / torque discovery 都幾乎滿分相關。

### 2. 0xD5 應視為 speed reference

`v23_report.json` 指出：

- `speed_ref = 0xD5 u16be_b1_2 raw`

這代表後續做人工篩選時，應該優先用 `0xD5` 當速度對照，而不是只看 `0xD8`。

### 3. 0x260 的核心地位更穩

`v23_top_ids.json` 顯示：

- `0x260 hits=34`

它是跨 discovery tables 命中最多的 ID，代表它不是單一場景偶然浮出來，而是穩定的重要候選。

### 4. 0x131 持續站在前排

`0x131` 在 steering / torque / speed discovery 都持續出現，值得維持高優先。

## 更新後的角色分類

### Group A: 主要被動候選

- `0x260`
- `0x116`
- `0x115`
- `0x131`

### Group B: 參考訊號

- `0x610`: steering reference
- `0xD5`: speed reference

### Group C: 次級參考 / 次級候選

- `0xD8`
- `0x177`

## 目前最合理的優先順序

1. `0x260`
2. `0x116`
3. `0x115`
4. `0x131`
5. `0x610` 作 steering reference
6. `0xD5` 作 speed reference
7. `0xD8`
8. `0x177`

## 對你現在最實際的意思

後續人工篩選不要再把所有高分 ID 混成同一類。比較合理的做法是：

- 候選線：`0x260 / 0x116 / 0x115 / 0x131`
- 參考線：`0x610 / 0xD5`

這樣才不會把正常 steering / speed feedback 誤判成 security 主候選。
