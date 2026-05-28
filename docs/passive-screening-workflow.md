# 純被動人工篩選流程

## 目標

用現有與後續的被動 CAN log，人工縮小最像 `TSK / SecOC` 的 frame。

## Step 1: 先切場景

把 log 先依照場景分開看：

- `IGN off -> IGN on`
- `IGN on -> Ready`
- `ACC on/off`
- `ADAS on/off`
- `comma 3X` 失敗前後

不要一開始就把整包 log 混著看。

## Step 2: 先看重點 ID

優先看：

- `bus 0 / 0x116`
- `bus 0 / 0x177`
- `bus 0 / 0x260`

如果它們在關鍵窗口有異常，再往周邊 ID 擴。

## Step 3: 看 tail bytes 行為

### 0x116

- core: `0,1,2,3`
- tail: `4,5,6,7`

### 0x177

- core: `0,1,2,3`
- tail: `4,5,6,7`

### 0x260

- core: `0,1,2,3,4,5`
- tail: `6,7`

觀察：

- tail 是否單調輪轉
- tail 是否在狀態切換時 reset
- tail 是否在失敗前後異常停頓或突變

## Step 4: 對照 bus 1

當 `bus 0` 候選 frame 出現異常窗口時，回頭看同時間的 `bus 1`：

- 哪些 frame 開始出現
- 哪些 frame 消失
- 哪些 frame 頻率突然升高
- 哪些 frame payload 格式明顯不同

## Step 5: 記錄假設，不急著下結論

每次只形成一個小假設，例如：

- `0x116` 的 tail reset 和 IGN on 有關
- `0x177` 的 tail 異常和 `comma 3X` 失敗時間重疊
- `bus 1` 某些新 frame 可能是 security 相關輔助訊號

## 目前不做的事

- 不先假設哪個就是 TSK 本體
- 不先假設 tail 就一定是 MAC
- 不先把統計高分直接當成結論

## 成功輸出

每次人工篩選都應該至少產出：

- 一個關鍵時間窗口
- 一個候選 frame
- 一個可驗證假設
