#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
認知強化 Bot — 每 5 分鐘一輪迭代
行為科學框架：衡量 → 配置 → 獲取
認知科學核心：主動回憶 + 間隔重複
"""
import requests, json, time, datetime, os, random, sys, argparse

_cfg_path = os.path.expanduser("~/.claude/.telegram-config")
_cfg = {}
if os.path.exists(_cfg_path):
    with open(_cfg_path) as _f:
        for _line in _f:
            _k, _, _v = _line.strip().partition("=")
            _cfg[_k.strip()] = _v.strip()
TOKEN   = _cfg.get("TOKEN", "")
CHAT_ID = _cfg.get("CHAT_ID", "")
OUT_DIR = "/home/yuchi/cognitive-tests"
INTERVAL = 300  # 5 分鐘

# ── 題庫 ─────────────────────────────────────────────────────────────────────
QUESTIONS = {
    "finance": [
        {"q": "NPV 為正代表什麼？",           "a": "計畫報酬率高於資金成本，應接受投資", "lv": 1},
        {"q": "IRR 與 NPV 衝突時優先用哪個？", "a": "NPV，因再投資假設更合理",           "lv": 2},
        {"q": "Duration 越長代表什麼風險？",   "a": "利率敏感度越高，利率升時價格跌幅越大", "lv": 2},
        {"q": "股利折現模型假設什麼？",         "a": "股利以固定成長率 g 永久成長",         "lv": 2},
        {"q": "Beta 係數衡量什麼？",            "a": "個股相對於市場的系統性風險",          "lv": 1},
    ],
    "stats": [
        {"q": "p-value < 0.05 代表什麼？",     "a": "在 5% 顯著水準下拒絕虛無假說",        "lv": 1},
        {"q": "Type I Error 是什麼？",          "a": "拒絕真的虛無假說（偽陽性）",          "lv": 1},
        {"q": "中央極限定理核心含義？",         "a": "樣本數夠大時，樣本平均數趨近常態分配", "lv": 2},
        {"q": "信賴區間 95% 的意義？",          "a": "重複取樣 100 次，約 95 次區間包含母體參數", "lv": 2},
        {"q": "迴歸的 R² 代表什麼？",           "a": "自變數能解釋應變數變異的比例",         "lv": 2},
    ],
    "accounting": [
        {"q": "折舊的目的是什麼？",             "a": "將固定資產成本在使用年限內系統性分攤至各期費用", "lv": 1},
        {"q": "應收帳款周轉率公式？",           "a": "銷貨淨額 ÷ 平均應收帳款",             "lv": 1},
        {"q": "FIFO vs LIFO 通膨時獲利差異？", "a": "FIFO 獲利較高，LIFO 獲利較低",        "lv": 2},
        {"q": "權責發生制與現金基礎差異？",     "a": "權責：費用於發生時認列；現金：收付時才認列", "lv": 1},
        {"q": "流動比率低於 1 代表什麼？",      "a": "短期負債大於流動資產，短期償債能力有疑慮", "lv": 2},
    ],
}

WRONG_POOL = {
    "finance":    ["需要更多資訊才能判斷", "代表資金成本過高", "應等待更好時機"],
    "stats":      ["樣本數不足", "信賴區間需要調整", "需要更多實驗"],
    "accounting": ["記錄資產減少", "反映市值變化", "屬於現金流量調整"],
}

# ── 認知模型狀態 ──────────────────────────────────────────────────────────────
model = {
    "iteration": 0,
    "phase":     "measure",
    "subjects":  {s: {"asked": 0, "correct": 0, "acc": 0.0, "diff": 1.0, "streak": 0}
                  for s in QUESTIONS},
    "history":   [],
}

def send(text):
    url  = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(url, json=data, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[Telegram error] {e}")
        return False

def pick_subject():
    """選最弱科目（最低正確率），首輪則輪流選"""
    asked = [(s, d) for s, d in model["subjects"].items() if d["asked"] > 0]
    if not asked:
        return list(QUESTIONS.keys())[model["iteration"] % 3]
    return min(asked, key=lambda x: x[1]["acc"])[0]

def pick_question(subject):
    diff = int(model["subjects"][subject]["diff"])
    pool = [q for q in QUESTIONS[subject] if q["lv"] <= max(1, diff)]
    return random.choice(pool or QUESTIONS[subject])

def simulate_student(question, subject):
    """模擬學生作答：正確率受當前 acc 影響"""
    acc = model["subjects"][subject]["acc"]
    hit = random.random() < (0.25 + acc * 0.55)
    if hit:
        return question["a"], True
    return random.choice(WRONG_POOL[subject]), False

def update_model(subject, correct):
    m = model["subjects"][subject]
    m["asked"] += 1
    if correct:
        m["correct"] += 1
        m["streak"]  += 1
    else:
        m["streak"] = 0
    m["acc"] = m["correct"] / m["asked"]
    # 難度自適應
    if m["acc"] > 0.75 and m["streak"] >= 2:
        m["diff"] = min(2.0, m["diff"] + 0.25)
    elif m["acc"] < 0.45:
        m["diff"] = max(1.0, m["diff"] - 0.2)

def phase_label():
    phases = {"measure": "衡量", "configure": "配置", "acquire": "獲取"}
    return phases[model["phase"]]

def update_phase():
    i = model["iteration"]
    if i < 4:
        model["phase"] = "measure"
    elif i < 8:
        model["phase"] = "configure"
    else:
        model["phase"] = "acquire"

def run_iteration():
    model["iteration"] += 1
    update_phase()
    now = datetime.datetime.now()
    ts  = now.strftime("%Y%m%d_%H%M%S")

    subject  = pick_subject()
    question = pick_question(subject)
    answer, correct = simulate_student(question, subject)
    update_model(subject, correct)

    # 分析者評估
    insights = []
    for s, d in model["subjects"].items():
        if d["asked"] == 0:
            continue
        if d["acc"] < 0.5:
            insights.append(f"{s} 正確率 {d['acc']*100:.0f}%，建議加強基礎題型")
        elif d["acc"] < 0.75:
            insights.append(f"{s} 正確率 {d['acc']*100:.0f}%，可嘗試提升難度")
        else:
            insights.append(f"{s} 正確率 {d['acc']*100:.0f}%，已掌握，可推進下一科")

    phase_advice = {
        "measure":   "目標：取得各科基準正確率，不調整難度，純觀察。",
        "configure": "目標：依基準數據配置難度，優先強化正確率 < 60% 的科目。",
        "acquire":   "目標：間隔重複弱點題型，連續答對 3 題才升難度，強化長期記憶留存率。",
    }

    # 寫 md 記錄
    bar = lambda a: "█" * int(a * 5) + "░" * (5 - int(a * 5))
    md = f"""# 認知分析迭代 #{model['iteration']}
