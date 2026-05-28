# 公開參考資料地圖

## 用途

這份文件把目前和專案最相關的公開資料整理成一張地圖。

目的不是說：

- 網路上已經有一份資料能直接解完 `2022 Sienna` 的 `TSK`

而是回答：

- 哪些公開資料最接近 direct `TSK` 提取
- 哪些適合拿來理解 `SecOC` 結構
- 哪些能反映 Toyota / openpilot / `TSK` 的社群現況
- 哪些只是一般 CAN reverse engineering 方法論參考

---

## 快速結論

目前公開資料大致可以分成四類：

1. **Direct TSK / SecOC key extraction**
2. **SecOC 結構與協定參考**
3. **Toyota / openpilot / TSK 社群脈絡**
4. **一般 CAN 逆向方法論**

最重要的限制是：

- 目前找不到一份公開資料，已經完整復現我們現在這套：
  - `0x116 / 0x131 / 0x2E4` protected-lifecycle 解讀
  - `TSK-nearest` 梯子
  - bridge-state 錄製目標與判讀方法

所以公開資料目前最適合拿來做：

- 對照
- 校準方向
- 補架構理解
- 驗證這條路不是憑空想像

而不是拿來直接取代我們自己的 Toyota-specific 模型。

---

## 1. 最接近 Direct TSK / SecOC Key Extraction 的公開資料

### A. I CAN Hack：2021 RAV4 Prime 的 SecOC key extraction

連結：

