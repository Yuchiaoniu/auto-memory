# 國中國文學習平台

純靜態 HTML/CSS/JS 教育網站，涵蓋七至九年級五大學習模組。

## 快速開始（本地開啟）

由於瀏覽器的 CORS 限制，直接雙擊 HTML 檔案會導致 JSON 資料無法載入。請使用任一方式開啟：

### 方法 1：VS Code Live Server（推薦）
1. 安裝 VS Code 擴充套件「Live Server」
2. 右鍵點擊 `index.html` → **Open with Live Server**

### 方法 2：Python HTTP Server
```bash
# 在專案根目錄執行
python -m http.server 8080
# 然後開啟 http://localhost:8080
```

### 方法 3：Node.js
```bash
npx serve .
```

## 目錄結構

```
junior-high-chinese/
├── index.html              首頁（五大模組導覽）
├── pages/
│   ├── text-reading.html       課文閱讀列表
│   ├── text-detail.html        課文閱讀內頁
│   ├── literary-knowledge.html 文學常識
│   ├── rhetoric-techniques.html 修辭技巧
│   ├── classical-translation.html 古文今譯
│   └── writing-practice.html  寫作練習
├── data/
│   ├── texts.json              課文資料（5 篇示範）
│   ├── authors.json            作者資料（10 位）
│   ├── rhetoric.json           修辭法定義（10 種）
│   ├── rhetoric-quiz.json      修辭測驗（30 題）
│   ├── classical.json          古文今譯（5 篇）
│   ├── writing-topics.json     作文題目（6 題）
│   ├── writing-guides.json     寫作技巧指引（4 文體）
│   └── writing-samples.json    範文（2 篇）
├── css/
│   └── common.css              共用樣式
└── js/
    └── common.js               工具函式庫
```

## 新增內容

所有內容以 JSON 格式維護，不需修改 HTML。

### 新增課文（texts.json）

```json
{
  "id": "text-006",
  "grade": 7,
  "title": "課文標題",
  "author": "作者",
  "source": "出處",
  "genre": "記敘文",
  "author_id": null,
  "paragraphs": [
    {
      "text": "段落內容...",
      "guide": "導讀說明..."
    }
  ],
  "vocabulary": [
    {
      "word": "生字詞",
      "phonetic": "注音",
      "meaning": "解釋",
      "paragraph_index": 0
    }
  ]
}
```

### 新增古文（classical.json）

```json
{
  "id": "c-006",
  "grade": 9,
  "title": "文章標題",
  "author": "作者",
  "author_id": "author-xxx",
  "era": "朝代",
  "sentences": [
    {
      "id": "c-006-s-001",
      "classical": "古文原文",
      "modern": "今譯",
      "analysis": "語法解析說明",
      "key_words": [
        {
          "word": "字",
          "meaning": "解釋",
          "type": "詞義/通假字/古今異義/詞性活用/虛詞"
        }
      ]
    }
  ]
}
```

### 新增修辭測驗題（rhetoric-quiz.json）

```json
{
  "id": "q-031",
  "sentence": "題目句子",
  "options": ["比喻", "擬人", "誇飾", "排比"],
  "answer": "比喻",
  "explanation": "解析說明"
}
```

## 技術說明

- **框架**：無框架，純 Vanilla JS
- **樣式**：Tailwind CSS CDN + 自訂 CSS 變數
- **字型**：Noto Sans TC（Google Fonts）
- **資料**：JSON 檔案，fetch API 載入
- **儲存**：段落架構板使用 localStorage
- **部署**：GitHub Pages（純靜態，無需 Build）

## 版權說明

- 現代文課文：自編示範，僅供教學參考
- 古文：均為公版（先秦至清代），不受著作權限制
- 修辭例句：自編或引用公版文學作品

## GitHub Pages 部署

將專案推送至 GitHub repository，在設定中啟用 GitHub Pages：
- 選擇 `main` branch 的 `/ (root)` 資料夾
- 或使用 `/docs` 資料夾（需將檔案複製到 docs/）