時間：{now.strftime('%Y-%m-%d %H:%M:%S')}
階段：{phase_label()}（{model['phase']}）

## 本輪測試

| 項目 | 內容 |
|------|------|
| 科目 | {subject} |
| 題目 | {question['q']} |
| 難度 | Lv.{question['lv']} |

### 角色：學生（使用者）
**作答**：{answer}
**結果**：{'正確' if correct else '錯誤'}
**正解**：{question['a']}

### 角色：分析者
{chr(10).join('- ' + i for i in insights)}

**本階段策略**：{phase_advice[model['phase']]}

## 各科認知模型快照

| 科目 | 已測 | 正確 | 正確率 | 難度 | 連勝 |
|------|------|------|--------|------|------|
"""
    for s, d in model["subjects"].items():
        md += f"| {s} | {d['asked']} | {d['correct']} | {d['acc']*100:.0f}% | Lv.{d['diff']:.1f} | {d['streak']} |\n"

    md_path = os.path.join(OUT_DIR, f"iter_{ts}.md")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    # Telegram 訊息（精簡版）
    result_mark = "答對" if correct else "答錯"
    acc_lines = ""
    for s, d in model["subjects"].items():
        if d["asked"] > 0:
            acc_lines += f"\n  {s}: {bar(d['acc'])} {d['acc']*100:.0f}%"

    tg = (
        f"[迭代 #{model['iteration']}] 階段：{phase_label()}\n\n"
        f"科目：{subject}\n"
        f"題目：{question['q']}\n\n"
        f"學生答：{answer}\n"
        f"結果：{result_mark}\n"
        f"正解：{question['a']}\n\n"
        f"各科正確率：{acc_lines}\n\n"
        f"分析：{insights[-1] if insights else '建立基準中'}\n"
        f"記錄：iter_{ts}.md"
    )
    return tg, md_path

def main(test_mode=False):
    send(
        "認知強化 Bot 已啟動\n\n"
        "框架：衡量 → 配置 → 獲取\n"
        "核心：主動回憶 + 間隔重複\n\n"
        "每 5 分鐘一輪迭代，同時建立 md 記錄檔。\n"
        "Bot 扮演學生作答，分析者評估並更新認知模型。"
    )

    if test_mode:
        # 單次迭代測試
        msg, path = run_iteration()
        ok = send(msg)
        print(f"Test iteration done. md={path}, send_ok={ok}")
        return

    while True:
        time.sleep(INTERVAL)
        try:
            msg, path = run_iteration()
            send(msg)
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] iter #{model['iteration']} → {path}")
        except Exception as e:
            err = f"迭代錯誤：{e}"
            print(err)
            send(err)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="單次迭代測試模式")
    args = parser.parse_args()
    main(test_mode=args.test)
