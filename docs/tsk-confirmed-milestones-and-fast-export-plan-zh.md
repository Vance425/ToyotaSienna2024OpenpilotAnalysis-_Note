# TSK 已確認後：里程碑與快速導出計畫

## 目的

這份文件以一個新前提來整理專案：

- **TSK 已經確認**

在這個前提下，我們不再把主重心放在：

- `TSK` 是否存在
- 哪條 passive backbone 最可信

而是改成更執行導向的兩個問題：

1. 我們已經走到哪些里程碑
2. 接下來怎麼用**最短路徑**把可用材料快速導出

## 一、已完成里程碑

### 1. Passive backbone 已定型

目前最穩的被動主線已經固定：

- `0x116`
- `0x131`
- `0x2E4`

這條線已經足夠支撐：

- lifecycle 判讀
- bridge-tier 比較
- route-level high-value window 篩選

### 2. Top-tier anchor 已固定

目前最強 anchor 仍然是：

- [toyota_seg_IGN_ON_20260312_190101_000.ndjson](../logs/toyota_seg_IGN_ON_20260312_190101_000.ndjson)

它仍然是：

- top-tier joined lifecycle
- 所有 `Grade A` 判斷的基準樣本

### 3. Bridge ladder 已建立

目前 bridge ladder 已經明確：

1. `185520`
2. `173834`
3. `184921`
4. `171414`
5. `190101`

而 `20260509 Session 3` 已經把中間地帶往前推成：

- **route-level bridge-tier candidate**

也就是：

- 高於 `171414`
- 低於 `190101`

### 4. Control-side anchor 已固定

目前最穩的 control-side anchor 是：

- `0x260`

而且 replay-backed 主分支已經收斂成：

- `decode_mode = no_b1_flip`
- `mode = identity`
- `higher slew`

### 5. 城市 transition/settle 規則已收斂

city-side local working rule 目前已經有可用形態：

- `low-band catch-up 5.5x`
- `deeper-negative helper 2.5x`
- 只在 `transition / settle` 子相位啟用

### 6. Direct branch 的真正卡點已定位

舊 `extract_keys` 分支現在最可信的結論不是：

- 車上沒有 key

而是：

- 舊 dump range / layout / parser
- **不再適合 `2024 Sienna`**

也就是：

- session / unlock / payload path 可能還能走很深
- 但最後讀回來的區域與舊結構假設不匹配

### 7. LKAS / SecOC 故障上下文已補強

目前已經有：

- fingerprint + `LKAS Context`
- `LKAS Failed`
- `SecOC synchronization / key-state`

這條異常樣本線可以幫助未來 active export 時快速判斷：

- 是 control-side 問題
- 還是 secure/auth-side 問題

## 二、現在的專案狀態

如果以「TSK 已確認」為前提，現在最準確的狀態是：

- **TSK 問題本身已不是主阻塞**
- **主阻塞改成怎麼更快導出可用 secure/auth 材料**

更白話一點：

- 我們現在不是在問：
  - `TSK` 是不是這條
- 而是在問：
  - 怎麼最快把 `TSK / SecOC` 相關材料導出成可重用成果

## 三、未來快速導出的目標

接下來的「導出」，建議分成三層，不要混在一起。

### A. 最小可用導出

目標：

- 先把 **raw dump / transcript / metadata** 穩定導出

這一層不要求：

- 立刻得到正確 key
- 立刻寫回 openpilot

只要求：

- 能穩定重現
- 能穩定保存
- 能穩定比較不同 firmware / 不同 dump range

### B. 結構導出

目標：

- 從 dump 中定位：
  - key-like structure
  - candidate offsets
  - checksum hypothesis
  - layout hypothesis

這一層的產物是：

- 結構假說
- candidate keys
- layout map

### C. 可操作導出

目標：

- 把 candidate 變成：
  - 可寫入
  - 可驗證
  - 可被 secure/auth path 接受

這一層才會碰：

- `SecOCKey`
- synchronization
- freshness
- MAC validity

## 四、最快的導出路徑

如果目標是**最快**，建議不要先追「直接吐出 key」。

最快路徑應該是：

### 第一步：先做 dump-only 導出

先把 direct branch 收成穩定的 dump 採集器。

最小輸出應該固定成：

