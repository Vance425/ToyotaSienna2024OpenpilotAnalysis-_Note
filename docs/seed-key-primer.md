# Seed / Key / TSK / SecOC 入門

## 這份文件是給誰的

給現在正在研究 `2024 Toyota Sienna + comma 3X`，但對 `seed/key`、`TSK`、`SecOC` 還不熟的人。

## 先講最短版本

### 傳統 seed/key 是什麼

它是一種車用 ECU 的解鎖流程：

1. 你先對 ECU 要一個 `seed`
2. ECU 回你一段資料
3. 你用某個演算法把 `seed` 算成 `key`
4. 你把 `key` 回送給 ECU
5. ECU 驗證通過後，才允許更高權限操作

## 在你這個案子裡，為什麼這件事重要

因為你現在遇到的情況是：

- `comma 3X` 想在車上正常工作
- 但 Toyota 新平台有 security 機制
- 目前車端沒有可用的 `TSK`
- `comma 3X` 也無法自動成功抓到它

所以你會自然想到：

「是不是要先拿到 seed，再算 key？」

## 但你現在的現況不是標準 seed/key 成功路線

你目前已經觀察到：

- 主動送 `seed` request，Sienna 不回
- `uds_events` 幾乎都是 timeout

這代表什麼：

- 你現在不是卡在「拿到 seed 但不會算 key」
- 你是更前面就卡在「根本沒有走通標準 UDS seed/key 路徑」

## TSK 是什麼

在你現在的討論脈絡裡，`TSK` 可以先理解成：

- Toyota Security Key
- 或更廣義地說，讓車上保護訊號能被接受所需的 security material

它不一定等同於傳統 UDS 那種單次 `seed -> key` 解鎖結果。

## SecOC 是什麼

`SecOC` 可以先把它理解成：

- 訊息保護 / 驗證機制
- 某些 CAN frame 不是只看 payload 內容
- 還會帶 counter、auth tag、MAC 或其他驗證欄位

簡單講：

- 就算你知道「控制值」要送什麼
- 如果沒有正確的保護欄位
- 車也可能不接受

## 這和 seed/key 的差別

### 傳統 UDS seed/key

- 比較像「進入高權限診斷模式」的門禁
- 典型形式是 request / response

### SecOC / TSK 問題

- 比較像「平常在跑的控制 frame 本身也被保護」
- 你需要的不只是開門
- 還需要讓每一筆訊息都長得像合法訊息

## 為什麼你現在只能先被動反推

因為你目前已經知道：

- Sienna 不回應你的 seed request
- 所以你拿不到標準 UDS 的 seed

這種情況下，比較合理的研究方法是：

1. 先被動錄 CAN log
2. 找出哪些 frame 很像有 counter / auth / SecOC
3. 比對狀態切換與 `comma 3X` 失敗前後
4. 反推出哪些訊號最可能受 `TSK` 影響

## 你現在最需要懂的，不是數學公式

而是先分清楚兩條路：

### 路線 A: 標準 UDS seed/key

如果車會回 seed，才值得往這條走。

### 路線 B: 被動反推 SecOC / TSK

如果車根本不回 seed，這條才是主線。

你目前比較像是走路線 B。

## 目前套用到你車上的實際理解

### 0x610

- 比較像 steering reference

### 0xD5

- 比較像 speed reference

### 0x260 / 0x116 / 0x115 / 0x131

- 比較像你現在要持續追的候選群
- 它們可能和受保護的控制 / 狀態 / auth 結構有關

## 我之後會怎麼協助你

我會把後續分析都盡量用這種方式講：

- 哪個是 reference
- 哪個是候選
- 哪個像 control
- 哪個像 auth / counter

而不是直接丟一堆縮寫給你。

## 你現在可以用一句話記住

你目前的問題，不像是「已經拿到 seed 但不會算 key」；
比較像是「標準 seed/key 路不通，所以要從被動 CAN log 反推受 TSK/SecOC 保護的訊號結構」。
