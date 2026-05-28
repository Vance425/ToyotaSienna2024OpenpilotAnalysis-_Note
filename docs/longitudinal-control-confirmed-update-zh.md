# 縱向控制已確認可用更新

## 目前狀態

以目前專案層級來說：

- `2024 Toyota Sienna` 搭配 `C3X` 的縱向控制，現在已可視為**實車已確認可用**。

這代表縱向這條線已經從：

- replay-backed working interpretation

往前推進到：

- vehicle-confirmed controllability

## 這件事確認了什麼

- 先前以 `0x260` 為中心的 control-side 解讀方向是對的。
- `0x260` 仍然是目前最強的縱向 / control-side anchor。
- ACC-active 的加速 / 減速行為，仍然最適合解讀成：
  - **多個 ID 同步變化的事件群**
  - 而不是單一一個 brake ID 或 accel ID
- 先前最強的 replay-backed branch 仍然是目前最可信的 implementation-facing 解讀：
  - `no_b1_flip + identity + higher slew`

## 這件事還沒有自動證明什麼

- `SecOCKey` 已可重複穩定導出
- freshness / synchronization 已完全閉合
- MAC / packing 已完全閉合
- final minimum protected message set 已經固定
- 當前 control mapping 已經是 deployment-final

## 這對專案的實際意義

現在縱向這條線應該分成兩層來看：

1. **實車結果層**
   - 縱向控制已經可以在 `2024 Toyota Sienna` 上工作
2. **實作閉合層**
   - repeatability
   - secure/auth stability
   - final message-set acceptance
   - stable fault handling / recovery

## 相關參考

- [VIRTUAL_TSK_SPEC_v2.md](VIRTUAL_TSK_SPEC_v2.md)
- [openpilot-control-side-working-note.md](openpilot-control-side-working-note.md)
- [current-findings-summary-v2.md](current-findings-summary-v2.md)
- [post-secoc-key-remaining-checklist-zh.md](post-secoc-key-remaining-checklist-zh.md)
