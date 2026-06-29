## ADDED Requirements

### Requirement: 歷史清單持久顯示
頁面 SHALL 在上傳區下方顯示「已建立表單」清單，內容從 localStorage `form_history` 讀取，重新整理後仍保留。

#### Scenario: 首次開啟（無歷史）
- **WHEN** localStorage 無 `form_history` 資料
- **THEN** 歷史區塊隱藏，不顯示任何內容

#### Scenario: 有歷史記錄
- **WHEN** localStorage 有 `form_history` 資料
- **THEN** 依建立時間倒序列出每筆，顯示檔案名稱、編輯連結、填寫連結、建立時間

### Requirement: 建立成功後寫入歷史
每次 POST /create-form 成功後，系統 SHALL 將該筆記錄寫入 localStorage 並即時更新清單。

#### Scenario: 建立表單成功
- **WHEN** /create-form 回傳 error 為 null
- **THEN** 新增 { fileName, editUrl, respondUrl, createdAt } 到 localStorage，清單立即出現該筆

### Requirement: 表單標題使用檔名
建立表單時，系統 SHALL 以上傳檔案的名稱（去除 .docx 副檔名）作為 Google Forms 的標題。

#### Scenario: 上傳 .docx 並建立表單
- **WHEN** 使用者上傳 `成人體適能問卷.docx` 並建立表單
- **THEN** Google Forms 標題為「成人體適能問卷」，歷史清單也顯示「成人體適能問卷」

### Requirement: 清除所有記錄
頁面 SHALL 提供「清除所有記錄」按鈕，點擊後清空 localStorage 並隱藏歷史清單。

#### Scenario: 點擊清除
- **WHEN** 使用者點擊「清除所有記錄」
- **THEN** localStorage `form_history` 清空，歷史區塊隱藏
