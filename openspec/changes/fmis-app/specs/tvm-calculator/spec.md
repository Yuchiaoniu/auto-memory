## ADDED Requirements

### Requirement: 四變數 TVM 計算（任三解一）
TVM 計算頁 SHALL 提供 PV、FV、PMT、NPER、Rate 五個輸入欄位，使用者填入任意四個已知數後，系統計算第五個未知數。

#### Scenario: 計算終值 FV
- **WHEN** 使用者輸入 PV=100000、Rate=5%、N=10、PMT=0，並選擇「求 FV」
- **THEN** 系統顯示 FV=162889.46

#### Scenario: 計算現值 PV
- **WHEN** 使用者輸入 FV=200000、Rate=3%、N=5、PMT=0，並選擇「求 PV」
- **THEN** 系統顯示 PV=172367.92

#### Scenario: 計算年金期數 N
- **WHEN** 使用者輸入 PV=0、FV=1000000、Rate=6%、PMT=-50000，並選擇「求 N」
- **THEN** 系統顯示所需期數

### Requirement: EAR 有效年利率計算
TVM 頁面 SHALL 提供 EAR 計算區塊，輸入名目利率與複利頻率後計算有效年利率。

#### Scenario: 計算月複利 EAR
- **WHEN** 使用者輸入名目利率 12%、複利頻率 12（月複利）
- **THEN** 系統顯示 EAR = 12.68%

#### Scenario: 計算連續複利 EAR
- **WHEN** 使用者選擇「連續複利」並輸入名目利率 10%
- **THEN** 系統顯示 EAR = e^0.1 - 1 = 10.52%

### Requirement: 72 法則快算翻倍年數
TVM 頁面 SHALL 顯示 72 法則區塊，輸入年利率後即時顯示概估翻倍年數與精確翻倍年數。

#### Scenario: 計算翻倍年數
- **WHEN** 使用者輸入年利率 8%
- **THEN** 系統顯示概估年數 = 72/8 = 9 年、精確年數 = ln(2)/ln(1.08) = 9.01 年
