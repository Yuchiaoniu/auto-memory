# grade4-english-tutor 專案設計規範

## 配色規範（重要）

- **避免使用粉紅色／玫瑰紅** (pink / rose / magenta)，包括卡片、封面、主題色等任何位置。
- **新單元的主色一律改用黃色系**：金黃、琥珀、暖黃皆可。
- 純鮮黃對白色文字對比不足，**黃底上的文字一律用深 navy** (`#2C3E50`)，不可用白色。

### 推薦黃色配色（已套用於 Unit 9）

```python
THEME    = RGBColor(0xFF, 0xC1, 0x07)  # 主黃 amber 500
THEME_D  = RGBColor(0xB0, 0x73, 0x09)  # 深琥珀（深色重點／文字）
LIGHT    = RGBColor(0xFF, 0xFA, 0xE5)  # 米色背景
CARD_BD  = RGBColor(0xF1, 0xDA, 0x9B)  # 暖棕邊
DARK     = RGBColor(0x2C, 0x3E, 0x50)  # navy slate（黃底文字色）
```

### 文字顏色對應表

| 背景 | 文字色 | 說明 |
|---|---|---|
| `THEME` 鮮黃 | `DARK` | 白字會看不清 |
| `THEME_D` 深琥珀 | `WHITE` | 深底用白字 |
| `LIGHT` 米色 | `DARK` 或 `THEME_D` | 內文與標題 |
| `WHITE` 白卡 | `DARK`／`THEME_D` | 鮮黃在白底看不到，點綴一律 `THEME_D` |

### 卡片邊框
- 白卡邊框用 `THEME_D`（深琥珀），不用 `THEME`（鮮黃在白底會看不到）。

## 其他既有單元色
- Unit 7 (What Time Is It?)：teal `#16A085` — 非粉紅系，沿用即可。
- 其他舊單元色若涉及粉紅／玫瑰紅，重做時須換成黃色或其他非粉紅色。
