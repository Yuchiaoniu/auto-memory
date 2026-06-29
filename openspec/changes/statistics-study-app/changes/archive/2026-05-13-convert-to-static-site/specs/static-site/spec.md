## ADDED Requirements

### Requirement: 純靜態檔案結構

系統 SHALL 以扁平結構放置所有靜態檔案於 repo 根目錄：根目錄含 `index.html`，子目錄含 `css/`、`js/`、`data/`、`chapters/`，無需 build 步驟即可部署。

#### Scenario: 開啟根目錄即首頁

- **WHEN** 訪客連到部署後的網址（GitHub Pages 或本機 server 根目錄）
- **THEN** 系統回傳 `index.html` 並顯示首頁

#### Scenario: 章節頁可獨立載入

- **WHEN** 訪客直接造訪 `/chapters/continuous-distributions.html`
- **THEN** 系統載入該頁，所有 CSS、JS、資料以相對路徑成功取得

### Requirement: 相對路徑載入資源

系統 SHALL 在所有 HTML 與 JS 中使用相對路徑連結資源（`./` 或 `../`），不使用 `<base href>`，亦不使用以 `/` 開頭的絕對路徑。

#### Scenario: 子目錄 fork 仍可運作

- **WHEN** 將整個 repo fork 並改名為 `my-stats-app`
- **THEN** 部署到 `<user>.github.io/my-stats-app/` 後所有資源照常載入，無需修改任何路徑

### Requirement: 題庫資料以 JSON 提供

系統 SHALL 將題庫以單一 JSON 檔案 `data/questions.json` 提供，包含所有題目的 id、chapter、concept、prompt、options、correct_index、explanation 欄位。

#### Scenario: 前端載入整份題庫

- **WHEN** 章節頁啟動 quiz 元件
- **THEN** 前端發出一次 fetch 取得 `../data/questions.json` 或 `./data/questions.json`，篩選後依觀念分組顯示

### Requirement: .nojekyll 設定

系統 SHALL 在 repo 根目錄放置空檔 `.nojekyll`，讓 GitHub Pages 跳過 Jekyll 處理。

#### Scenario: 含底線資料夾可被存取

- **WHEN** 訪客請求 `/openspec/changes/...` 之類路徑
- **THEN** 即使 GitHub Pages 預設會排除底線開頭資料夾，因為有 .nojekyll 而不受影響（雖然 openspec/ 本身不對外，但確保未來新增底線資料夾不出意外）

### Requirement: README 含部署步驟

系統 SHALL 在 README.md 提供下列段落：（1）本機預覽方式（`npx serve` 或 Live Server）、（2）GitHub Pages 啟用步驟、（3）如何新增題目並重新部署、（4）線上 demo 網址（部署後填入）。

#### Scenario: 新使用者照 README 部署

- **WHEN** 第一次接觸專案的使用者依 README 流程操作
- **THEN** 能在 10 分鐘內完成 fork → enable Pages → 看到自己版本上線
