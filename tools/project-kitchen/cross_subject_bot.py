#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cross_subject_bot.py v5.0 — 全面觀念追蹤版
# 修正清單：qtype欄位、pick_question/simulate_student改用DB、
#           META含qtype分布與趨勢、掌握科目降頻、題庫擴充至12題/科、
#           MASTERY_MIN_SEEN=3、GROUP_CONCAT排序修正

import requests, subprocess, time, datetime, os, json, random, tempfile, sqlite3

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
STATE_PATH = os.path.join(OUT_DIR, "practice_state.json")
LOG_PATH   = os.path.join(OUT_DIR, "practice_log.md")
DB_PATH    = os.path.join(OUT_DIR, "practice.db")
INTERVAL   = 600

TZ_TAIPEI = datetime.timezone(datetime.timedelta(hours=8))
def now_taipei():
    return datetime.datetime.now(TZ_TAIPEI)

SUBJECTS = ["finance", "psychology", "stats", "toefl"]
MASTERY_THRESHOLD = 0.7
MASTERY_MIN_SEEN  = 3  # 至少見過 3 次才能判定掌握

# qtype: definition / formula / application / vocabulary / grammar / reading / writing
QUESTIONS = {
    "finance": [
        {"q": "NPV 為正代表什麼？", "a": "計畫報酬率高於資金成本，應接受投資", "concept": "NPV", "chapter": "Ch04", "qtype": "definition", "lv": 1},
        {"q": "IRR 與 NPV 衝突時優先用哪個，為什麼？", "a": "NPV，因為 IRR 假設現金流以 IRR 再投資，而 NPV 假設以資金成本再投資，後者更合理", "concept": "IRR", "chapter": "Ch04", "qtype": "application", "lv": 2},
        {"q": "Duration 越長代表什麼風險？", "a": "利率敏感度越高，利率上升時價格跌幅越大", "concept": "Duration", "chapter": "Ch04", "qtype": "definition", "lv": 2},
        {"q": "回收期法（Payback Period）的最大缺點是什麼？", "a": "忽略回收期後的現金流，也不考慮貨幣時間價值", "concept": "PaybackPeriod", "chapter": "Ch04", "qtype": "application", "lv": 1},
        {"q": "股利折現模型（DDM）Gordon Growth Model 公式？", "a": "P₀ = D₁ / (r - g)，D₁為下期股利、r為要求報酬率、g為永久成長率", "concept": "DDM", "chapter": "Ch05", "qtype": "formula", "lv": 2},
        {"q": "Beta 係數衡量什麼？", "a": "個股相對於市場的系統性風險，β>1 波動大於市場", "concept": "Beta", "chapter": "Ch05", "qtype": "definition", "lv": 1},
        {"q": "CAPM 公式是什麼？", "a": "E(R) = Rf + β × (Rm - Rf)", "concept": "CAPM", "chapter": "Ch05", "qtype": "formula", "lv": 2},
        {"q": "WACC 是什麼，公式如何計算？", "a": "加權平均資金成本；WACC = Wd×Kd×(1-t) + We×Ke", "concept": "WACC", "chapter": "Ch05", "qtype": "formula", "lv": 2},
        {"q": "系統性風險與非系統性風險的區別？", "a": "系統性：無法分散，影響整體市場；非系統性：可透過分散投資消除", "concept": "RiskTypes", "chapter": "Ch05", "qtype": "definition", "lv": 1},
        {"q": "P/E 比率高代表什麼？", "a": "市場對公司未來成長期望高，或股價相對獲利被高估", "concept": "PERatio", "chapter": "Ch06", "qtype": "application", "lv": 1},
        {"q": "財務槓桿（Financial Leverage）如何影響 EPS？", "a": "獲利好時放大 EPS，獲利差時放大虧損，增加股東風險", "concept": "FinLeverage", "chapter": "Ch06", "qtype": "application", "lv": 2},
        {"q": "債券殖利率與價格的關係？", "a": "反向關係：殖利率上升→債券價格下跌；殖利率下降→價格上漲", "concept": "BondYield", "chapter": "Ch06", "qtype": "definition", "lv": 1},
    ],
    "psychology": [
        {"q": "基本歸因謬誤（FAE）是什麼？", "a": "過度強調他人行為的內在因素（個性），忽略外在情境的影響", "concept": "FAE", "chapter": "Ch06", "qtype": "definition", "lv": 1},
        {"q": "認知失調（Cognitive Dissonance）是什麼？", "a": "同時持有相互矛盾的信念或行為時的心理不適，個體設法減少不一致", "concept": "CognitiveDiss", "chapter": "Ch06", "qtype": "definition", "lv": 1},
        {"q": "確認偏誤（Confirmation Bias）指什麼？", "a": "傾向尋找、詮釋與既有信念一致的資訊，忽視反駁證據", "concept": "ConfirmBias", "chapter": "Ch07", "qtype": "definition", "lv": 1},
        {"q": "從眾效應（Bandwagon Effect）的核心機制？", "a": "個體跟隨多數人行為，即使與自身判斷相違，受社會認同驅動", "concept": "Bandwagon", "chapter": "Ch07", "qtype": "definition", "lv": 1},
        {"q": "可得性捷思（Availability Heuristic）如何影響判斷？", "a": "以容易想到的例子估計機率，導致高估生動或近期事件的頻率", "concept": "AvailHeuristic", "chapter": "Ch08", "qtype": "application", "lv": 2},
        {"q": "錨定效應（Anchoring）如何影響決策？", "a": "最初接收的數字成為判斷基準，後續估計向錨點靠攏，難以完全調整", "concept": "Anchoring", "chapter": "Ch08", "qtype": "application", "lv": 2},
        {"q": "自我效能感（Self-efficacy）由哪四個來源決定？", "a": "過去成功經驗、替代性學習（觀察他人）、言語說服、生理/情緒狀態", "concept": "SelfEfficacy", "chapter": "Ch08", "qtype": "definition", "lv": 2},
        {"q": "過度自信偏誤（Overconfidence Bias）在投資中的表現？", "a": "高估預測準確性，交易過度頻繁，低估風險", "concept": "Overconfidence", "chapter": "Ch09", "qtype": "application", "lv": 2},
        {"q": "古典制約（Classical Conditioning）vs. 操作制約（Operant Conditioning）的差別？", "a": "古典：中性刺激與非制約刺激配對產生反應；操作：行為因結果（獎懲）而增減", "concept": "Conditioning", "chapter": "Ch09", "qtype": "definition", "lv": 2},
        {"q": "馬斯洛需求層次（Maslow's Hierarchy）由低至高五層是什麼？", "a": "生理→安全→社會歸屬→尊重→自我實現", "concept": "Maslow", "chapter": "Ch10", "qtype": "definition", "lv": 1},
        {"q": "認知負荷理論（Cognitive Load Theory）核心主張？", "a": "工作記憶容量有限，學習設計應降低外在認知負荷，釋放資源給內在學習", "concept": "CognLoad", "chapter": "Ch10", "qtype": "definition", "lv": 2},
        {"q": "自我決定理論（Self-Determination Theory）三大基本需求是什麼？", "a": "自主性（Autonomy）、能力感（Competence）、歸屬感（Relatedness）", "concept": "SDT", "chapter": "Ch10", "qtype": "definition", "lv": 2},
    ],
    "stats": [
        {"q": "p-value < 0.05 代表什麼？", "a": "在 5% 顯著水準下拒絕虛無假說（H₀）", "concept": "pValue", "chapter": "Ch08", "qtype": "definition", "lv": 1},
        {"q": "Type I 與 Type II Error 各代表什麼？", "a": "Type I（α）：拒絕真的 H₀（偽陽性）；Type II（β）：未拒絕假的 H₀（偽陰性）", "concept": "ErrorTypes", "chapter": "Ch08", "qtype": "definition", "lv": 1},
        {"q": "統計檢定力（Power）是什麼，如何提升？", "a": "正確拒絕假 H₀ 的機率（1-β）；增加樣本數、提升顯著水準 α 或增大效果量", "concept": "TestPower", "chapter": "Ch08", "qtype": "definition", "lv": 2},
        {"q": "中央極限定理（CLT）的核心含義？", "a": "母體不論任何分配，只要樣本數夠大（n≥30），樣本平均數的抽樣分配趨近常態", "concept": "CLT", "chapter": "Ch09", "qtype": "definition", "lv": 2},
        {"q": "95% 信賴區間的正確解讀是什麼？", "a": "以相同方法重複取樣 100 次，約 95 次建立的區間會包含母體參數（不是單一區間有 95% 機率）", "concept": "CI", "chapter": "Ch09", "qtype": "application", "lv": 2},
        {"q": "何時用 t 檢定，何時用 z 檢定？", "a": "母體標準差 σ 已知→z 檢定；σ 未知用樣本 s 估計→t 檢定（實務幾乎都用 t）", "concept": "tVsZ", "chapter": "Ch10", "qtype": "application", "lv": 2},
        {"q": "單尾檢定 vs 雙尾檢定的選擇依據？", "a": "對研究方向有明確假設（只關注一邊）→單尾；僅知道有差異、不確定方向→雙尾", "concept": "OneTwoTail", "chapter": "Ch10", "qtype": "application", "lv": 2},
        {"q": "效果量（Effect Size）與統計顯著性的差別？", "a": "統計顯著性受樣本數影響（n大就容易顯著）；效果量反映實際差異大小，不受n影響", "concept": "EffectSize", "chapter": "Ch10", "qtype": "application", "lv": 2},
        {"q": "迴歸的 R² 代表什麼？", "a": "自變數能解釋應變數總變異的比例，0–1 之間，越高模型解釋力越強", "concept": "R2", "chapter": "Ch11", "qtype": "definition", "lv": 1},
        {"q": "相關不等於因果的經典反例是什麼？", "a": "冰淇淋銷量與溺水率呈正相關，但原因是第三變數（夏天/高溫），非直接因果", "concept": "CorrVsCause", "chapter": "Ch11", "qtype": "application", "lv": 1},
        {"q": "ANOVA（變異數分析）的用途是什麼？", "a": "同時比較三組或以上的平均數是否有差異，避免多次 t 檢定累積型一錯誤", "concept": "ANOVA", "chapter": "Ch12", "qtype": "definition", "lv": 2},
        {"q": "抽樣偏誤（Sampling Bias）有哪些常見類型？", "a": "選擇偏誤、非回應偏誤、存活者偏誤、自我選擇偏誤", "concept": "SamplingBias", "chapter": "Ch11", "qtype": "definition", "lv": 2},
    ],
    "toefl": [
        {"q": "Vocabulary: 'ubiquitous' means?", "a": "Found everywhere; present in all places at the same time", "concept": "vocab-ubiquitous", "chapter": "VocabAdv", "qtype": "vocabulary", "lv": 1},
        {"q": "Vocabulary: 'ephemeral' means?", "a": "Lasting for a very short time; transitory", "concept": "vocab-ephemeral", "chapter": "VocabAdv", "qtype": "vocabulary", "lv": 1},
        {"q": "Vocabulary: 'ambiguous' means?", "a": "Open to more than one interpretation; unclear or uncertain", "concept": "vocab-ambiguous", "chapter": "VocabAdv", "qtype": "vocabulary", "lv": 1},
        {"q": "Vocabulary: 'indigenous' means?", "a": "Originating or occurring naturally in a particular place; native", "concept": "vocab-indigenous", "chapter": "VocabAdv", "qtype": "vocabulary", "lv": 1},
        {"q": "Vocabulary: 'albeit' means?", "a": "Although; even though (used to introduce a concession)", "concept": "vocab-albeit", "chapter": "VocabConn", "qtype": "vocabulary", "lv": 2},
        {"q": "Vocabulary: 'nevertheless' signals what in a sentence?", "a": "Contrast/concession — despite what was just said, the following is still true", "concept": "vocab-nevertheless", "chapter": "VocabConn", "qtype": "vocabulary", "lv": 2},
        {"q": "Grammar: 'She don't like it' — what is wrong?", "a": "Third-person singular requires 'doesn't', not 'don't'", "concept": "grammar-3rdPerson", "chapter": "Grammar", "qtype": "grammar", "lv": 1},
        {"q": "Grammar: When do you use the subjunctive mood? Give an example.", "a": "For hypothetical/contrary-to-fact conditions: 'If I were you...' (not 'was')", "concept": "grammar-subjunctive", "chapter": "Grammar", "qtype": "grammar", "lv": 2},
        {"q": "Reading skill: what is 'inference'?", "a": "Drawing a conclusion not explicitly stated in the text, using context clues and logic", "concept": "reading-inference", "chapter": "ReadingSkills", "qtype": "reading", "lv": 2},
        {"q": "Reading skill: how do you identify the main idea of a passage?", "a": "Look for the topic sentence (often first/last of paragraph) and what most details support", "concept": "reading-mainidea", "chapter": "ReadingSkills", "qtype": "reading", "lv": 1},
        {"q": "Writing: what makes a strong thesis statement?", "a": "It states a specific, arguable claim (not a fact) and signals the essay's direction", "concept": "writing-thesis", "chapter": "WritingSkills", "qtype": "writing", "lv": 2},
        {"q": "Vocabulary: 'coalesce' means?", "a": "To come together to form one mass or whole; to merge or unite", "concept": "vocab-coalesce", "chapter": "VocabAdv", "qtype": "vocabulary", "lv": 2},
    ],
}


