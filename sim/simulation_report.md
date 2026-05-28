# Simulation Validation Report - Toyota Sienna 2024 Control Logic

## 1. Test Objective
驗證將 openpilot 標準化請求 $[-1, 1]$ 映射至 `Srv_Setpoint` $\text{Range: } [-2300, 7981]$ 的線性度、邊界截斷以及 Slew Rate 限制器的有效性。

## 2. Validation Results
### 2.1 Boundary Check (Static)
| Input Request | Expected Setpoint | Actual Output | Result |
| :--- | :--- | :--- | :--- |
| `0` (Neutral) | $289$ | $289$ | ✅ Pass |
| `1` (Max Pos) | $7981$ | $7981$ | ✅ Pass |
| `-1` (Max Neg) | $-2300$ | $-2300$ | ✅ Pass |

### 2.2 Dynamic Behavior Analysis
- **Asymmetric Mapping**: 確認模型正確處理了非對稱量程。正向偏移量 ($7692$) 與負向偏移量 ($1049$) 在映射邏輯中已完全分離，確保請求 $\pm 1$ 能精準觸達物理極限。
- **Slew Rate Protection**: 模擬測試中，當指令從 $\text{Max Pos} \to \text{Max Neg}$ 發生階躍跳變時，`Slew Rate Limiter` 將輸出轉化為斜坡函數 (Ramp)，有效避免了單次週期內數值突變。

## 3. Conclusion
目前的數位分身模型已準確實作 `VIRTUAL_TSK_SPEC.md` 與 `integration_mapping_report.md` 定義的邏輯。控制鏈路在數學層面上是安全的，且符合 ACU 的保護規範。

**Next Step**: 建議進入 **Passive Validation** 階段，將此模型生成的預期數值與 Grade A 實車 Log 中的實際 `Srv_Setpoint` 變化進行交叉比對。
