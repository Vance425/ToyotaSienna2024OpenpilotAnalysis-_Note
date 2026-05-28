# 研究結果分享指南

## 目的

這份指南說明如何把目前的研究結果整理成可以分享給其他伙伴的版本。

目前專案裡的大部分研究筆記都放在：

- [practical](/D:/Codex/toyota-sienna-tsk-analysis/practical)

但這些檔案現在有一個現實問題：

- 很多 Markdown 連結是本機絕對路徑
- 例如：
  - `/D:/Codex/...`
  - `/D:/Temp/...`

這些連結在你自己的電腦上可用，但一上傳到網路空間後，別人點了會失效。

所以分享前，最好先做一次「導出 bundle」。

---

## 最穩的分享方式

目前最推薦的做法是：

1. 先產生一份 share bundle
2. 再上傳到：
   - 私有 GitHub repo
   - GitHub Pages
   - Google Drive / OneDrive / Dropbox
   - Notion 附件區

如果你只是要快速給夥伴看，最簡單的是：

- 產出 bundle
- 壓成 zip
- 上傳到雲端硬碟

如果你想要後續持續更新、版本可追蹤，最適合的是：

- 私有 GitHub repo

---

## 目前已經準備好的工具

導出腳本：

- [export_share_bundle.ps1](../scripts/export_share_bundle.ps1)

這支腳本會做幾件事：

- 複製 `practical/*.md`
- 複製 `scripts/` 到 bundle
- 把 repo 內的本機絕對路徑改成相對連結
- 把 `D:/Temp/...` 這類只存在你電腦上的 log 連結標成 `local-only`
- 產生 bundle 入口頁

---

## 直接操作方式

在 PowerShell 跑：

```powershell
powershell -ExecutionPolicy Bypass -File <LOCAL_ANALYSIS_WORKSPACE>\scripts\export_share_bundle.ps1
```

預設輸出會在：

- [share_bundle](/D:/Codex/toyota-sienna-tsk-analysis/share_bundle)

主要內容：

- `README.md`
- `docs/`
- `scripts/`

---

## 建議分享哪些內容

如果你要先給伙伴看最重要的內容，建議至少分享：

- [current-findings-summary-v2.md](./current-findings-summary-v2.md)
- [final-frame-role-map.md](./final-frame-role-map.md)
- [tsk-nearest-ladder-entry-to-anchor.md](./tsk-nearest-ladder-entry-to-anchor.md)
- [passive-tsk-nearest-overview-zh.md](./passive-tsk-nearest-overview-zh.md)
- [next-log-analysis-template.md](./next-log-analysis-template.md)
- [public-references-map.md](./public-references-map.md)
- [public-references-map-zh.md](./public-references-map-zh.md)

---

## 上傳後怎麼分享

### 方案 A：雲端硬碟

做法：

1. 跑導出腳本
2. 把 `share_bundle` 壓成 zip
3. 上傳到 Google Drive / OneDrive / Dropbox
4. 分享連結給伙伴

適合：

- 快速分享
- 不需要協作改文檔

### 方案 B：私有 GitHub repo

做法：

1. 跑導出腳本
2. 新建一個 private repo
3. 上傳 `share_bundle` 內容
4. 邀請伙伴

適合：

- 持續更新
- 需要版本追蹤
- 研究討論會反覆修改

### 方案 C：GitHub Pages / 靜態網頁

做法：

1. 跑導出腳本
2. 把 bundle 放到 repo
3. 用 GitHub Pages 發佈

適合：

- 需要網址直接打開文件
- 不適合放敏感資料

注意：

- 如果內容涉及敏感 reverse engineering 細節，優先用 private repo 或私有雲端硬碟

---

## 目前分享版的限制

即使經過 bundle 導出，還是要知道：

- 原始 `D:/Temp/...` log 不會一起上網
- 那些 log 連結會被標成：
  - `local-only`
- 如果你想讓伙伴也能看 raw log，需要另外決定是否分享原始資料

---

## 最短建議

如果你現在就要分享給伙伴，最穩的流程是：

1. 先跑：

```powershell
powershell -ExecutionPolicy Bypass -File <LOCAL_ANALYSIS_WORKSPACE>\scripts\export_share_bundle.ps1
```

2. 再把：

- [share_bundle](/D:/Codex/toyota-sienna-tsk-analysis/share_bundle)

壓成 zip 上傳到私有雲端空間

3. 分享 link 給伙伴

---

## 一句話

不是直接把現在的 Markdown 原封不動丟上網，而是先做一份：

- 可分享
- 相對連結化
- 本機路徑清理過

的 bundle，再發給別人。
