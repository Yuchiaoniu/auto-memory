## Context

參考既有的 statistics-study-app 與 finance-study-app 風格，建立純靜態會計學練習題網頁。無後端需求，檔案直接部署或本機開啟。

## Goals / Non-Goals

**Goals:**
- 靜態單頁 HTML，CSS 內嵌或獨立檔，JS 處理篩選互動
- 依章節（Ch04／Ch05／Ch06）顯示題目，支援篩選切換
- 每題含：章節標籤、題號、題目說明段落、題目本文、空白答案區
- 版面清晰易讀，適合列印或螢幕閱讀

**Non-Goals:**
- 不實作自動批改或答案顯示功能（第一版）
- 不需要登入、帳號、後端 API
- 不需要資料庫

## Decisions

| 決策 | 選擇 | 理由 |
|------|------|------|
| 頁面架構 | 單一 index.html | 無後端，部署最簡單；與 statistics/finance-study-app 一致 |
| 樣式 | 內嵌 `<style>` 或獨立 style.css | 減少相依檔案，方便直接開啟 |
| 資料儲存 | JS 陣列（hardcoded 題目） | 題目數量少，不需外部 JSON；易於擴充新題 |
| 章節篩選 | 按鈕切換 + JS filter | 簡單直覺，無需 router |
| 答案區 | 空白 `<textarea>` 或留白 div | 讓學生手動填寫或列印後手寫 |

## Risks / Trade-offs

- 題目全部 hardcoded → 新增題目需直接編輯 JS 陣列，但量少時可接受
- 無答案自動顯示 → 學生需自行對答案；後續可擴充「顯示解答」功能