# ── DB 操作 ──────────────────────────────────────────────────────────────────

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            iteration INTEGER,
            ts        TEXT,
            subject   TEXT,
            chapter   TEXT,
            concept   TEXT,
            qtype     TEXT,
            lv        INTEGER,
            correct   INTEGER,
            is_intro  INTEGER DEFAULT 0
        )
    """)
    for col in ["qtype TEXT", "is_intro INTEGER DEFAULT 0"]:
        try:
            con.execute(f"ALTER TABLE answers ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
    con.commit()
    con.close()


def record_answer(iteration, subject, question, correct, is_intro=False):
    ts = now_taipei().strftime("%Y-%m-%d %H:%M:%S")
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO answers (iteration, ts, subject, chapter, concept, qtype, lv, correct, is_intro) VALUES (?,?,?,?,?,?,?,?,?)",
        (iteration, ts, subject, question["chapter"], question["concept"],
         question.get("qtype", ""), question["lv"], int(correct), int(is_intro)),
    )
    con.commit()
    con.close()


def query_concept_stats():
    """從 DB 查詢每個觀念的統計。
    seen = 排除首次介紹（is_intro=1）的正式測試次數；acc 只計正式測試。
    total_seen = 含 intro 的全部接觸次數（用於判斷是否已介紹過）。
    """
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("""
        SELECT subject, concept, chapter, qtype, lv,
               COUNT(*) as total_seen,
               SUM(CASE WHEN is_intro IS NULL OR is_intro=0 THEN 1 ELSE 0 END) as seen,
               SUM(CASE WHEN is_intro IS NULL OR is_intro=0 THEN correct ELSE 0 END) as hits,
               GROUP_CONCAT(CASE WHEN is_intro IS NULL OR is_intro=0 THEN correct END, ',') as history
        FROM (SELECT * FROM answers ORDER BY iteration ASC)
        GROUP BY subject, concept
    """).fetchall()
    con.close()
    result = {}
    for subject, concept, chapter, qtype, lv, total_seen, seen, hits, history in rows:
        clean_hist = [x for x in (history or "").split(",") if x != "None" and x != ""]
        recent = [int(x) for x in clean_hist[-3:]] if clean_hist else []
        result.setdefault(subject, {})[concept] = {
            "chapter": chapter, "qtype": qtype or "", "lv": lv,
            "total_seen": total_seen,
            "seen": seen, "hits": hits,
            "acc": hits / seen if seen > 0 else 0.0,
            "recent": recent,
        }
    return result


def query_qtype_stats(db_stats):
    """從已查好的 db_stats 彙整各 qtype 的整體正確率。"""
    qt = {}
    for concepts in db_stats.values():
        for d in concepts.values():
            t = d.get("qtype") or "unknown"
            if t not in qt:
                qt[t] = {"seen": 0, "hits": 0}
            qt[t]["seen"] += d["seen"]
            qt[t]["hits"] += d["hits"]
    return qt


# ── State ────────────────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_PATH):
        s = json.load(open(STATE_PATH, encoding="utf-8"))
        for subj in SUBJECTS:
            if subj not in s["subjects"]:
                s["subjects"][subj] = {"asked": 0, "correct": 0, "acc": 0.0, "streak": 0}
        if "round_robin_idx" not in s:
            s["round_robin_idx"] = s.get("iteration", 0)
        return s
    return {
        "iteration": 0,
        "round_robin_idx": 0,
        "subjects": {s: {"asked": 0, "correct": 0, "acc": 0.0, "streak": 0} for s in SUBJECTS},
    }


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ── 選題與模擬 ────────────────────────────────────────────────────────────────

def is_mastered(c_data):
    return c_data["seen"] >= MASTERY_MIN_SEEN and c_data["acc"] >= MASTERY_THRESHOLD


def subject_mastery_rate(subject, db_stats):
    subj_db = db_stats.get(subject, {})
    total = len(QUESTIONS[subject])
    mastered = sum(1 for d in subj_db.values() if is_mastered(d))
    return mastered / total if total > 0 else 0.0


def pick_subject(state, db_stats):
    """Round-robin + 兩個保護機制：掌握率≥80% 降頻、同科連推不超過 2 次。"""
    last = state.get("last_subjects", [])
    for _ in range(len(SUBJECTS) * 2):
        idx = state["round_robin_idx"] % len(SUBJECTS)
        state["round_robin_idx"] += 1
        subject = SUBJECTS[idx]
        rate = subject_mastery_rate(subject, db_stats)
        if rate >= 0.8 and random.random() >= 0.4:
            continue
        if last[-2:] == [subject, subject]:  # 連推緩衝：同科連出不超過 2 輪
            continue
        state["last_subjects"] = (last + [subject])[-6:]
        return subject
    subject = SUBJECTS[state["round_robin_idx"] % len(SUBJECTS)]
    state["last_subjects"] = (last + [subject])[-6:]
    return subject


def pick_question(subject, db_stats):
    """
    優先層（依序）：
    1. unseen     — 從未介紹過的觀念（total_seen=0）
    2. intro_done — 已介紹過但尚未正式測試（seen=0）
    3. weak       — 正式測試 acc<60%，非掌握
    4. unconfirmed— seen<3 且 acc=100%，需二次確認
    5. other      — 其餘非掌握
    6. fallback   — 全部題目
    額外：15% 機率直接抽 unconfirmed，確保不被 unseen 永遠排在前面。
    """
    subj_db = db_stats.get(subject, {})

    unseen      = [q for q in QUESTIONS[subject] if q["concept"] not in subj_db]
    intro_done  = [q for q in QUESTIONS[subject]
                   if q["concept"] in subj_db
                   and subj_db[q["concept"]]["total_seen"] > 0
                   and subj_db[q["concept"]]["seen"] == 0]
    weak        = [q for q in QUESTIONS[subject]
                   if q["concept"] in subj_db
                   and subj_db[q["concept"]]["seen"] > 0
                   and not is_mastered(subj_db[q["concept"]])
                   and subj_db[q["concept"]]["acc"] < 0.6]
    unconfirmed = [q for q in QUESTIONS[subject]
                   if q["concept"] in subj_db
                   and subj_db[q["concept"]]["seen"] > 0
                   and not is_mastered(subj_db[q["concept"]])
                   and subj_db[q["concept"]]["acc"] == 1.0]
    other       = [q for q in QUESTIONS[subject]
                   if q["concept"] not in subj_db
                   or not is_mastered(subj_db[q["concept"]])]

    if unconfirmed and random.random() < 0.15:
        pool = unconfirmed
    else:
        pool = unseen or intro_done or weak or unconfirmed or other or QUESTIONS[subject]
    return random.choice(pool)


def simulate_student(question, subject, db_stats):
    """根據 DB 中該觀念的歷史正確率（含近期趨勢加權）模擬作答。"""
    subj_db = db_stats.get(subject, {})
    c_data  = subj_db.get(question["concept"])
    if c_data and c_data["seen"] > 0:
        base_acc = c_data["acc"]
        if len(c_data["recent"]) >= 2:
            recent_acc = sum(c_data["recent"][-2:]) / 2
            base_acc   = 0.6 * base_acc + 0.4 * recent_acc
    else:
        base_acc = 0.3
    return random.random() < (0.25 + base_acc * 0.55)


def update_state(subject, correct, state):
    subj = state["subjects"][subject]
    subj["asked"]   += 1
    subj["correct"] += int(correct)
    subj["streak"]   = subj["streak"] + 1 if correct else 0
    subj["acc"]      = subj["correct"] / subj["asked"]


# ── 觀念推導 ──────────────────────────────────────────────────────────────────

def mental_model_inference(db_stats):
    lines = []
    for subject in SUBJECTS:
        subj_db  = db_stats.get(subject, {})
        if not subj_db:
            continue
        mastered  = [c for c, d in subj_db.items() if is_mastered(d)]
        weak      = [c for c, d in subj_db.items() if d["acc"] < 0.6 and not is_mastered(d)]
        improving = [c for c, d in subj_db.items()
                     if len(d["recent"]) >= 2 and sum(d["recent"][-2:]) == 2 and not is_mastered(d)]
        unseen_n  = len(QUESTIONS[subject]) - len(subj_db)
        parts = []
        if weak:
            parts.append(f"弱點：{' / '.join(weak)}")
        if improving:
            parts.append(f"進步中：{' / '.join(improving)}")
        if mastered:
            parts.append(f"已掌握：{' / '.join(mastered)}")
        if unseen_n > 0:
            parts.append(f"未探索 {unseen_n} 個觀念")
        if parts:
            lines.append(f"[{subject}] " + "，".join(parts))
    return "\n".join(lines) if lines else "觀念覆蓋建立中。"


# ── META ──────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """你是跨科目學習系統的雙軌分析師。