```text
out/secoc_dump_YYYYMMDD_HHMMSS/
  transcript.jsonl
  metadata.json
  dump_xxxxx.bin
  dump_summary.txt
```

這一步的核心不是「解密」，而是：

- 每次都能留下可重播、可比較的原始證據

### 第二步：再做 parser / candidate 導出

在 dump-only 穩定後，再做 parser。

建議輸出：

```text
candidate_report.md
candidate_keys.csv
layout_hypotheses.json
```

這樣就能把問題從：

- 「為什麼是 0000」

變成：

- 「哪一段像新 key table」
- 「哪個 offset 最可疑」
- 「哪種 checksum / struct size 最像」

### 第三步：最後才做 write-back / validation

只在前兩步穩了之後，才進入：

- `SecOCKey` candidate write-back
- synchronization validation
- active acceptance check

這樣會比一開始就直接追：

- 「能不能一次吐出正確 key」

快很多，也穩很多。

## 五、建議的最短執行順序

### 路徑 1：最快、風險最低

1. 固化 `dump-only` 腳本
2. 固化 metadata / transcript 保存格式
3. 多次對同車、同 firmware 重複 dump
4. 比較 dump 穩定區與變動區
5. 再做 parser

適合目的：

- 快速建立可比較資產
- 快速縮小 key layout 搜尋範圍

### 路徑 2：最快逼近 key

1. dump-only 穩定
2. 直接做 candidate parser
3. 試多個 layout hypothesis
4. 找出最像 `KEY_4 / SecOC key` 的區段

適合目的：

- 盡快逼近 candidate key

代價：

- 較容易把 parser 假說寫太滿

### 路徑 3：最快逼近 openpilot 可用材料

1. dump-only
2. parser
3. candidate write-back
4. `SecOC synchronization` 驗證
5. acceptance check

適合目的：

- 最快朝 implementation 前進

代價：

- 風險最高
- 最容易把 secure/auth 問題和 parser 問題纏在一起

## 六、我建議的實際走法

如果要兼顧速度和穩定，我建議：

### 現在先走：

- **路徑 1 + 路徑 2 的前半**

也就是：

1. 先穩定 `dump-only`
2. 再穩定 `candidate parser`
3. 先不要急著 write-back

原因很簡單：

- 你現在最大的已知風險不是 `TSK` 本身
- 而是：
  - dump range
  - memory layout
  - parser assumptions

只要這三個沒穩，
直接衝 write-back 很容易浪費時間。

## 七、導出成功的判定標準

### 最小成功

- dump 能穩定導出
- transcript 能穩定保存
- metadata 完整

### 中等成功

- parser 能產出穩定 candidate
- 不同 dump 之間能找到重複的 key-like 結構

### 高成功

- candidate 能通過 write-back / sync 驗證
- secure/auth path 不再報：
  - missing
  - wrong key
  - MAC mismatch

## 八、目前不建議的做法

### 1. 不建議再把主時間花在 passive ladder 爭論

因為在「TSK 已確認」前提下，
這已經不是主阻塞。

### 2. 不建議一開始就直接追最終 key

因為這樣會把：

- dump 問題
- layout 問題
- parser 問題
- sync 問題

全部混成一團。

### 3. 不建議沒有完整 transcript 就做 active write-back

因為這樣之後很難回頭比對：

- 到底哪一層失敗

## 九、一句話總結

如果現在前提是 **TSK 已確認**，那專案下一階段的正確重心就不是再證明 `TSK`，而是用 **dump-only -> candidate parser -> write-back validation** 這條最短鏈，把 `SecOC / TSK` 相關材料穩定、快速、可重現地導出。

## 參考

- [current-findings-summary-v2.md](current-findings-summary-v2.md)
- [OPENPILOT_INTEGRATION_PROGRESS_REPORT.md](../OPENPILOT_INTEGRATION_PROGRESS_REPORT.md)
- [direct-tsk-branch-decision-note-zh.md](direct-tsk-branch-decision-note-zh.md)
- [direct-tsk-branch-minimum-validation-order.md](direct-tsk-branch-minimum-validation-order.md)
- [secoc-direct-branch-modification-methods-20260509-zh.md](secoc-direct-branch-modification-methods-20260509-zh.md)
