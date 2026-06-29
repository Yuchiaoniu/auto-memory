## Why

桌面上累積了大量散落的檔案（捷徑、安裝檔、圖片、文件等），導致桌面雜亂難以使用。透過分類整理，讓桌面保持乾淨，方便日後快速找到所需檔案。

## What Changes

- 將所有捷徑（.lnk, .url）集中移至「捷徑」資料夾（**已完成**）
- 刪除 Word 暫存檔（~$*, ~WRL*.tmp）（**已完成**）
- 將安裝檔與壓縮包（.exe, .msi, .msix, .zip, .7z）移至「安裝檔」資料夾
- 將圖片與影片（.jpg, .jpeg, .png, .svg, .mp4 等）移至「媒體」資料夾
- 將散落的學校文件（.docx, .doc, .pdf, .pptx, .xlsx 等）歸入適當資料夾

## Capabilities

### New Capabilities

- `move-installers`: 將安裝檔與壓縮包集中到「安裝檔」資料夾
- `move-media`: 將圖片與影片集中到「媒體」資料夾
- `move-documents`: 將散落的學校文件歸入適當資料夾

### Modified Capabilities

（無）

## Impact

- 桌面路徑：`C:\Users\yuchi\OneDrive\Desktop`
- 僅移動檔案，不刪除內容（除已完成的暫存檔清理外）
- 不影響任何程式或系統設定