- [I CAN Hack: Extracting Secure Onboard Communication (SecOC) keys from a 2021 Toyota RAV4 Prime](https://icanhack.nl/blog/secoc-key-extraction/)

為什麼重要：

- 這是目前最接近我們最終目標的公開 Toyota 參考
- 它不是在猜 key，而是真的走：
  - firmware extraction
  - bootloader reverse
  - payload upload
  - RAM key extraction

怎麼用：

- 把它當成 **direct branch** 的最佳公開範例
- 拿來理解真正的 direct extraction 路徑長什麼樣

注意：

- 它的對象是 `2021 RAV4 Prime`
- 不能直接假設它對 `2022 Sienna` 仍然完全適用

### B. hardwear.io：My car, My keys

連結：

- [hardwear.io: My car, My keys: obtaining CAN bus SecOC signing keys](https://hardwear.io/my-car-my-keys-obtaining-can-bus-secoc-signing-keys/)

為什麼重要：

- 是同一路研究的公開摘要版
- 很清楚地告訴我們：
  - 這本質上是 ECU / bootloader / update path 問題
  - 不是只靠看 CAN log 就能直接推出 key

怎麼用：

- 很適合拿來跟本地協作者解釋：
  - passive log work
  - 和 direct extraction
  是兩條不同工作線

### C. Hackaday 摘要

連結：

- [Hackaday: Extracting SecOC Keys From A 2021 Toyota RAV4 Prime](https://hackaday.com/2024/03/08/extracting-secoc-keys-from-a-2021-toyota-rav4-prime/)

為什麼重要：

- 比原文更好讀
- 適合快速讓非技術讀者進入狀況

怎麼用：

- 只當易讀摘要
- 不當主技術來源

---

## 2. 最適合對照 SecOC 結構的公開資料

### A. AUTOSAR SecOC 規格

連結：

- [AUTOSAR CP SWS Secure Onboard Communication (R24-11)](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_SecureOnboardCommunication.pdf)

為什麼重要：

- 這是最底層、最正式的結構參考
- 它能幫我們理解：
  - secured I-PDU
  - authenticator
  - freshness value
  - verification
  - security profile

最值得看的部分：

- functional overview
- data covered by authenticator
- freshness value
- authentication / verification
- security profiles

怎麼用：

- 對照我們看到的：
  - `0x116` protected tail
  - auth-heavy 區域
  - rolling / freshness-like backbone
  - `0x131 / 0x116` lifecycle context

注意：

- 它解釋的是標準
- 不是 Toyota 實作細節
- 更不是 Toyota 的 `TSK` 值

### B. SecOC 解說型文章

例如：

- [SecOC in AUTOSAR: Secure Vehicle Communication Explained](https://www.altenpolska.pl/en/2025/07/28/secure-onboard-communication-secoc-in-autosar-architecture-and-practical-implementation/)

為什麼重要：

- 比 AUTOSAR 原規格更容易讀

怎麼用：

- 當 onboarding 輔助資料
- 精準判讀時仍以 AUTOSAR spec 為主

---

## 3. Toyota / openpilot / TSK 社群脈絡

這一類未必給你正式證明，但很有助於理解現實世界裡大家遇到的是什麼問題。

### A. optskug/docs

連結：

- [optskug/docs](https://github.com/optskug/docs)

為什麼重要：

- 這是目前公開社群裡最集中、最實務的 Toyota/Lexus/Subaru `TSK` / `SecOC` 說明之一
- 內容包括：
  - 車種列表
  - extraction / installation 說明
  - 社群歷史
  - openpilot 實務資訊

怎麼用：

- 做 reality check
- 看社群怎麼描述哪些車有 `TSK`
- 看哪些車線目前被視為 security-key relevant

注意：

- 這是社群文件，不是正式 reverse engineering proof set

### B. 2022 Sienna 相關 openpilot issue

連結：

- [commaai/openpilot issue #34012](https://github.com/commaai/openpilot/issues/34012)

為什麼重要：

- 它直接點到 `2022 Sienna Hybrid`
- 說明缺 SecOC key 時，這條車線確實會出現對應問題

怎麼用：

- 當作這台車線確實是 `TSK / SecOC` 問題的旁證
- 不要拿它當具體欄位模型證據

### C. comma / openpilot 官方頁面

連結：

- [openpilot docs](https://docs.comma.ai/)
- [comma openpilot page](https://comma.ai/openpilot)

為什麼重要：

- 幫助說明為什麼 SecOC 會影響 steering integration / openpilot

怎麼用：

- 只當一般背景資料

---

## 4. 一般 CAN Reverse Engineering 方法論

這一類不是 Toyota-specific，但對方法設計很有幫助。

### A. Online reverse engineering of CAN data

連結：

- ScienceDirect: Online reverse engineering of CAN data

為什麼重要：

- 很適合對照：
  - signal discovery
  - correlation
  - continuous / discrete signal handling
  - search space reduction

怎麼用：

- 拿來對照我們自己的：
  - field ranking
  - signal scoring
  - local-window correlation

### B. CAN reverse engineering survey

例如：

- [PMC survey with CAN reverse engineering work table](https://pmc.ncbi.nlm.nih.gov/articles/PMC10802965/)

為什麼重要：

- 幫我們把自己的方法放進更大的文獻脈絡裡

怎麼用：

- 當文獻背景
- 不是拿來推 Toyota-specific 結論

### C. 實務型逆向教學

例如：

- [CSS Electronics CAN reverse engineering overview](https://www.csselectronics.com/pages/can-bus-sniffer-reverse-engineering)

為什麼重要：

- 比較適合實務 onboarding

怎麼用：

- 做初學者導引
- 不當深層 Toyota/SecOC 推論依據

---

## 哪些最接近我們現在這個專案

### 最接近終極目標的

- [I CAN Hack SecOC extraction](https://icanhack.nl/blog/secoc-key-extraction/)

因為它最接近真正拿到 Toyota SecOC key 的公開案例。

### 最接近我們現在的 passive 結構分析

- [AUTOSAR SecOC specification](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_SecureOnboardCommunication.pdf)

因為它最適合對照：

- freshness-like 結構
- auth-heavy tail
- verification context

### 最接近 Toyota / openpilot 實際社群狀況

- [optskug/docs](https://github.com/optskug/docs)
- [commaai/openpilot issue #34012](https://github.com/commaai/openpilot/issues/34012)

---

## 公開資料目前仍然沒有直接給我們什麼

目前公開資料還沒有直接給出：

- 我們這套 `0x116 / 0x131 / 0x2E4` protected-lifecycle 解讀
- `TSK-nearest` 梯子
- `171414_000 -> 190101_000` 中間缺掉的 bridge-state
- 這套 Toyota-specific 的 regime-first passive 判讀方法

這些仍然是專案自己從樣本中慢慢整理出來的。

---

## 建議閱讀順序

如果是新加入專案的人，最短可用閱讀順序是：

1. [I CAN Hack SecOC extraction](https://icanhack.nl/blog/secoc-key-extraction/)
2. [AUTOSAR SecOC specification](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_SecureOnboardCommunication.pdf)
3. [optskug/docs](https://github.com/optskug/docs)
4. [commaai/openpilot issue #34012](https://github.com/commaai/openpilot/issues/34012)
5. ScienceDirect CAN reverse engineering paper

---

## 一句話收尾

公開資料現在能做的，是幫我們：

- 校準方向
- 理解 SecOC
- 知道 direct branch 長什麼樣
- 確認 Toyota / TSK 問題不是個人幻想

但它們還不能直接取代我們目前這套 Toyota-specific passive `TSK-nearest` 模型。
