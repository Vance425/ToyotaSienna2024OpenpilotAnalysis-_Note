# LKAS Context 快速閱讀 2026-05-08

這份文件保留當時 LKAS context log 的閱讀結論。公開版 repo 不包含原始 context log，因為原始輸出會混入 C3X device status、swaglog、params 狀態與本機/裝置路徑。

## 當時觀察目的

當時要確認的是：

- 是否處於 Toyota Sienna fingerprint context
- `SecOCKey` 是否存在
- 是否出現 SecOC synchronization / MAC mismatch 類訊息
- 這些訊息是否能解釋 `LKAS Failed`

## 主要觀察

1. fingerprint context 指向 `TOYOTA_SIENNA_TSS25_PLUS`。
2. context 中曾看到 `SecOCKey missing` 類訊息。
3. context 中曾看到 `SecOC synchronization MAC mismatch, wrong key?` 類訊息。
4. 這些訊息支持「LKAS failure 與 SecOC key / synchronization 狀態有關」的早期判斷。

## 後續狀態

後續分析已找到並安裝有效 SecOC key，因此這份 context log 的價值主要是作為早期故障定位線索，不再作為最終 proof。

目前最終結論應停在：

- SecOC key 已分析完成
- key 已在 C3X 安裝
- key 生效後，重點轉為 live validation 與 openpilot / sunnypilot 整合驗證

## 公開版處理

原始 context log 不放入 public repo。公開版只保留本摘要，避免暴露裝置狀態、路徑或其他可識別資訊。
