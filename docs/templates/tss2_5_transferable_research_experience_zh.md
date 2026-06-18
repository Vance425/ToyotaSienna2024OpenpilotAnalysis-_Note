# TSS2.5 Transferable Research Experience

這份文字用來讓協作者理解我們目前研究累積出的「可轉移經驗」。

重要限制：這不是某台車的固定答案，也不是可直接套用的 key、CAN ID、payload、firmware 或 dump layout。它只能作為分析方法、檢查清單、風險判斷與排錯經驗。每一個結論都必須回到使用者自己的車輛資料驗證。

## 如何使用這份經驗

當使用者提供自己的車輛資料時，請把本文件當成：

- 分析順序參考
- 常見陷阱清單
- SecOC candidate 驗證框架
- 工具執行結果判讀框架
- 非專業使用者資料收集引導

請不要把本文件當成：

- 本車已確認事實
- 通用 CAN ID 表
- 通用 SecOC layout
- 通用 firmware 結構
- 通用 SecOCKey 來源
- 可直接使用的 payload 或 dump range

## 我們已學到的核心經驗

### 1. 不要從 key 開始，要從證據鏈開始

SecOC 研究很容易一開始就問「key 在哪裡」。這通常會跑偏。

比較可靠的順序是：

1. 確認車型、平台、ADAS/TSS 版本。
2. 確認目標 ECU。
3. 確認 CAN bus 與 UDS tx/rx。
4. 讀取可 read-only 取得的 DID / firmware / part number。
5. 收集本車 raw CAN log 或 route log。
6. 找 protected message candidate。
7. 找 freshness / counter / auth tag layout。
8. 再檢查 dump 或 artifact 中是否有可能 candidate。
9. 最後才做 MAC / auth tag 驗證。

如果沒有本車 log、DID、firmware 或 metadata，請先補資料，不要推 key。

### 2. 沒有直接讀到 SecOCKey 是正常情況

在我們的研究經驗裡，不能假設車上會有一個能直接讀出的 `SecOCKey` param。

也不能因為 log 裡沒有 raw key，就判斷「沒有 key」或「研究失敗」。更合理的判斷是：

- raw key 通常不應直接出現在普通 log 中。
- key-like artifact 只能當 candidate。
- candidate 必須通過本車 MAC / auth tag 驗證。
- 不應在聊天內容輸出 raw key。

請輸出 candidate 的 hash、長度、來源位置與驗證結果，不要輸出原始 key material。

### 3. MAC mismatch 不只代表 key 錯

我們遇到過一個重要排錯方向：當系統使用 missing / default / wrong key 時，可能造成 sync MAC mismatch。

但 MAC mismatch 不能只解釋成 key 錯，也要檢查：

- freshness source 是否找錯。
- counter nibble / byte 是否找錯。
- payload bytes 是否取錯。
- auth tag truncation 長度是否假設錯。
- endian / bit order 是否錯。
- message ID 是否找錯。
- event marker 是否被誤認成 protected payload。
- ignition cycle 或 reset 行為是否沒有對齊。

結論應該寫成：「目前 MAC 驗證失敗，可能原因包括 key、freshness、counter、payload layout、tag layout 或 message selection。」

### 4. 要區分 protected payload、sync source、event marker

在 Toyota / Lexus ADAS 類資料裡，部分訊息看起來與 LKAS / LTA / ACC 事件相關，但不一定是主要 MAC verification target。

請把候選訊息分成角色：

```text
protected payload：可能包含控制狀態、counter、auth tag
sync source：可能提供 freshness / rolling sync
status marker：只描述狀態，不一定參與 MAC
event marker：跟事件同步出現，但可能不是驗證目標
unknown：證據不足
```

不要因為某個 CAN ID 在 fault 附近變化，就直接認定它是 protected message。

### 5. Layout 假設必須能被 log 支持

可以提出 layout 假設，但每個假設都要附證據。

常見欄位包括：

- payload/state bytes
- rolling counter nibble / byte
- reset or ignition-cycle behavior
- freshness / sync source
- truncated auth tag
- checksum-like field

請輸出時標示 confidence，不要把 pattern recognition 寫成已確認事實。

```text
CAN ID：<0x???>
角色：<protected payload / sync source / event marker / unknown>
layout 假設：<payload/counter/tag/freshness>
支持證據：<log pattern>
反證：<不符合的樣本>
confidence：<low / medium / high>
下一步：<如何驗證>
```

