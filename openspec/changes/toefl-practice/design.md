## Architecture

純前端靜態網站，四個檔案，無任何外部依賴：

```
C:\Users\yuchi\toefl-practice\
  ├── index.html      結構與三個畫面（start / quiz / result）
  ├── style.css       樣式
  ├── app.js          狀態機與互動邏輯
  └── questions.js    1000 題題庫（const QUESTIONS = [...]）
```

## Data Model

每題為一個 JS 物件，結構如下：

```js
{
  id: number,           // 1–1000，唯一識別碼
  type: "vocabulary" | "reading" | "grammar",
  passage: string|null, // Reading 題目附文章段落
  sentence: string|null,// Vocabulary 題目附例句（含 <u> 標記目標字）
  question: string,
  options: [A, B, C, D],
  answer: number,       // 0-indexed 正確選項
  explanation: string   // 詳細解析
}
```

題庫分布：
| 類型 | 題數 | ID 範圍 |
|------|------|---------|
| vocabulary | 557 | 1–557 |
| reading | 168 | 558–725 |
| grammar | 275 | 726–1000 |

## State Management

```js
state = {
  type: 'all' | 'vocabulary' | 'reading' | 'grammar',
  mode: 'quiz' | 'review',
  queue: Question[],  // 當次 shuffle 後的 50 題
  index: number,
  correct: number,
  wrong: number,
  wrongIds: Set<number>,  // 從 localStorage 讀取並同步
}
```

錯題持久化：`localStorage.setItem('toefl_mistakes', JSON.stringify([...wrongIds]))`

## Screen Flow

```
start-screen
  ↓ [Start →]
quiz-screen (50 題)
  ↓ 全部完成
result-screen
  ↓ [Retry] → quiz-screen（重新抽題）
  ↓ [Review Mistakes] → quiz-screen（mode=review）
  ↓ [Home] → start-screen
```

## TOEFL 分數估算邏輯

| 正確率 | 估算分數區間 |
|--------|-------------|
| ≥ 90% | 100–120（Excellent）|
| ≥ 75% | 85–100（Good）|
| ≥ 60% | 70–85（Intermediate）|
| < 60% | below 70 |
