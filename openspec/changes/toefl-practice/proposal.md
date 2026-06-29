## Why

準備 TOEFL 考試需要大量且系統化的練習，市面上的題庫資源零散、不互動，且多需付費。本工具提供 1000 道完整題庫（單字 557、閱讀 168、文法 275），搭配即時評分、詳解、錯題複習與 TOEFL 分數區間估計，讓使用者能隨時自主備考。

## What Changes

- 建立純靜態前端 TOEFL 練習題庫網站（`C:\Users\yuchi\toefl-practice\`）
- 提供 1000 題三類型題庫（Vocabulary / Reading / Grammar）
- 每次 Quiz 從題池隨機抽 50 題，完成後顯示正確率與 TOEFL 分數區間估計
- 錯題自動記錄於 localStorage，支援「錯題複習」模式
- 每題附詳細解析說明答案理由

## Capabilities

### New Capabilities

- `start-screen`: 首頁，可選題型（All/Vocabulary/Reading/Grammar）與模式（Quiz/Review Mistakes），顯示可用題數與錯題數
- `quiz-mode`: Quiz 主畫面，隨機抽 50 題，逐題作答，即時顯示對錯與解析
- `review-mistakes-mode`: 僅從 localStorage 錯題池抽題複習，支援清錯題紀錄
- `result-screen`: 完成畫面，顯示答對/答錯數、正確率，以及對應 TOEFL 分數區間

### Modified Capabilities

（無既有 spec，全為新建）

## Impact

- 純前端靜態網站（HTML + CSS + JavaScript），無後端、無 API 依賴
- 題庫硬編碼於 `questions.js`（1000 題物件陣列）
- 錯題紀錄透過 localStorage 持久化，重整不遺失
- 可部署至 GitHub Pages 供隨時存取
