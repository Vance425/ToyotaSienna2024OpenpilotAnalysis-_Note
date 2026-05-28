# 分析階段總結

## 這份文件在做什麼

把 `<LOCAL_TEMP>\20260312\分析階段內容` 裡的 `v9` 到 `v23`，整理成一條連續的研究線，而不是一堆分散版本。

## 整體脈絡

這些版本不是亂跑的，而是大致沿著下面這條路：

1. 先從大範圍被動 log 取出方向、速度、扭力、SecOC 候選
2. 再把 `0x115 / 0x116 / 0x131 / 0x260` 逐步拉成核心候選群
3. 再把正常訊號和可疑訊號分開
4. 最後開始形成 `steering reference / speed reference / candidate group` 的角色分類

## Phase 1: 初始掃描與候選海

### 版本

- `v9`
- `v10`
- `v11`
- `v12`

### 主要工作

- 建立 segment summary
- 從不同場景切出 `steering / speed / torque / counter / secoc / control`
- 產生初始 Toyota CAN map

### 這一階段的關鍵收穫

- 很早就把 `0x115 / 0x116 / 0x131 / 0x260` 拉進 focus 名單
- `0x115` 很早就被視為 counter / CRC / SecOC-like 強候選
- `0x260` 很早就被視為 control / LKAS / torque-like 強候選
- `0x131` 和 `0x116` 也持續站在前排
- 速度一開始偏向 `0xD8`

### 這一階段的限制

- 正常控制訊號和 security-like 訊號還混在一起
- steering / torque / control 很容易互相混淆
- 有些候選其實是 reference，不是 TSK 主角

## Phase 2: 候選群收斂

### 版本

- `v13`
- `v14`
- `v15`

### 主要工作

- 開始把輸出轉成更精煉的 JSON 摘要
- 進一步做 counter / CRC / LKAS / injection template 類型的結構化分析
- 看哪些 ID 在不同任務裡反覆浮現

### 這一階段的關鍵收穫

- `0x610`、`0x260`、`0x131` 開始在高分名單裡反覆出現
- `0x115` 持續是最強 counter-like / SecOC-like 候選之一
- `0x260` 在 LKAS / steering / control 路徑裡的重要性越來越高
- 工具開始把單一候選轉成「候選群」來看

### 這一階段的意義

這一步讓研究從「找單一神奇 ID」變成「看整個關聯群」。

## Phase 3: 統計、尺度與 counter/checksum 假設

### 版本

- `v16`
- `v17`
- `v18`

### 主要工作

- 加入 `top_ids`
- 加入 scale hints
- 加入 counter steps / checksum probe
- 開始做 focus timeseries

### 這一階段的關鍵收穫

- `0x610 / 0x260 / 0x131` 在 top IDs 裡穩定前排
- `0x115 / 0x116 / 0x260` 成為 counter-like 強候選
- simple checksum / xor 假設對 `0x115 / 0x116 / 0x131 / 0x260` 都不強

### 這一階段最重要的判讀

這很支持你現在的方向：

- 問題不像是簡單 checksum
- 更像高熵、counter/auth 類型結構
- 被動分析比硬猜傳統 checksum 更值得投資

## Phase 4: 安全版本的訊號對齊與相關性

### 版本

- `v19_safe`
- `v20`
- `v21`
- `v22`

### 主要工作

- 做 aligned timeseries
- 做 correlations
- 做 scatter / heatmap / envelope
- 把 signal 家族關係畫出來

### 這一階段的關鍵收穫

- 研究開始不只看單一 ID，而是看 signal family
- `steering_angle_like`
- `vehicle_speed_like`
- `driver_torque_like`
- `lkas_torque_like`
- `adas_state_like`

### 這一階段的意義

這一段幫你建立了非常重要的基礎：

- 哪些是正常車輛動態訊號
- 哪些是 LKAS / driver torque / ADAS state 相關
- 後面才有辦法把這些正常線和 security-like 候選分開

## Phase 5: 角色正式分流

### 版本

- `v8.1`
- `v23`

### 主要工作

- 進一步做人類可讀的 top candidates / decode map
- 把 steering / speed / torque discovery 分流
- 開始形成 reference 與 candidate 的角色分類

### 這一階段的關鍵收穫

#### v8.1

- `0x260` 高熵、切換敏感，持續很強
- `0x115 / 0x116 / 0x131` 成為一組值得一起看的候選群
- `0xD8` 看起來很像速度 / 動態訊號

#### v23

- `0x610` 幾乎可視為 steering reference
- `0xD5` 幾乎可視為 speed reference
- `0x260` 是跨表命中最多的核心候選
- `0x131` 仍然穩定前排

## 目前最成熟的整體判讀

### 參考線

- `0x610`: steering reference
- `0xD5`: speed reference

### 主要候選線

- `0x260`
- `0x116`
- `0x115`
- `0x131`

### 次級保留

- `0xD8`
- `0x177`

## 這條研究線最有價值的地方

它不是只給你一堆高分 ID，而是已經慢慢做出下面這種分層：

- 哪些像正常 steering / speed / torque feedback
- 哪些像 LKAS / state / control family
- 哪些像 counter / auth / SecOC 候選

這正是你現在做純被動 TSK 研究最需要的基礎。

## 我對整體品質的判斷

這組分析不是亂槍打鳥，而是有明顯迭代軌跡：

- 前期先廣撒網
- 中期做統計與候選收斂
- 後期開始做角色分流

所以你前面的功課是有累積價值的，而且現在已經能支撐下一步人工篩選。