系統核心目標：辨識使用者對每個科目、每個章節、每個觀念的掌握強弱——
強的觀念停止推送，弱的觀念深度分析原因，追蹤觀念類型（definition/formula/application等）而非只記答對答錯次數。

每 5 輪進行一次 META 分析：

Track A【系統自檢】依序回答六個問題（每題一行）：
Q1 觀念推送邏輯是否有盲點（值得優化的地方）
Q2 哪些機制正在有效運作（值得保留的優點）
Q3 有無覆蓋缺口或邏輯死角（未注意到的問題）
Q4 推送是否過量或過雜（降低認知負荷的可能）
Q5 30 輪後、100 輪後系統會是什麼狀態（跨時間宏觀視角）
Q6 各機制評分 0–10（需有比較基準）

Track B【觀念建模】：根據觀念接觸記錄與題型分布，分析使用者當前認知狀態：
- 哪類題型（definition/formula/application）系統性偏弱？
- 弱點觀念是孤立個案還是跨科共同盲點（如：都是應用型題目偏弱）？
- 近期趨勢：哪些觀念在進步，哪些持續弱？

輸出格式：
Q1｜結論
Q2｜結論
Q3｜結論
Q4｜結論
Q5｜結論
Q6｜結論
觀念｜{2–3 句分析，必須提及題型層面的規律}
決策｜{一句}
待辦｜• item1 • item2 • item3

