# TSS2.5 SecOC 自助研究提示詞分享

這份文件是給對 Toyota / Lexus TSS2.5、openpilot / sunnypilot、CAN log、SecOC 驗證有興趣的人使用的公開分享版。

它不是一份「拿去就能得到 key」的文件，也不是某台車的固定答案。比較準確地說，它是一套研究提示詞與分析框架，目標是幫助你把自己的車輛資料整理成 AI 能分析的形式，並避免把別人的 CAN ID、firmware、payload、dump range 或 SecOC layout 誤套到自己的車上。

如果你只是剛開始嘗試，建議先從 read-only 資料收集開始。不要一開始就做 ECU write、programming session、security access、routine control、payload upload 或套用他人的 dump / key / firmware。

## 這裡提供什麼

本次分享包含兩份文字：

1. [TSS2.5 Generic Remote Research Prompt](./templates/tss2_5_generic_remote_research_prompt_zh.md)
   - 給 AI 或協作者使用的主提示詞。
   - 一開始會要求使用者填自己的車輛資訊。
   - 如果使用者不是專業研究者，會先引導收集低風險資料。
   - 內含研究隔離原則與 SecOC 公式推導方法。

2. [TSS2.5 Transferable Research Experience](./templates/tss2_5_transferable_research_experience_zh.md)
   - 我們目前研究中比較可轉移的方法經驗。
   - 重點是分析順序、排錯方式、candidate 驗證標準。
   - 可以借用方法，不應直接套用車輛實值。

## 使用方式

建議把兩份文字一起交給你使用的 AI 或研究協作者，並補充一句：

```text
請使用這兩份文件協助分析我自己的車輛資料。請不要套用其他車的 CAN ID、firmware、payload、dump range、key 或 SecOC layout。所有結論都必須由我提供的本車 log、DID、firmware、metadata 或實際觀察驗證。
```

接著先回答主提示詞裡的基本問題，例如：

```text
車型 / 年份：
市場版本：
ADAS / TSS 版本：
目標 ECU：
CAN bus：
UDS tx/rx：
已確認 DID：
firmware / part number：
目前遇到的問題：
已收集資料類型：
是否只做 read-only 分析：
```

不知道的欄位請填 `unknown`，不要用網路文章或其他車的資料代入。

## 可以套用的經驗

可以套用的是研究方法：

- 先建立本車 baseline，再談 SecOC。
- 優先分析既有 log、DID、firmware、metadata。
- 從本車 CAN log 找 protected message candidate。
- 區分 protected payload、sync source、event marker、status marker。
- 對 payload、counter、freshness、auth tag、tag truncation 做 formula candidate 推導。
- 用多組 frame 和 holdout frames 驗證公式。
- candidate 不等於 key，必須通過本車 MAC / auth tag 驗證。

不應直接套用的是研究結果：

- 不要直接套用其他車的 CAN ID。
- 不要直接套用其他車的 message layout。
- 不要直接套用其他車的 firmware / part number。
- 不要直接套用其他車的 dump range。
- 不要直接套用其他車的 payload、key、candidate 或公式。

## 對非專業使用者的建議

如果你不熟悉 CAN、UDS、DID、firmware、dump、SecOC，請先收集低風險資料：

- 車型、年份、市場版本。
- 是否有 LTA / LKA / ACC / AEB。
- 問題發生時的錯誤畫面或文字。
- 是否使用 openpilot / sunnypilot / comma 裝置。
- 是否有 route log、qlog、rlog、raw CAN log 或 app 匯出資料。

請先不要做：

- 不要寫 ECU。
- 不要跑 payload。
- 不要進 programming session。
- 不要做 security access。
- 不要執行 routine control。
- 不要套用別人的 key、dump、payload、firmware。

如果要做實車 read-only 收集，請先確認這是自己的車或已獲車主授權，車輛停在安全位置，並且你清楚知道自己只是在讀取資料。

## 公開分享前請先遮蔽

如果你要把 log、截圖、bundle 或分析結果貼到 issue、論壇、社群或其他 AI 工具，請先移除或遮蔽：

- VIN
- 車牌
- 精確 GPS 位置與住家 / 公司路線
- dongle id
- 帳號、token、API key
- SSH key、密碼、credential
- raw SecOCKey
- raw candidate key material
- private dump binary

如果要分享 candidate，請只分享 hash、長度、來源位置、驗證狀態，不要分享原始 key bytes。

## 一句話原則

可以借用我們的分析方法、排錯順序與驗證標準；不要借用我們或任何人的車輛實值、CAN ID、firmware、payload、dump range、key 或公式結論。

