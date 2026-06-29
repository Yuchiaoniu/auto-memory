# finance-study-app — 現況快照

## 目前狀態

**截圖腳本修正完成、PPTX 已更新**

- App 本機 http://localhost:3000 正常運行（15 章節、383 題）
- `take_study_app_screenshots.py` 修正完成：ch04 損益表/資產負債表/現金流量均顯示計算結果
- `study_app_snapshot.pptx`（23 頁）已重新生成（2026-06-24）

## 待辦

- 關閉 PowerPoint 後，複製 study_app_snapshot.pptx 覆蓋 財務管理資訊系統期末報告20260623.pptx：
  ```
  Copy-Item "C:\Users\yuchi\pptx-builder\output\study_app_snapshot.pptx" `
            "C:\Users\yuchi\pptx-builder\output\財務管理資訊系統期末報告20260623.pptx" -Force
  ```
- `take_study_app_screenshots.py` 內仍有 ch04 debug 塊（第 410-425 行）可移除（確認 PPTX 正確後）

## 下一步

確認 PPTX 內容正確，移除 debug 塊，PPTX 提交期末報告。