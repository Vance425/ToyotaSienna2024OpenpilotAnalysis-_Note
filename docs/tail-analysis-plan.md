# Tail Analysis Plan

## 為什麼現在該看 tail

前面的工作已經把事件模板縮得夠小了：

- `0x131` 定邊界
- `0x260` 定 family state
- `0x116` 切 phase

所以下一步最值得看的，就是：

`0x116` 的 tail bytes (`b4-b7`) 是否和這個 state base 有固定關係。

## 要看的核心問題

1. 同一個 `0x116` phase 下，tail 是否仍然快速變動
2. 不同 state base 下，tail 的分布是否明顯改變
3. `0x116` 的 tail 是否比較像：
   - auth tag
   - rolling value
   - state-dependent protected output

## 建議先看的方式

先不要試著直接解 auth。

先做這三件事：

1. 固定某個 `0x116` phase 值，觀察 tail 變化
2. 換到另一個 `0x116` phase，對比 tail 分布
3. 對照同一時刻的 `0x131.b3` 與 `0x260.b4`

## 下一輪最值得做的事

用 `184921` 和 `185451` 這兩個窗口，整理：

- `0x116 phase`
- `0x131 state base`
- `0x260 family base`
- `0x116 tail`

看 tail 是否可以被 state/phase 分群。
