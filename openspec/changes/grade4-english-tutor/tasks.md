## 1. 專案初始化

- [x] 1.1 建立專案目錄結構（`index.html`、`style.css`、`data/`、`pages/`）
- [x] 1.2 建立 `data/units.js`：定義 8 單元基本資料（編號、標題中英文、emoji）
- [x] 1.3 建立共用樣式：色彩變數、字型、卡片元件、按鈕、分頁標籤

## 2. 首頁與導覽（unit-navigator）

- [x] 2.1 建立 `index.html`：顯示課程標題與 8 張單元卡片（2 欄 4 列 grid）
- [x] 2.2 實作點擊單元卡片跳轉至 `unit.html?id=<n>` 的路由邏輯
- [x] 2.3 實作單元頁面四分頁標籤切換（單字/句型/對話/測驗）
- [x] 2.4 實作返回首頁按鈕

## 3. 教材資料建立

- [x] 3.1 建立 `data/unit1.js`（Hello, Friends!）：單字 8 個、句型 2 個、對話 6 句、測驗 5 題
- [x] 3.2 建立 `data/unit2.js`（My Family）：同上格式
- [x] 3.3 建立 `data/unit3.js`（At School）：同上格式
- [x] 3.4 建立 `data/unit4.js`（I'm Hungry!）：同上格式
- [x] 3.5 建立 `data/unit5.js`（Animals I Like）：同上格式
- [x] 3.6 建立 `data/unit6.js`（Dress Up!）：同上格式
- [x] 3.7 建立 `data/unit7.js`（What Time Is It?）：同上格式
- [x] 3.8 建立 `data/unit8.js`（What's the Weather?）：同上格式

## 4. 單字卡片（vocabulary-cards）

- [x] 4.1 實作單字卡片元件：emoji + 英文（大字）+ 中文 + 注音，單張顯示
- [x] 4.2 實作上一張/下一張按鈕與進度顯示（第 X / 共 Y 張）
- [x] 4.3 實作「查看全部單字」可展開列表

## 5. 句型練習（sentence-patterns）

- [x] 5.1 實作句型卡片展示：句型結構 + 中文說明 + 可展開例句
- [x] 5.2 實作填空練習：句型框架 + 3 個選項按鈕
- [x] 5.3 實作答對（綠色提示）與答錯（紅色提示）回饋邏輯

## 6. 對話閱讀（dialogue-reader）

- [x] 6.1 實作對話顯示：A 靠左藍色、B 靠右橘色，英中對照
- [x] 6.2 實作單字標示：本單元新單字加底線，點擊顯示翻譯 tooltip
- [x] 6.3 實作角色朗讀模式：角色選擇（A/B）+ 逐行高亮 + 空白鍵/按鈕推進

## 7. 單元測驗（unit-quiz）

- [x] 7.1 實作測驗流程：逐題顯示、選項點選、題號進度
- [x] 7.2 實作交卷與結果頁：得分 + 每題正誤標示 + 正確答案
- [x] 7.3 實作「再試一次」重置功能（選項打亂順序）

## 8. 大學伴提示面板（tutor-guide）

- [x] 8.1 實作面板收起/展開動畫（右側滑出）
- [x] 8.2 建立每單元大學伴提示資料：教學重點 + 常見錯誤 + 互動引導語
- [x] 8.3 實作面板內容隨當前分頁自動切換
- [x] 8.4 實作「顯示所有答案」功能（於測驗分頁的大學伴面板中）

## 9. 收尾與部署

- [x] 9.1 確認所有 8 單元資料完整且無錯別字
- [x] 9.2 響應式樣式調整（手機/平板單欄顯示）
- [x] 9.3 建立 GitHub Repository 並推送（https://github.com/Yuchiaoniu/english.git，master branch）
- [x] 9.4 啟用 GitHub Pages 部署，確認公開連結可正常存取
      → 公開網址：https://Yuchiaoniu.github.io/english/

## 額外完成（2026-05-11）

- [x] 單字擴充：每單元從 8 個字擴充至 16 個，共 128 個核心詞彙
- [x] 生成 PPTX 教材（145 張投影片）：C:\Users\yuchi\grade4-english-tutor\Grade4_English_Vocab.pptx
      → 結構：封面 + 單元封面×8 + 單字卡×128 + 單元總整理×8
- [ ] 確認翰林版實際課綱單元是否與現有 8 單元吻合，視需要調整內容

## 額外完成（Multi-Topic Review PPTX）

- [x] 製作跨單元複習簡報（16 頁）：C:\Users\yuchi\grade4-english-tutor\Multi_Topic_Review.pptx
      → 涵蓋天氣、時間、情緒、教室物品、介系詞 at/on/in
      → 產生器 make_multi_topic_pptx.py；黃色主題配色

## 額外完成（2026-05-24）

- [x] 補齊 `data/unit7.js` 單字：由 8 個擴充至 16 個（新增 four~ten、time，並修正 o'clock 注音為 ㄉㄧㄢˇ ㄓㄨㄥ）
- [x] 製作第七課單課完整簡報（17 頁）：C:\Users\yuchi\grade4-english-tutor\Unit7_What_Time_Is_It.pptx
      → 結構：封面 + 單字總覽 + 數字/時間字卡 + 句型×2 + 對話 + 測驗×2 + 解答 + 大學伴提示 + 結尾
      → 產生器 make_unit7_pptx.py；數字卡改用鐘面 emoji 🕐–🕙（PowerPoint 對 keycap 1️⃣ 放大會空白）