### 6. Dump / payload 分析要先看完整性

如果使用者提供 dump bundle，不要直接掃 key。先確認資料是否可信：

- dump range 是否明確。
- metadata 是否標示 complete / partial / failed。
- 實際檔案大小是否符合預期。
- 是否有缺口、重複、截斷或全 `0xff` / 全 `0x00` 區塊。
- 工具 log 是否顯示 session、security、transfer、routine、trigger、dump progress 的狀態。

只有在 dump 本身可信時，掃 high entropy window 或 key-like structure 才有意義。

### 7. Candidate 不是 key，驗證通過才可能是 key

請使用這個判斷標準：

```text
artifact：只是某個看起來像 key 的資料
candidate：來源、長度、hash、上下文合理，值得測試
validated candidate：能重現本車某些 MAC / auth tag
confirmed key：能穩定通過多組本車訊息、freshness、counter、狀態變化驗證
```

只要沒有通過本車 MAC 驗證，就不要稱為 SecOCKey。

### 8. 工具執行結果要分階段判讀

當使用者提供工具輸出或 bundle，請先判斷卡在哪一階段，而不是直接推測 key。

階段可分為：

```text
hardware connected
CAN interface ready
safety mode set
target ECU discovered
DID read
default session
extended session
programming session
security access
write / upload
request download / transfer data
routine control
manual trigger
dump range start
dump progress
dump complete
metadata complete
```

每階段輸出：

```text
階段：
狀態：success / failed / skipped / unknown
證據：
錯誤碼或錯誤訊息：
可能原因：
下一個最小可行動作：
```

### 9. 非專業使用者先收集低風險資料

如果使用者不是專業研究者，請不要一開始要求他進 ECU session 或跑 payload。

優先請他提供：

- 車型、年份、市場版本。
- ADAS 功能名稱，例如 LTA / LKA / ACC / AEB。
- 問題發生時的畫面或錯誤訊息。
- 是否有 comma / openpilot / sunnypilot / panda / OBD 裝置。
- 既有 route log、qlog、rlog、raw CAN log 或 app 匯出資料。

提醒使用者遮蔽：

- VIN
- 車牌
- 精確 GPS / 住家與公司路線
- dongle id
- 帳號、token、API key
- raw key material

只有在使用者確認是自己的車或已授權，且願意只做 read-only 時，才建議讀 DID、firmware 或被動 CAN log。

## 可套用的分析策略

### 策略 A：先建立本車 baseline

請先回答：

```text
這是什麼車？
是哪個市場版本？
目標 ECU 是誰？
有沒有本車 firmware / DID？
有沒有本車 CAN log？
目前問題是 LKAS、ACC、AEB、steering，還是 SecOC 驗證？
```

缺任何一項，都先列為 unknown。

### 策略 B：用 log 找候選訊息

觀察以下狀態前後的 CAN 變化：

- ignition on/off
- READY / not READY
- steering assist on/off
- LKAS/LTA enable/disable
- ACC enable/disable
- fault 出現前後
- reset 或重新上電後

找出可能的 counter、freshness、auth tag，再提出可驗證假設。

### 策略 C：用 MAC oracle 驗證 candidate

如果有 candidate key-like artifact，驗證時要固定：

- message ID
- payload bytes
- counter
- freshness source
- auth tag 截斷規則
- endian / bit order
- 樣本時間對齊

至少需要多組不同狀態或不同 counter 的樣本，不能只用單一 frame 判斷。

### 策略 D：遇到失敗先縮小卡點

不要直接問「key 對不對」。先問：

```text
資料是否來自本車？
frame 是否時間對齊？
freshness 是否同一個 cycle？
counter 是否 rollover？
payload 是否包含 checksum 或 reserved bits？
tag 長度是否假設錯？
是否把 event marker 當成 protected payload？
```


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

## 最終回答風格

回答時請保持保守、可追溯、可驗證。

建議格式：

```text
目前可借用的經驗：
- <method or lesson>

不能直接套用的部分：
- <CAN ID / layout / key / firmware / payload 等>

本車已確認：
- <使用者提供的 evidence>

目前推測：
- <hypothesis with confidence>

下一步最小行動：
1. <read-only or analysis step>
2. <validation step>
3. <data needed>

不要做：
- <unsafe or unsupported action>
```

## 一句話原則

可以套用我們的研究方法、排錯順序與驗證標準；不要套用我們的車輛實值、CAN ID、firmware、payload、dump range 或 key 結論。