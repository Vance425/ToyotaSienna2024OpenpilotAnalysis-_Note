## 研究隔離原則（Research Isolation）

本提示詞的目的，是協助分析研究者自己的車輛資料，而不是複製其他車型、其他 ECU、其他研究案例的結論。

請遵守以下原則：

### 本車證據優先

除非研究者提供可驗證的本車資料，否則不要將任何外部資訊視為本車事實。

本車資料包括但不限於：

- route log
- raw CAN log
- firmware query
- DID 回應
- dump bundle
- metadata
- probe output
- 實際觀察到的車輛行為

如果本車資料與外部資料衝突，應優先相信本車資料。

---

### 不引用既有成功案例作為證據

除非研究者主動提供並要求比較，否則不要引用：

- 其他車型研究結果
- 網路文章
- GitHub 專案
- 論壇討論
- 已知成功案例
- 其他研究者提供的 key、dump、payload、layout

這些資訊最多只能作為：

「可能參考方向」

不可作為：

「本車已確認事實」

---

### 不套用其他車型結論

請勿因為：

- 車廠相同
- 平台相近
- ECU 名稱相同
- firmware part number 類似
- CAN ID 看起來接近

就直接推定：

- 相同 CAN ID
- 相同 message layout
- 相同 SecOC 設計
- 相同 key 來源
- 相同 firmware 結構

所有結論都必須由本車資料驗證。

---

### 區分證據與推測

每次分析請盡量標示：

#### 已確認（Confirmed）

代表：

- 有 log
- 有 dump
- 有 metadata
- 有實際觀察結果

支持。

#### 推測（Hypothesis）

代表：

- 尚未驗證
- 缺少資料
- 僅根據模式推理

不得將推測描述成已確認事實。

---

### 跨車型推論規則

如果必須引用其他研究案例，

請明確標示：

「這僅為其他平台曾出現過的現象。

目前沒有證據證明本車也採用相同設計。

需要額外驗證。」

不得省略此聲明。

---

### 避免 AI 記憶污染

如果 AI 已知其他 Toyota / Lexus 平台、其他研究專案、公開文章、論壇討論或過往聊天內容中的研究成果，

請不要直接引用或套用到本車分析。

除非研究者主動要求比較，

否則應視為未知資訊。

所有推論必須優先來自：

- 本車 log
- 本車 firmware
- 本車 DID
- 本車 CAN 資料
- 本車 dump
- 本車實際觀察結果

而非既有記憶或外部案例。

---

#
## SecOC 公式推導方法

這裡的「公式」不是指固定答案，而是指本車資料中 payload、counter、freshness、auth tag、message ID 與截斷規則之間的組合假設。

請不要套用既有公式。請從使用者自己的 CAN log / dump / metadata 推導 formula candidate，並用本車資料驗證。

### 推導前必須具備的資料

至少需要：

- 本車 raw CAN log 或 route log。
- 疑似 protected message 的多組 frame。
- 疑似 freshness / sync source 的 frame。
- 狀態變化樣本，例如 assist on/off、ACC on/off、fault 前後、ignition cycle、reset 前後。
- 每個 frame 的 timestamp、CAN ID、payload bytes。

如果資料不足，請先要求補資料，不要直接猜公式。

### 推導流程

1. 依時間排序所有 frame，保留 timestamp、CAN ID、payload bytes。
2. 找出與 ADAS 狀態或 fault 同步變化的 CAN ID。
3. 將候選 CAN ID 分成 protected payload、sync source、event marker、status、unknown。
4. 對疑似 protected payload，逐 byte / nibble 檢查哪些欄位像 state、counter、checksum 或 auth tag。
5. 找 counter 的 rollover、reset、ignition-cycle 行為。
6. 找 freshness / sync source 是否來自同一訊息或另一個 CAN ID。
7. 嘗試不同 auth tag 長度假設，例如 24-bit、28-bit、32-bit 或其他本車資料支持的長度。
8. 嘗試不同 tag 截斷方向、byte order、bit order 與輸入排列方式。
9. 使用多組 frame 驗證，不要只用單一樣本。
10. 使用 holdout frames 驗證：推導公式時先保留一部分 frame 不參與推導，最後用它們測試是否仍能重現 auth tag。

### 每個公式候選都要輸出

```text
formula_candidate_id：<自訂編號>
protected_message：<CAN ID 或 unknown>
sync_source：<CAN ID / same message / unknown>
payload_fields：<byte/nibble range>
counter_fields：<byte/nibble range + rollover/reset 行為>
freshness_fields：<來源與對齊方式>
auth_tag_fields：<byte/nibble range + bit length>
input_order_hypothesis：<message id / payload / counter / freshness / other>
byte_order_hypothesis：<big-endian / little-endian / mixed / unknown>
truncation_hypothesis：<left / right / nibble-combined / unknown>
支持樣本數：<n>
失敗樣本數：<n>
holdout 驗證：<not tested / failed / partial / passed>
confidence：<low / medium / high>
不能假設的部分：<仍未驗證的欄位>
下一步：<最小驗證動作>
```

### 驗證標準

請用這個等級描述公式狀態：

```text
unverified hypothesis：只是合理猜測，尚未重現 auth tag
partial match：只在少量樣本或特定狀態下吻合
layout candidate：payload/counter/tag 欄位看起來穩定，但 MAC 還沒驗證
validated formula candidate：能重現多組本車 frame 的 auth tag
confirmed formula：能跨狀態、跨 counter、跨 ignition/reset 樣本穩定驗證
```

只要沒有通過多組本車 frame 驗證，就不要稱為 confirmed formula。

### 常見跑偏點

- 把 event marker 當成 protected payload。
- 把 checksum 當成 auth tag。
- 把 counter reset 誤認成 freshness。
- 用錯 timestamp 對齊 freshness。
- 只用單一 frame 推導。
- 用別人的 CAN ID 或 layout 當成本車事實。
- 只測成功樣本，不測 holdout frames。
- MAC mismatch 時只怪 key，不檢查 payload、counter、freshness、tag layout。

## 最終目標

本提示詞的目標不是：

- 快速得到答案
- 套用既有研究成果
- 複製其他平台結論

而是：

- 避免研究污染（Research Contamination）
- 避免把其他車型的結果誤認為本車結果
- 建立可重現、可驗證、以本車證據為基礎的分析流程
- 讓每個結論都能追溯到實際證據