總長不超過 400 字，繁體中文，精準有力。"""


def build_meta_prompt(n, db_stats, infer):
    # 觀念明細
    concepts_block = ""
    for subject in SUBJECTS:
        c = db_stats.get(subject, {})
        if c:
            rows = [f"  {k}({v['qtype']}): seen={v['seen']} acc={v['acc']*100:.0f}% recent={v['recent']}"
                    for k, v in c.items()]
            concepts_block += f"{subject}:\n" + "\n".join(rows) + "\n"

    # 題型彙整
    qt = query_qtype_stats(db_stats)
    qt_block = "\n".join(
        f"  {t}: {d['hits']}/{d['seen']} ({d['hits']/d['seen']*100:.0f}%)"
        for t, d in sorted(qt.items()) if d["seen"] > 0
    )

    return (
        f"迭代 #{n} META 分析\n\n"
        f"## 各科觀念覆蓋狀態（qtype/seen/acc/recent3）\n{concepts_block}\n"
        f"## 題型正確率分布\n{qt_block}\n\n"
        f"## 觀念推導摘要\n{infer}\n\n"
        f"請執行雙軌分析（Track A 六問自檢 + Track B 觀念建模，重點分析題型層面的規律）。"
    )


def call_claude_meta(prompt_text):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".sys", delete=False, dir="/tmp") as sf:
        sf.write(SYSTEM_PROMPT); sys_path = sf.name
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".usr", delete=False, dir="/tmp") as uf:
        uf.write(prompt_text); usr_path = uf.name
    script = f"""source /home/yuchi/.nvm/nvm.sh 2>/dev/null
