# 專案記憶：junior-high-chinese

## PPT 製作規格

### 投影片尺寸
- 寬 × 高：13.33" × 7.5"（python-pptx 寬螢幕）
- 字型：微軟正黑體（FONT = "微軟正黑體"）

### 內容區域常數
```
CT  = Inches(1.42)   # content top（標題帶下方）
CB  = Inches(7.10)   # content bottom（頁碼上方）
CH  = CB - CT        # ≈ 5.68"（可用內容高度）
PNY = Inches(7.18)   # 頁碼 y 座標
```

### 標題帶（header 函式）
- 背景色塊：y=0, h=1.30"，淺藍灰（#F2F8F8）
- 左側色條：x=0, w=0.20", h=1.30"，TEAL
- 主標題：y=0.12, size=26pt, bold, TEAL
- 橫線：y=0.78, thickness=1.5pt, TEAL
- 副標題：y=0.82, size=14pt, MUTED
- **重要**：不使用全高側條，避免與內容框重疊

### 色盤
| 名稱       | RGB hex  | 用途           |
|------------|----------|----------------|
| BG         | #FAF8F4  | 投影片底色     |
| TEAL       | #1A6B7A  | 主題色（標題、強調） |
| GREEN      | #2E6B3A  | 第二強調色     |
| AMBER      | #C8780A  | 第三強調色     |
| PURPLE     | #7A3A8A  | 第四強調色     |
| PANEL      | #EEF6F7  | 淡藍說明框底色 |
| COVER_BG   | #081E24  | 封面深色背景   |

### 無重疊佈局原則
1. 多行框高度用算式：`BH = (CH - 間距總和) / 行數`，不手動估算
2. Slide 15 等有「主題詞 + 底部統整框」的頁面，統整框 y = CT + n×BH + (n-1)×GAP + 額外間距
3. 各框水平方向保留 ≥ 0.15" 間距
4. 頁碼 (pnum) 不需背景，直接疊在最後一行框上方無妨

### 課文全讀函式（full_read）
```python
def full_read(s, accent, para_label, text_lines):
    TW = Inches(12.65); TX = Inches(0.35)
    rect(s, TX, CT, TW, CH, RGBColor(0xF4,0xFB,0xFC), radius=12000)
    rect(s, TX, CT, Inches(0.14), CH, accent)
    txt(s, para_label, TX+Inches(0.26), CT+Inches(0.12), Inches(3.0), Inches(0.40), 14, accent, bold=True)
    mltxt(s, text_lines, TX+Inches(0.26), CT+Inches(0.58), TW-Inches(0.42), CH-Inches(0.65), 16, DARK, ls=1.68)
```
- `text_lines`：一字不差的完整段落，每段一個字串，長段落自動換行
- 字級 16pt，行距 1.68，可容納約 350 字於單頁

### 已完成的 PPT 腳本
| 腳本 | 課文 | 輸出檔 | 投影片數 |
|------|------|--------|---------|
| make_ppt_empty_city.py | 空城計（羅貫中） | 空城計.pptx | — |
| make_ppt_chabuduo.py | 差不多先生傳（胡適） | 差不多先生傳.pptx | 18 |
| make_ppt_bird.py | 鳥（梁實秋） | 鳥.pptx | 15 |
| make_ppt_sport_spirit.py | 運動家的風度（羅家倫） | 運動家的風度.pptx | — |
| make_ppt_water_god.py | 水神的指引 | 水神的指引.pptx | — |

---

## 網站架構規則

**TEXTS_DATA 唯一來源：`js/main.js`**
- `pages/lessons.html` 讀取 `../js/main.js` 顯示課文列表
- `pages/lesson.html` 有內聯副本，不作為修改目標

**新增課文時需同步三處（均在 lesson.html）：**
1. `LESSON_CONTENT['vol-no']`：課文全文
2. `LESSON_GUIDE['vol-no']`：作者介紹、段旨、寫作手法、主旨
3. `LESSON_VOCAB['vol-no']`：重要詞語（注音、出處句、釋義）

**已完成課文頁面（lesson.html 內有完整內容的課）：**
- 3-5 張釋之執法、3-6 蜜蜂的讚美、3-7 差不多先生傳、3-8 愛蓮說
- 4-6 運動家的風度、4-9 鳥、4-12 空城計（自學選文）
- 6-3 水神的指引

---

## 課程進度

- 國二（八年級）上學期：第三冊完成多課
- 國二（八年級）下學期：4-6 運動家的風度、4-9 鳥 已完成
- 國三（九年級）下學期：6-3 水神的指引 已完成
