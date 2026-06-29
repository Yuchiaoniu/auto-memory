## ADDED Requirements

### Requirement: Display accounting problem
每道練習題 SHALL 顯示以下欄位：章節標籤（如 Ch04）、題號、題目說明段落、題目本文（含子項 (1)(2)... 列點）、空白答案區。

#### Scenario: Problem renders all fields
- **WHEN** 頁面載入完成
- **THEN** 每道題顯示章節標籤、題號、說明段落、題目本文、空白答案 textarea

#### Scenario: Blank answer area is editable
- **WHEN** 使用者點擊答案區
- **THEN** 可以在 textarea 內輸入文字

### Requirement: Multi-item problem sub-questions
題目本文中如含有 (1)(2)(3)... 子項，SHALL 以清單方式呈現，保持縮排與可讀性。

#### Scenario: Sub-questions displayed as list
- **WHEN** 題目資料含有子項陣列
- **THEN** 每個子項獨立一行顯示，前面標示 (1) (2) ... 編號
