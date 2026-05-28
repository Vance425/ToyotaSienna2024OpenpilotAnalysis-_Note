# Direct TSK 分支決策短版

## 先講結論

如果未來要重開 `direct TSK branch`，現在的正確態度不是：

- 直接沿用舊 `secoc` 方法去跑

而是：

- 把它當成一條高風險、版本綁定、需要重新逐步驗證的分支

一句話：

> 舊方法可以當參考，但不能當現成可用方案。

## 舊方法本質是什麼

舊方法不是被動分析 CAN。

它是在做：

1. 對 EPS 側 ECU 走 UDS
2. 進 programming session
3. 用舊的 `SEED_KEY_SECRET` 解鎖
4. 寫 DID
5. 上傳 payload
6. 觸發 routine
7. dump ECU 記憶體
8. 從記憶體裡解析出 TSK

所以它本質上是：

- 主動
- 高風險
- firmware-specific
- 直接取 key 的 exploit 路線

## 為什麼不能直接照舊跑

目前最可能已失效的地方是：

1. 直接 `SecurityAccess` 路徑
2. 舊的 `SEED_KEY_SECRET`
3. DID / download / routine-control 流程
4. payload 相容性
5. 固定 dump 位址與 key structure 偏移

也就是說，最可能不是死在最後的 key parsing，
而是死在中間的：

- session
- unlock
- download
- trigger

## 如果真的要重開 direct 分支，最小驗證順序

只能按這個順序往前走：

1. 目標 ECU reachability
2. APP / bootloader version
3. session transition
4. `SecurityAccess` 行為
5. DID prerequisite
6. download path
7. routine trigger
8. payload compatibility
9. dump validity
10. key-structure validity

前四步最重要。

如果：

- ECU 連不上
- session 不通
- seed path 不存在

那就不應該再往 payload / dump 走。

## 現在應怎麼看這條分支

現在最合理的定位是：

- 舊 `secoc` 分支 = 歷史上的 direct extraction 參考分支
- 現在主線 = passive / regime-first 分析分支

也就是：

- 舊分支保留做架構參考
- 主線仍然以低風險的被動分析為主

## 舊分支今天還有什麼價值

它今天仍然有三個價值：

1. 告訴我們 direct TSK 本質上是 firmware / bootloader 問題
2. 告訴我們 EPS 側 authority 值得重視
3. 告訴我們如果要重開 direct branch，該先驗什麼

## 最短決策句

如果今天要決定：

> 要不要直接走舊 `secoc` 方法？

答案是：

> 不直接照跑。只能把它當高風險候選分支，按驗證階梯一步步重證。

## 入口文件

- [old-secoc-direct-branch-overview.md](./old-secoc-direct-branch-overview.md)
- [direct-tsk-branch-minimum-validation-order.md](./direct-tsk-branch-minimum-validation-order.md)
