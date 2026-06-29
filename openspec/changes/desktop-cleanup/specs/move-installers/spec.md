## ADDED Requirements

### Requirement: 將安裝檔與壓縮包移至「安裝檔」資料夾
系統 SHALL 將桌面上所有副檔名為 .exe、.msi、.msix、.zip、.7z 的檔案移至桌面的「安裝檔」資料夾。

#### Scenario: 移動安裝檔
- **WHEN** 桌面存在 .exe、.msi、.msix、.zip 或 .7z 檔案
- **THEN** 這些檔案被移入「安裝檔」資料夾，桌面不再有這些散落檔案