SYSP=$(cat {sys_path})
cat {usr_path} | claude --print --dangerously-skip-permissions --system-prompt "$SYSP"
"""
    try:
        result = subprocess.run(
            ["bash", "-l"], input=script, capture_output=True, text=True, timeout=180,
            env={**os.environ, "HOME": "/home/yuchi", "USER": "yuchi"},
        )
        out = result.stdout.strip()
        return out if out else f"[無輸出 rc={result.returncode}: {result.stderr[:150]}]"
    except subprocess.TimeoutExpired:
        return "[逾時 180s]"
    except Exception as e:
        return f"[錯誤: {e}]"
    finally:
        for p in [sys_path, usr_path]:
            try: os.unlink(p)
            except: pass


# ── Telegram & Log ────────────────────────────────────────────────────────────

def send(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text[:4000]}, timeout=15,
        )
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[Telegram] {e}"); return False


def append_log(text):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(text)


# ── 主迭代 ────────────────────────────────────────────────────────────────────

def run_iteration(state):
    db_stats = query_concept_stats()
    state["iteration"] += 1
    n       = state["iteration"]
    subject = pick_subject(state, db_stats)
    q       = pick_question(subject, db_stats)

    # 首次介紹：此觀念在本輪前從未出現過（total_seen=0）
    is_intro = q["concept"] not in db_stats.get(subject, {})

    correct = simulate_student(q, subject, db_stats)
    update_state(subject, correct, state)
    record_answer(n, subject, q, correct, is_intro=is_intro)
    save_state(state)

    # DB 更新後重新查（含本輪新記錄）
    db_stats = query_concept_stats()
    infer    = mental_model_inference(db_stats)
    is_meta  = (n % 5 == 0)
    ts       = now_taipei().strftime("%Y-%m-%d %H:%M:%S (台北)")

    # 連續答錯提示：最近 2 次都錯（recent[-2:]==[0,0]）
    c_data = db_stats.get(subject, {}).get(q["concept"])
    needs_hint = (
        c_data is not None
        and len(c_data["recent"]) >= 2
        and c_data["recent"][-2:] == [0, 0]
    )
    hint_line = f"\n💡 連續兩次答錯，正確答案：{q['a']}" if needs_hint else ""
    intro_tag = " [初次介紹]" if is_intro else ""

    log = (f"## 迭代 #{n} | {ts} | {subject} / {q['concept']} ({q['qtype']}){intro_tag}"
           f"{'  | ★META' if is_meta else ''}\n\n"
           f"題目：{q['q']}\n正解：{q['a']}\n模擬作答：{'答對' if correct else '答錯'}{hint_line}\n\n"
           f"觀念快照：\n{infer}\n\n")

    if is_meta:
        qt = query_qtype_stats(db_stats)
        qt_line = " | ".join(f"{t}:{d['hits']}/{d['seen']}" for t, d in sorted(qt.items()) if d["seen"] > 0)
        log += f"### META #{n} 資料\n題型: {qt_line}\n\n"

    log += "---\n\n"
    append_log(log)

    # Telegram：只在 META 輪發送觸發訊號；一般迭代不發送
    if is_meta:
        covered = sum(1 for s in db_stats.values() for d in s.values() if d["total_seen"] > 0)
        return (f"★ META #{n} | {now_taipei().strftime('%H:%M')} 台北\n"
                f"覆蓋 {covered}/48 觀念\n"
                f"請在 Claude Code 說「跑 META」")
    return None


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    init_db()
    if not os.path.exists(LOG_PATH):
        append_log(f"# 跨科目學習系統 v5.2\n\n啟動：{now_taipei()}\n\n---\n\n")
    state = load_state()
    send(f"跨科目學習 Bot v5.2 啟動\n"
         f"已累積 {state['iteration']} 輪，繼續迭代。\n"
         f"題庫：{sum(len(v) for v in QUESTIONS.values())} 題 / {len(QUESTIONS)} 科\n"
         f"v5.2 新功能：is_intro 標記、連續錯誤提示、unconfirmed 15% 早抽、Telegram 只推 META 輪")
    try:
        tg = run_iteration(state)
        if tg:
            send(tg)
        print(f"[{now_taipei().strftime('%H:%M:%S')} 台北] 迭代 #{state['iteration']} 完成")
    except Exception as e:
        send(f"迭代錯誤：{e}"); print(f"迭代錯誤：{e}")
    while True:
        time.sleep(INTERVAL)
        try:
            tg = run_iteration(state)
            if tg:
                send(tg)
            print(f"[{now_taipei().strftime('%H:%M:%S')} 台北] 迭代 #{state['iteration']} 完成")
        except Exception as e:
            err = f"迭代錯誤：{e}"; print(err); send(err)


if __name__ == "__main__":
    import sys as _sys, json as _json
    _cmd = _sys.argv[1] if len(_sys.argv) > 1 else "daemon"

    if _cmd == "pick":
        os.makedirs(OUT_DIR, exist_ok=True)
        init_db()
        _state = load_state()
        _db = query_concept_stats()
        _subj = pick_subject(_state, _db)
        _q = pick_question(_subj, _db)
        print(_json.dumps({
            "subject": _subj,
            "concept": _q["concept"],
            "question": _q["q"],
            "answer": _q["a"],
            "chapter": _q["chapter"],
            "qtype": _q["qtype"],
            "iteration": _state["iteration"] + 1
        }, ensure_ascii=False))

    elif _cmd == "record":
        # 用法：python bot.py record <輪次> <科目> <觀念> <答對:1|答錯:0>
        _n, _subj, _concept, _correct = int(_sys.argv[2]), _sys.argv[3], _sys.argv[4], int(_sys.argv[5])
        os.makedirs(OUT_DIR, exist_ok=True)
        init_db()
        _q = next((qq for qq in QUESTIONS[_subj] if qq["concept"] == _concept), None)
        if _q:
            _db = query_concept_stats()
            _is_intro = _concept not in _db.get(_subj, {})
            record_answer(_n, _subj, _q, bool(_correct), is_intro=_is_intro)
            _state = load_state()
            _state["iteration"] = _n
            save_state(_state)
            _db = query_concept_stats()
            print(_json.dumps(_db.get(_subj, {}).get(_concept, {}), ensure_ascii=False))

    elif _cmd == "stats":
        os.makedirs(OUT_DIR, exist_ok=True)
        init_db()
        _db = query_concept_stats()
        _summary = {}
        for _subj, _concepts in _db.items():
            _summary[_subj] = {
                "total": len(QUESTIONS[_subj]),
                "seen": sum(1 for d in _concepts.values() if d["total_seen"] > 0),
                "mastered": sum(1 for d in _concepts.values() if is_mastered(d)),
                "weak": sum(1 for d in _concepts.values() if d["seen"] > 0 and not is_mastered(d) and d["acc"] < 0.6)
            }
        print(_json.dumps(_summary, ensure_ascii=False))

    elif _cmd == "send":
        _msg = _sys.argv[2] if len(_sys.argv) > 2 else "（空訊息）"
        send(_msg)
        print("sent")

    else:
        main()
