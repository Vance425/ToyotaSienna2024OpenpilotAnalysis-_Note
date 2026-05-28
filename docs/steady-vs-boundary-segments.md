# Steady vs Boundary Segments

## 為什麼現在要分段

目前已知：

- `n0` 在 phase 內常見 `+4`
- phase 切換時會重定相

所以最值得做的，不是再把所有點混在一起看，而是把 `0x116` 切成兩種區段：

- boundary segment
- steady segment

## 目前定義

### boundary segment

phase 剛切換後的前 `1-2` 個 `0x116` frame。

### steady segment

同一 phase 內，phase 已經穩住後的後續 `0x116` frame。

## 這樣做的好處

如果 `n0` 真的是 phase-aware rolling nibble，那麼：

- boundary segment 應該比較容易出現重定相或異常步進
- steady segment 應該比較容易恢復 `+4` 骨架

## 下一輪最值得驗證的事

1. `n0` 的 `+4` 是否主要出現在 steady segment
2. `n1/n3` 的混亂是否主要集中在 boundary segment
3. 如果是，則 `0x116 tail` 可以再拆成：
   - phase reset zone
   - phase steady zone
