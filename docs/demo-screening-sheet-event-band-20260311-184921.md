# 人工篩選紀錄表: 第四輪事件帶示範

## 基本資訊

- Log 名稱：`toyota_seg_IGN_ON_20260311_184921_000.ndjson`
- 場景：`IGN_ON`
- 分析模式：事件帶
- 分析人：Codex

## Anchor 條件

- 以 `0x610` 變化點為 anchor
- 在附近小窗口內檢查：
  - `0x131 resetlike`
  - `0x116 phase change`
  - `0x260 prefix change`
  - `0xD5` 是否不變

## 最佳 anchor

- `1773255027173`

### 判定結果

- `0x131 resetlike`：是
- `0x116 phase change`：是
- `0x260 prefix change`：是
- `0xD5 changed`：否

## 次級 anchor

- `1773255028267`
- `1773255031370`

## 本輪結論

- 最佳事件帶入口：`1773255027173`
- 最值得延用的模板：
  - `0x610` 有事件點
  - `0xD5` 不動
  - `0x131` resetlike
  - `0x116` phase change
  - `0x260` prefix change

## 下一輪假設

其他真正接近 `comma 3X` 失敗的 log，如果也出現相同模板，就很值得優先做深入比對。
