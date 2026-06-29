## ADDED Requirements

### Requirement: 純中文句子禁止直接嵌入英文工具名稱
在純中文敘述句中，英文工具名稱（如 Read、WebFetch、Bash、Edit 等）不得直接作為主詞或受詞使用。SHALL 先以白話中文描述其功能，若需標示原始名稱則以括號補充。

#### Scenario: 受詞為工具名稱時必須白話化
- **WHEN** 中文句子的受詞是英文工具名稱
- **THEN** 必須改為白話中文加括號，例如「要不要委派這個讀取動作（Read）」，不得寫「這個 Read 要不要委派」

#### Scenario: 主詞為工具名稱時必須白話化
- **WHEN** 中文句子的主詞是英文工具名稱
- **THEN** 必須改為白話中文加括號，例如「網頁抓取工具（WebFetch）會發出 HTTP 請求」，不得寫「WebFetch 會發出 HTTP 請求」
