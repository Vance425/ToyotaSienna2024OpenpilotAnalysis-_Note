# Integration Mapping Technical Report - Toyota Sienna 2024

## 1. Executive Summary
本報告定義了將 openpilot 控制請求映射至 2024 Toyota Sienna 執行器控制單元 (ACU) 的技術路徑。核心目標是利用已驗證的 `VIRTUAL_TSK_SPEC.md` 公式，實現安全且精確的轉向控制。

## 2. Control Chain Architecture
### 2.1 Signal Flow
**openpilot Request** $\to$ **Slew Rate Limiter** $\to$ **Setpoint Mapper** $\to$ **CAN Frame Generator (0x260)** $\to$ **ACU Execution**.

### 2.2 Sync Path (The Guardian)
- **Primary Control**: `0x260` (Srv_Setpoint).
- **Sync Anchor**: `0x2E4`.
- **Mechanism**: 利用 `0x2E4` 的低延遲特性（$0\text{ms}-17\text{ms}$）作為指令發送前的狀態預檢，確保控制鏈路在合法相位下運行。

## 3. Mapping Logic & Formulas
### 3.1 Setpoint Decoding/Encoding
根據 TSK 規範，`Srv_Setpoint` 的計算公式為：
$\text{Value} = \text{sign}(B1) \times (\text{Int16LE}(B2, B3) + (B5_{\text{signed}} \ll 8))$

### 3.2 Directional Mapping Model
定義 $\text{Req\_Slew}$ 為 openpilot 的標準化轉向請求 $[-1, 1]$：
- **Positive Range (Left/Right)**: $[289, 7981]$
  $\text{Setpoint}_{\text{pos}} = \text{clamp}(289 + (\text{Req\_Slew} \times \text{Scale}_{\text{pos}}), 289, 7981)$
- **Negative Range (Right/Left)**: $[-2300, 289]$
  $\text{Setpoint}_{\text{neg}} = \text{clamp}(289 + (\text{Req\_Slew} \times \text{Scale}_{\text{neg}}), -2300, 289)$

### 3.3 Safety Constraints (The Redlines)
- **Neutral Point**: $289$ (所有控制必須以此為中心)。
- **Slew Rate Limit**: 單次週期 $\Delta\text{Setpoint} \le \text{Limit}_{\Delta}$，防止觸發 ACU 保護機制。
- **Saturation Alert**: 注意反向量程（$-2300$）遠小於正向量程（$7981$），控制算法需在接近 $-2300$ 時提前進行飽和處理。

## 4. Implementation Roadmap
1. **Virtual Simulation**: 在模擬環境中驗證上述映射公式的線性度。
2. **Passive Validation**: 使用 `20260312_190101_000` 等 Grade A Logs 比對預期 setpoint 變化與實際 Slew 表現。
3. **Hardware-in-the-loop (HIL)**: 在實車上進行低幅度的 Neutral $\to$ Setpoint 微調測試。

## 5. Conclusion
本映射方案在技術上可行，且嚴格遵守了 TSK 的解碼定義。儘管量程不對稱，但透過 Slew Rate Limiter 與方向感知 clamp，可以有效降低系統跳出的風險。
