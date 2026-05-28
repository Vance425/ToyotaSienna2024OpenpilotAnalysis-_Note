# Bootloader Identification 觀察

## 目前應該怎麼記錄

在目前這台 `2024 Toyota Sienna` 的 direct-branch 診斷紀錄裡，相關識別資訊應記成：

- application 側 `APPLICATION_SOFTWARE_IDENTIFICATION`：
  - `8965B4514000`
- bootloader 側 `APPLICATION_SOFTWARE_IDENTIFICATION` 回應：
  - `\x02!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!`

## 這代表什麼

重點不是把這段 bootloader 回應讀成「正常版本字串」。

更合理的解讀是：

- bootloader 路徑有被碰到
- bootloader 側 DID 有回應
- 但回來的內容比較像 filler-like / low-information response

所以它更適合被當成：

- 目前受測目標的識別特徵
- bootloader path reached 的證據

而不是：

- 一般語義清楚的 bootloader version label

## 為什麼這很重要

這可以避免後面文件再把：

- `8965B4514000`
- 和 `\x02!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!`

混成同一種「正常可讀版本資訊」。

也能讓受測車型內容和 direct-branch 分析使用同一套表述。
