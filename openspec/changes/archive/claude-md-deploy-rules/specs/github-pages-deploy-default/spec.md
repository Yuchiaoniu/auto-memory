## ADDED Requirements

### Requirement: GitHub Pages 預設部署在 main 分支根目錄
部署到 GitHub Pages 時，Claude SHALL 預設使用 main 分支根目錄（root），不使用 docs 資料夾或其他分支，除非有明確的特殊原因。

#### Scenario: 無特殊原因時使用 main 根目錄
- **WHEN** Claude 需要部署靜態網站到 GitHub Pages
- **THEN** Claude 預設選擇 main 分支、根目錄（root）作為 Pages 來源，不詢問、不改用 docs

#### Scenario: 有特殊原因時先討論再決定
- **WHEN** 存在合理的特殊原因需要使用 docs 資料夾或其他分支（例如 repo 根目錄有非網站內容、需要與其他工具共存）
- **THEN** Claude 必須先說明原因並與使用者討論確認，不得自行決定偏離預設
