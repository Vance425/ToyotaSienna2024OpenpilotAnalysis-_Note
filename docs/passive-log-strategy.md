# 純被動 CAN Log 研究策略

## 為什麼改成純被動

目前已知情況是：

- 主動送 `seed` 到 Sienna 不會回應
- 因此目前拿不到標準 `UDS security access` 的 seed/response
- 所以現階段不能把主線放在主動 `seed -> key` 流程

這代表現在最合理的主線是：

`從被動 CAN log 反推哪些 frame 帶有 TSK / SecOC 痕跡`

## 現在的研究目標

不是直接拿到 `TSK`，而是先回答：

1. 哪些 frame 高度疑似帶有 `SecOC/auth/counter`
2. 哪些 frame 在狀態切換時出現可疑變化
3. 哪些 frame 在 `comma 3X` 嘗試失敗前後出現模式改變
4. 哪些 bus 最值得持續深挖

## 目前重點候選 ID

根據既有統計分析與 `v8.1` 結果，先把以下 frame 視為重點候選：

- `bus 0 / id 0x116`
- `bus 0 / id 0x115`
- `bus 0 / id 0x131`
- `bus 0 / id 0x260`

目前優先順序：

1. `0x116`
2. `0x115`
3. `0x131`
4. `0x260`

補充角色：

- `0x177`: 保留觀察
- `0xD8`: 速度 / 動態參考

## 為什麼它們值得優先看

### 0x116

- 高分
- repeated core 很高
- core 幾乎固定，但 tail 持續變化
- 很像 payload 穩定、auth/tag 變動的保護格式

### 0x115 / 0x131

- `v8.1` 將它們和 `0x116` 拉成同一群
- 在 toggle / entropy / priority focus 裡反覆出現
- 很值得當成相依 frame 群一起觀察

### 0x260

- 也有 auth/counter 味道
- 但 payload 本身變動大很多
- 比較像「一般訊號 + 保護欄位」，所以排在第三

## 純被動要看什麼

### 1. 狀態切換

優先比對：

- `IGN off -> IGN on`
- `IGN on -> Ready`
- 原廠 `ACC off -> on`
- 原廠 `ADAS off -> on`

### 2. comma 3X 失敗時序

優先比對：

- 接上前
- 接上後
- 開始嘗試抓取前
- 失敗出現當下
- 失敗後短時間內

### 3. 候選 frame 的 tail bytes

重點觀察：

- 是否出現 reset
- 是否出現停頓
- 是否出現 counter 跳變
- 是否出現 auth 區塊模式切換

### 4. bus 差異

目前已知：

- `bus 0` 和 `bus 2` 很像鏡像
- `bus 1` 分布顯著不同

因此：

- `bus 1` 要深挖
- `bus 0` 要持續追 `0x115 / 0x116 / 0x131 / 0x260`
- `bus 2` 主要做對照

## 現階段的成功定義

### 最小成功

知道哪一些 frame 最像受 `TSK / SecOC` 影響。

### 中等成功

知道這些 frame 在哪些狀態切換下會改變。

### 高成功

能把「候選 frame 的變化」和 `comma 3X` 的失敗時序建立關聯。
