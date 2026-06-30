# 跨科目學習系統迭代改進腳本

每次執行代表一輪完整的分析與改進。
工作階段結束後自動關閉，不累積記憶。

---

## 第一步：讀取目前系統狀態

執行以下指令取得 GCP 最新資料：

```powershell
. ~/.claude/env.ps1
$SSH_OPTS = @("-i", $SSH_KEY, "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes")
& $SSH_BIN @SSH_OPTS "${SSH_USER}@35.227.93.38" "python3 -c \"
import json, sqlite3, datetime
state = json.load(open('/home/yuchi/cognitive-tests/practice_state.json'))
db = sqlite3.connect('/home/yuchi/cognitive-tests/practice.db')
rows = db.execute('SELECT subject, concept, is_correct, answered_at FROM answers ORDER BY answered_at DESC LIMIT 20').fetchall()
print('=== 目前進度 ===')
print(f'已完成輪次：{state.get(chr(105)+chr(116)+chr(101)+chr(114)+chr(97)+chr(116)+chr(105)+chr(111)+chr(110), 0)}')
concepts = {}
for r in rows:
    k = f'{r[0]}/{r[1]}'
    if k not in concepts: concepts[k] = []
    concepts[k].append(r[2])
print('=== 最近 20 筆答題（科目/觀念：對/錯紀錄）===')
for k,v in concepts.items():
    acc = sum(v)/len(v)
    print(f'{k}: {[\"對\" if x else \"錯\" for x in v]} 正確率 {acc:.0%}')
\""
```

---

## 第二步：分析弱點

請呼叫 `Skill(openspec-explore)`，把以下問題作為探索起點：

1. 哪些觀念最近連續答錯，需要優先加強？
2. 哪個科目被推送的比例不均衡？
3. 出題邏輯或題目本身有沒有可以改進的地方？
4. 這次改動之後有沒有可能出問題？

---

## 第三步：決定一個改進項目

根據分析，選擇**一件**最有價值的事情來做：
- 不要同時改多個地方
- 優先選對學習效果影響最大的改進
- 如果現在沒有明顯問題，可以跳過本輪

---

## 第四步：實作改進

修改 `C:\Users\yuchi\.claude\tools\project-kitchen\cross_subject_bot.py`。

**Telegram 推送內容的硬性規定：**
- 只能用白話中文
- 不能出現英文縮寫（例如 acc、qtype、MCQ 等）
- 不能出現程式碼變數名稱
- 不能出現自創的專業術語

---

## 第五步：部署

```powershell
cd "C:\Users\yuchi\.claude\tools\project-kitchen"
git add cross_subject_bot.py
git commit -m "迭代改進：<一句話說明改了什麼>"
git push origin main
```

然後通知 GCP 更新：

```powershell
. ~/.claude/env.ps1
$SSH_OPTS = @("-i", $SSH_KEY, "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes")
& $SSH_BIN @SSH_OPTS "${SSH_USER}@35.227.93.38" "cd /home/yuchi/.claude/tools/project-kitchen && git reset --hard origin/main && pkill -f cross_subject_bot.py; sleep 1; nohup python3 -u /home/yuchi/.claude/tools/project-kitchen/cross_subject_bot.py >> /home/yuchi/cognitive-tests/bot.log 2>&1 </dev/null &"
```

---

## 注意事項

- 每輪只做一件事，做完就結束
- 不要為了「有改動」而修改，沒有明顯問題時可以跳過
- 部署後確認機器人有正常啟動（ps aux 查看）
