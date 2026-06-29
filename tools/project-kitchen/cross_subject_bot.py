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
INTERVAL   = 300

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

# 每道題目的錯誤選項（3 個），每個附帶心智模型標籤
# model 欄位說明該錯誤選項對應的常見錯誤心智模型
WRONG_OPTIONS = {
    # ── finance ──────────────────────────────────────────────────────────────
    "NPV": [
        {"text": "計畫在未來某時點一定會回本（只要回收期為正）", "model": "PaybackPeriod混淆"},
        {"text": "計畫的 IRR 大於零（IRR與NPV正負相同）", "model": "IRR與NPV混淆"},
        {"text": "計畫的現金流入總額大於流出總額（不考慮折現）", "model": "忽略時間價值"},
    ],
    "IRR": [
        {"text": "IRR，因為它不依賴折現率假設，更客觀中立", "model": "IRR客觀性迷思"},
        {"text": "NPV，因為 NPV 數值永遠大於 IRR", "model": "數字大小混淆"},
        {"text": "兩者相同，衝突情況在理論上不可能發生", "model": "IRR-NPV必然一致迷思"},
    ],
    "Duration": [
        {"text": "違約風險越高，發行人倒帳機率越大", "model": "Duration=信用風險混淆"},
        {"text": "到期日越遠，總還款金額越多", "model": "Duration=到期日混淆"},
        {"text": "流動性越差，在市場上越難賣出", "model": "Duration=流動性風險混淆"},
    ],
    "PaybackPeriod": [
        {"text": "計算複雜，需設定折現率，容易出錯", "model": "回收期法與NPV缺點混淆"},
        {"text": "無法比較不同規模的投資計畫", "model": "IRR限制與回收期混淆"},
        {"text": "只能用於單期現金流，無法處理多期", "model": "使用範圍誤解"},
    ],
    "DDM": [
        {"text": "P₀ = D₀ / (r - g)，D₀為本期股利", "model": "D0與D1混淆"},
        {"text": "P₀ = D₁ / (g - r)，分母順序相反", "model": "分母順序顛倒"},
        {"text": "P₀ = D₁ × (r + g)，把除法誤記為乘法", "model": "乘除運算錯誤"},
    ],
    "Beta": [
        {"text": "個股的總風險，包含可分散與不可分散的部分", "model": "Beta=總風險混淆"},
        {"text": "個股相對於同業的獲利能力比較", "model": "Beta=獲利能力混淆"},
        {"text": "市場整體波動的絕對數值", "model": "Beta=市場絕對波動混淆"},
    ],
    "CAPM": [
        {"text": "E(R) = Rf + β × Rm（未減去無風險利率）", "model": "遺漏風險溢酬調整"},
        {"text": "E(R) = β × (Rm - Rf)（遺漏無風險利率基礎）", "model": "遺漏無風險基礎"},
        {"text": "E(R) = Rm + β × (Rm - Rf)（把Rm誤記為基礎）", "model": "基礎利率搞混"},
    ],
    "WACC": [
        {"text": "加權平均資金成本；WACC = Wd×Kd + We×Ke（忽略稅盾）", "model": "忽略債務稅盾"},
        {"text": "各資金來源成本的簡單平均，與資本結構無關", "model": "加權vs簡單平均混淆"},
        {"text": "加權平均資金成本；WACC = Wd×Ke + We×Kd（成本配對搞反）", "model": "成本配對顛倒"},
    ],
    "RiskTypes": [
        {"text": "系統性：影響特定公司；非系統性：影響整體市場（定義互換）", "model": "兩者定義顛倒"},
        {"text": "兩者差異在規模：系統性金額大，非系統性金額小", "model": "規模vs分散能力混淆"},
        {"text": "系統性風險可透過買保險消除，非系統性無法避免", "model": "可消除性搞反"},
    ],
    "PERatio": [
        {"text": "公司目前獲利能力很強，本期每股盈餘最高", "model": "P/E高=高EPS混淆"},
        {"text": "公司股價絕對值高，適合短期套利", "model": "本益比vs股價絕對值混淆"},
        {"text": "公司負債比例偏低，財務結構穩健", "model": "本益比與財務槓桿混淆"},
    ],
    "FinLeverage": [
        {"text": "財務槓桿永遠使 EPS 上升，因為借貸成本低於股權成本", "model": "槓桿單向放大迷思"},
        {"text": "財務槓桿使總資產增加，但 EPS 不受影響", "model": "EPS免疫迷思"},
        {"text": "財務槓桿降低風險，因為分散了資金來源", "model": "槓桿=降低風險誤解"},
    ],
    "BondYield": [
        {"text": "正向關係：殖利率越高，債券越吸引人，價格越高", "model": "正向關係混淆"},
        {"text": "兩者無關：殖利率由信用評等決定，與市價獨立", "model": "獨立性迷思"},
        {"text": "反向關係，但只適用短期債券，長期債券無此規律", "model": "適用範圍誤解"},
    ],
    # ── psychology ───────────────────────────────────────────────────────────
    "FAE": [
        {"text": "過度強調自身行為的外在因素，忽略個人特質", "model": "FAE方向反轉（自利偏誤混淆）"},
        {"text": "在自我評估時，高估自己的能力和表現", "model": "過度自信混淆"},
        {"text": "傾向把他人行為歸因於情境，忽略個人性格", "model": "正確定義顛倒"},
    ],
    "CognitiveDiss": [
        {"text": "因為記憶不準確，導致對事件的認知出現偏差", "model": "認知失調=記憶錯誤混淆"},
        {"text": "對某問題缺乏足夠訊息，導致無法做出正確判斷", "model": "認知不足混淆"},
        {"text": "長期累積的心理壓力導致決策能力下降", "model": "認知負荷混淆"},
    ],
    "ConfirmBias": [
        {"text": "傾向相信第一次接觸的資訊，無論後續資訊如何", "model": "錨定效應混淆"},
        {"text": "傾向模仿他人行為和意見以獲得社會接納", "model": "從眾效應混淆"},
        {"text": "傾向誇大自身能力和正確率，忽視自身錯誤", "model": "過度自信混淆"},
    ],
    "Bandwagon": [
        {"text": "看到多數人選擇某項目，推斷它必定品質更好（可得性推論）", "model": "品質推論混淆"},
        {"text": "因為害怕社會懲罰而改變行為，而非出於認同", "model": "威脅vs認同機制混淆"},
        {"text": "長期接觸主流觀點後，逐漸內化成自身真實信念", "model": "從眾vs真正態度改變混淆"},
    ],
    "AvailHeuristic": [
        {"text": "依據統計機率精確估計未來事件可能性（系統性評估）", "model": "理性估計混淆"},
        {"text": "傾向高估自己接觸過的資訊的重要性", "model": "確認偏誤混淆"},
        {"text": "根據事件的重要程度（而非生動性）估計機率", "model": "重要性vs生動性混淆"},
    ],
    "Anchoring": [
        {"text": "對最近接收的資訊記憶最深，以最後看到的數字為基準（近因效應）", "model": "近因效應混淆"},
        {"text": "傾向選擇中間選項，避免極端值（折衷效應）", "model": "折衷效應混淆"},
        {"text": "每次決策都從空白開始，完全不受前次資訊影響", "model": "錨定免疫迷思"},
    ],
    "SelfEfficacy": [
        {"text": "智力、努力程度、學習環境、社會支持", "model": "一般因素混淆"},
        {"text": "過去成功、現在表現、未來預測、他人評價（混合時間維度）", "model": "時間維度混淆"},
        {"text": "內在動機、外在動機、認知能力、情緒穩定度（SDT因素混淆）", "model": "SDT混淆"},
    ],
    "Overconfidence": [
        {"text": "對市場走勢過於悲觀，傾向持有過多現金不投入市場", "model": "過度自信反向"},
        {"text": "因為害怕錯過漲幅，跟隨他人買入熱門股", "model": "從眾/FOMO混淆"},
        {"text": "嚴格遵守紀律，拒絕超出自身能力範圍的投資", "model": "紀律交易混淆"},
    ],
    "Conditioning": [
        {"text": "古典：透過獎勵強化行為；操作：透過配對刺激建立反射（兩者定義對調）", "model": "定義互換"},
        {"text": "兩者相同，都是透過重複練習建立習慣，只是動物種類不同", "model": "無差別混淆"},
        {"text": "古典制約是有意識的學習；操作制約是無意識的自動反應", "model": "意識性顛倒"},
    ],
    "Maslow": [
        {"text": "生理→社會歸屬→安全→尊重→自我實現（安全與社會歸屬互換）", "model": "安全與歸屬順序錯誤"},
        {"text": "安全→生理→尊重→社會歸屬→自我實現（生理與安全顛倒）", "model": "生理與安全顛倒"},
        {"text": "尊重→自我實現→生理→安全→社會歸屬（完全錯誤順序）", "model": "完全重排"},
    ],
    "CognLoad": [
        {"text": "多元感官同時輸入（視覺+聽覺）能成倍增加學習效率", "model": "多媒體=倍增迷思"},
        {"text": "大腦學習沒有容量限制，只有動機和注意力是瓶頸", "model": "容量無限迷思"},
        {"text": "重複練習能自動降低認知負荷，無需特別設計學習順序", "model": "自動化混淆"},
    ],
    "SDT": [
        {"text": "外在獎勵（Reward）、能力感（Competence）、歸屬感（Relatedness）", "model": "自主性換成外在獎勵"},
        {"text": "自主性（Autonomy）、智力（Intelligence）、歸屬感（Relatedness）", "model": "能力感換成智力"},
        {"text": "安全感（Security）、能力感（Competence）、自主性（Autonomy）", "model": "歸屬感換成安全感"},
    ],
    # ── stats ─────────────────────────────────────────────────────────────────
    "pValue": [
        {"text": "H₀ 為假的機率是 5%，研究結論正確的機率高達 95%", "model": "p值=H₀為假的機率誤解"},
        {"text": "結果的重要性（effect size）超過 95% 的研究", "model": "顯著=重要混淆"},
        {"text": "再做 100 次實驗，至少 95 次會得到同樣的結果", "model": "複製率誤解"},
    ],
    "ErrorTypes": [
        {"text": "Type I：未拒絕假的 H₀；Type II：拒絕真的 H₀（兩者互換）", "model": "兩者定義互換"},
        {"text": "Type I：樣本不具代表性；Type II：測量工具不準確", "model": "操作定義混淆"},
        {"text": "Type I 和 Type II 是同一種錯誤的不同嚴重程度", "model": "非獨立類別誤解"},
    ],
    "TestPower": [
        {"text": "研究結果能被複製的機率；需提升測量工具精確度", "model": "複製率混淆"},
        {"text": "正確支持 H₀ 的機率（1-α）；需縮小樣本以降低雜訊", "model": "定義與方向錯誤"},
        {"text": "研究設計的嚴謹程度；透過盲化和隨機化提升", "model": "效度混淆"},
    ],
    "CLT": [
        {"text": "樣本數夠大後，樣本本身的分配會趨近常態（非抽樣分配）", "model": "樣本vs抽樣分配混淆"},
        {"text": "只要母體是常態分配，任何樣本的平均數抽樣分配也是常態", "model": "母體限制誤解"},
        {"text": "樣本數越大，樣本平均數越接近 0（收斂目標誤解）", "model": "收斂到零迷思"},
    ],
    "CI": [
        {"text": "這個具體區間有 95% 的機率包含母體參數", "model": "單一區間機率誤解（最常見錯誤）"},
        {"text": "母體參數有 95% 的機率落在這個區間內（母體參數隨機化）", "model": "母體參數隨機化誤解"},
        {"text": "樣本中 95% 的觀測值落在這個區間內", "model": "樣本vs參數混淆"},
    ],
    "tVsZ": [
        {"text": "樣本數 n<30 用 t 檢定；n≥30 用 z 檢定", "model": "樣本大小vs σ已知混淆"},
        {"text": "定性資料用 t 檢定；定量資料用 z 檢定", "model": "資料類型混淆"},
        {"text": "雙樣本比較用 t 檢定；單樣本假設用 z 檢定", "model": "樣本數量混淆"},
    ],
    "OneTwoTail": [
        {"text": "樣本數少用單尾（節省統計力），樣本數多用雙尾", "model": "樣本大小規則混淆"},
        {"text": "結果顯著後轉換成單尾以降低 p 值（合理化 p-hacking）", "model": "p-hacking合理化"},
        {"text": "單尾代表高度確定，雙尾代表完全不確定（二元誤解）", "model": "二元誤解"},
    ],
    "EffectSize": [
        {"text": "效果量是統計顯著性的延伸，p 值越小效果量必定越大", "model": "p值=效果量混淆"},
        {"text": "兩者測量同一件事，效果量只是另一種表達顯著性的方式", "model": "冗餘迷思"},
        {"text": "統計顯著說明結果可複製，效果量說明結果是否重要", "model": "各自意義混淆"},
    ],
    "R2": [
        {"text": "自變數與應變數的相關係數（r 而非 r²）", "model": "r與R²混淆"},
        {"text": "模型預測準確率：R²=0.8 代表預測 80% 的情況都正確", "model": "R²=準確率混淆"},
        {"text": "參數的 p 值，R² 越高代表統計越顯著", "model": "R²=顯著性混淆"},
    ],
    "CorrVsCause": [
        {"text": "兩變數相關時必定存在因果關係，只是方向未確定", "model": "相關即因果"},
        {"text": "相關係數越高，因果關係越強（r=0.9 代表高度因果）", "model": "係數大小=因果強度"},
        {"text": "只有實驗設計才能回答因果，觀察性研究永遠無法觸及因果問題", "model": "過度否定觀察性研究"},
    ],
    "ANOVA": [
        {"text": "比較兩組以上的變異數，確認各組離散程度是否相同", "model": "ANOVA名稱字面誤解"},
        {"text": "分析一組資料的內部變異，找出極端值和異常點", "model": "單組分析誤解"},
        {"text": "在兩組比較中取代 t 檢定，計算結果相同但步驟更簡單", "model": "ANOVA替代t迷思"},
    ],
    "SamplingBias": [
        {"text": "測量誤差、記憶偏誤、報告偏誤、研究者偏誤", "model": "抽樣偏誤vs測量誤差混淆"},
        {"text": "選擇偏誤、樣本數不足偏誤、計算誤差、分析偏誤", "model": "把非偏誤項目納入"},
        {"text": "只有選擇偏誤才算抽樣偏誤，其他都是分析層面問題", "model": "過度縮窄定義"},
    ],
    # ── toefl ─────────────────────────────────────────────────────────────────
    "vocab-ubiquitous": [
        {"text": "Occurring very rarely; found only in specific remote locations", "model": "Opposite meaning"},
        {"text": "Extremely large in size or scope; massive and imposing", "model": "Sounds big → everywhere confusion"},
        {"text": "Quickly spreading or growing; tending to multiply rapidly", "model": "Spreading ≈ everywhere confusion"},
    ],
    "vocab-ephemeral": [
        {"text": "Existing only in a spiritual or non-physical form; otherworldly", "model": "ephem- sounds like ethereal"},
        {"text": "Gradually appearing or emerging over a long period of time", "model": "Emergence misread"},
        {"text": "Highly emotional and easily excited; volatile in mood", "model": "Emotional instability confusion"},
    ],
    "vocab-ambiguous": [
        {"text": "Having extreme or strong opinions; showing definite, clear intent", "model": "Opposite: clarity confusion"},
        {"text": "Being friendly and sociable; having an easygoing personality", "model": "ambi- sounds friendly"},
        {"text": "Capable of using both hands equally well; adaptable to many tasks", "model": "ambi- → ambidextrous confusion"},
    ],
    "vocab-indigenous": [
        {"text": "Introduced from another region; foreign but well-adapted to local conditions", "model": "Imported = established locally"},
        {"text": "Belonging to an earlier, more primitive stage of development; ancient", "model": "Primitive/ancient conflation"},
        {"text": "Endangered and near extinction in its natural habitat", "model": "Indigenous = threatened species confusion"},
    ],
    "vocab-albeit": [
        {"text": "As a result; consequently (signals cause-effect)", "model": "Concession confused with causative"},
        {"text": "In addition to; furthermore (signals addition)", "model": "Concession confused with addition"},
        {"text": "Only if; provided that (signals condition)", "model": "Concession confused with condition"},
    ],
    "vocab-nevertheless": [
        {"text": "Sequence — indicating the next step in a process or time order", "model": "Discourse marker confused: sequence"},
        {"text": "Elaboration — providing further detail for the previous point", "model": "Discourse marker confused: elaboration"},
        {"text": "Emphasis — strongly reinforcing the point just made in the same direction", "model": "Discourse marker confused: reinforcement"},
    ],
    "grammar-3rdPerson": [
        {"text": "The pronoun 'she' should be 'her' in this context (subject pronoun error)", "model": "Pronoun case confusion"},
        {"text": "'Don't' is informal; the error is register, not grammar ('does not' needed in writing)", "model": "Register vs. grammatical agreement"},
        {"text": "The object is missing; the sentence needs to specify what 'it' refers to", "model": "Reference vs. agreement error"},
    ],
    "grammar-subjunctive": [
        {"text": "For questions and negative sentences: 'Were she coming?' requires subjunctive", "model": "Question inversion confusion"},
        {"text": "For polite requests: 'I would like you come' uses subjunctive for politeness", "model": "Politeness/modal confusion"},
        {"text": "After 'have': 'I have been' is subjunctive because it describes completed actions", "model": "Perfect aspect confusion"},
    ],
    "reading-inference": [
        {"text": "Finding the exact definition of an unfamiliar word using surrounding context clues", "model": "Vocabulary from context ≠ inference"},
        {"text": "Identifying the stated main idea by finding the topic sentence in each paragraph", "model": "Main idea identification ≠ inference"},
        {"text": "Summarizing the author's argument by paraphrasing the key points from the text", "model": "Summary ≠ inference"},
    ],
    "reading-mainidea": [
        {"text": "Find the longest or most detailed sentence, as the author emphasizes the main idea most", "model": "Length = importance confusion"},
        {"text": "The first sentence of the entire passage always states the main idea explicitly", "model": "First-sentence rule overgeneralization"},
        {"text": "Identify the most frequently repeated word — it refers to the main idea", "model": "Word frequency = main idea confusion"},
    ],
    "writing-thesis": [
        {"text": "It summarizes all the key points the essay will cover, acting as a table of contents", "model": "Thesis = outline confusion"},
        {"text": "It states a well-known fact clearly and precisely to establish common ground", "model": "Thesis = fact confusion (most common)"},
        {"text": "It asks a thought-provoking question that the essay will explore without answering", "model": "Thesis = question confusion"},
    ],
    "vocab-coalesce": [
        {"text": "To break apart into many small pieces; to fragment or disperse", "model": "Opposite meaning"},
        {"text": "To heat and cool a substance to change its properties; to harden", "model": "coalesce sounds like coal → heat"},
        {"text": "To gradually disappear or fade away over time", "model": "Dissolution/vanishing confusion"},
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
    for col in ["qtype TEXT", "is_intro INTEGER DEFAULT 0",
                "options_json TEXT", "selected_option INTEGER",
                "source TEXT DEFAULT 'simulated'"]:
        try:
            con.execute(f"ALTER TABLE answers ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
    con.commit()
    con.close()


def record_answer(iteration, subject, question, correct, is_intro=False,
                  options_json=None, selected_option=None, source="simulated"):
    ts = now_taipei().strftime("%Y-%m-%d %H:%M:%S")
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO answers (iteration, ts, subject, chapter, concept, qtype, lv, correct, is_intro, options_json, selected_option, source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (iteration, ts, subject, question["chapter"], question["concept"],
         question.get("qtype", ""), question["lv"], int(correct), int(is_intro),
         options_json, selected_option, source),
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
    4. needs_more — 正式測試 1-2 次且 acc>=60%（尚未達到掌握門檻，需補足次數）
    5. unconfirmed— seen<3 且 acc=100%，需二次確認
    6. other      — 其餘非掌握
    7. fallback   — 全部題目
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
    needs_more  = [q for q in QUESTIONS[subject]
                   if q["concept"] in subj_db
                   and 0 < subj_db[q["concept"]]["seen"] < MASTERY_MIN_SEEN
                   and not is_mastered(subj_db[q["concept"]])
                   and subj_db[q["concept"]]["acc"] >= 0.6]
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
        pool = unseen or intro_done or weak or needs_more or unconfirmed or other or QUESTIONS[subject]
    return random.choice(pool)


def simulate_student(question, subject, db_stats):
    """根據 DB 中該觀念的歷史正確率（含近期趨勢加權）模擬作答。
    新觀念依難度分層：lv1→base_acc=0.45，lv2→base_acc=0.20（v36 修正）。
    """
    subj_db = db_stats.get(subject, {})
    c_data  = subj_db.get(question["concept"])
    if c_data and c_data["seen"] > 0:
        base_acc = c_data["acc"]
        if len(c_data["recent"]) >= 2:
            recent_acc = sum(c_data["recent"][-2:]) / 2
            base_acc   = 0.6 * base_acc + 0.4 * recent_acc
    else:
        base_acc = 0.45 if question.get("lv", 1) == 1 else 0.20
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


# ── 多選題（MCQ）支援 ─────────────────────────────────────────────────────────

def build_options(question):
    """
    組合四個選項（1 個正確 + 3 個錯誤），隨機洗牌後回傳。
    每個選項是 dict: {text, is_correct, model}
    """
    concept = question["concept"]
    wrongs  = WRONG_OPTIONS.get(concept, [
        {"text": "以上皆非", "model": "fallback"},
        {"text": "無法判斷", "model": "fallback"},
        {"text": "以上皆是", "model": "fallback"},
    ])[:3]
    options = [{"text": question["a"], "is_correct": True, "model": "correct"}]
    for w in wrongs:
        options.append({"text": w["text"], "is_correct": False, "model": w["model"]})
    random.shuffle(options)
    return options


def send_question_mcq(n, subject, question, options):
    """
    用 Telegram inline keyboard 傳送四選項題目。
    回傳 message_id（用於後續追蹤）。
    """
    labels = ["A", "B", "C", "D"]
    lines  = [f"【第{n}題 · {subject}/{question['concept']}】", "", question["q"], ""]
    for i, opt in enumerate(options):
        lines.append(f"{labels[i]}. {opt['text']}")
    text = "\n".join(lines)

    # inline_keyboard: 每個按鈕一行，callback_data = "A:1" (letter:is_correct)
    keyboard = [[{
        "text": labels[i],
        "callback_data": f"{labels[i]}:{1 if options[i]['is_correct'] else 0}"
    }] for i in range(4)]
    # 改為單行四個按鈕排列
    keyboard = [[
        {"text": labels[i], "callback_data": f"{labels[i]}:{1 if options[i]['is_correct'] else 0}"}
        for i in range(4)
    ]]

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text[:4000],
                "reply_markup": {"inline_keyboard": keyboard}
            },
            timeout=15,
        )
        result = r.json().get("result", {})
        return result.get("message_id")
    except Exception as e:
        print(f"[MCQ send error] {e}")
        return None


def get_tg_updates(offset=None, timeout=30):
    """長輪詢取得 Telegram 更新（含 callback_query）。"""
    params = {"timeout": timeout, "allowed_updates": ["callback_query"]}
    if offset is not None:
        params["offset"] = offset
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getUpdates",
            params=params, timeout=timeout + 5,
        )
        return r.json().get("result", [])
    except Exception as e:
        print(f"[getUpdates error] {e}")
        return []


def answer_callback(callback_id, correct):
    """回應 Telegram callback query，顯示結果通知。"""
    text = "✅ 答對了！" if correct else "❌ 答錯了"
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
            json={"callback_query_id": callback_id, "text": text, "show_alert": False},
            timeout=10,
        )
    except Exception as e:
        print(f"[answerCallback error] {e}")


def run_interactive():
    """
    互動式多選題模式：傳送題目→等使用者點選→記錄→下一題。
    每題最多等 600 秒，逾時視為略過。
    """
    os.makedirs(OUT_DIR, exist_ok=True)
    init_db()
    state  = load_state()
    offset = None
    pending = None  # {n, subject, q, options, options_json, is_intro, sent_ts, msg_id}

    send("🎯 互動式多選題模式啟動！每題請點選 A / B / C / D。")
    print(f"[{now_taipei().strftime('%H:%M:%S')}] 互動模式啟動")

    while True:
        # ── 取得 Telegram 更新 ──
        updates = get_tg_updates(offset=offset, timeout=10)
        for upd in updates:
            offset = upd["update_id"] + 1
            cb = upd.get("callback_query")
            if not cb or pending is None:
                continue
            # 解析使用者選擇
            data      = cb.get("callback_data", "A:0")
            letter, is_correct_str = data.split(":")
            correct   = bool(int(is_correct_str))
            sel_idx   = "ABCD".index(letter)
            sel_model = pending["options"][sel_idx]["model"]

            answer_callback(cb["id"], correct)

            # 送出結果說明
            correct_text = pending["q"]["a"]
            result_msg = (
                f"{'✅' if correct else '❌'} 選了 {letter}（{pending['options'][sel_idx]['text'][:60]}）\n"
                f"正確答案：{correct_text[:200]}"
            )
            if not correct:
                result_msg += f"\n心智模型標籤：{sel_model}"
            send(result_msg)

            record_answer(
                pending["n"], pending["subject"], pending["q"],
                correct, is_intro=pending["is_intro"],
                options_json=pending["options_json"],
                selected_option=sel_idx,
                source="interactive",
            )
            update_state(pending["subject"], correct, state)
            save_state(state)
            print(f"[{now_taipei().strftime('%H:%M:%S')}] #{pending['n']} {pending['subject']}/{pending['q']['concept']} → {'O' if correct else 'X'} (model={sel_model})")
            pending = None

        # ── 逾時未回答 → 略過 ──
        if pending is not None:
            elapsed = (now_taipei() - pending["sent_ts"]).total_seconds()
            if elapsed > 600:
                send(f"⏱ 逾時，略過：{pending['q']['concept']}\n正確答案：{pending['q']['a'][:200]}")
                record_answer(
                    pending["n"], pending["subject"], pending["q"],
                    False, is_intro=pending["is_intro"],
                    options_json=pending["options_json"],
                    selected_option=None,
                    source="interactive",
                )
                pending = None

        # ── 沒有待答題目 → 出下一題 ──
        if pending is None:
            db_stats = query_concept_stats()
            state["iteration"] += 1
            n       = state["iteration"]
            subject = pick_subject(state, db_stats)
            q       = pick_question(subject, db_stats)
            is_intro = q["concept"] not in db_stats.get(subject, {})
            options  = build_options(q)
            opts_json = json.dumps(
                [{"text": o["text"], "is_correct": o["is_correct"], "model": o["model"]} for o in options],
                ensure_ascii=False
            )
            msg_id = send_question_mcq(n, subject, q, options)
            pending = {
                "n": n, "subject": subject, "q": q,
                "options": options, "options_json": opts_json,
                "is_intro": is_intro,
                "sent_ts": now_taipei(), "msg_id": msg_id,
            }
            print(f"[{now_taipei().strftime('%H:%M:%S')}] 已送出 #{n} {subject}/{q['concept']}")

        import time as _t
        _t.sleep(3)


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
    _wd_con = sqlite3.connect(DB_PATH)
    _wd_ic = _wd_con.execute("SELECT COUNT(*) FROM answers WHERE source='interactive'").fetchone()[0]
    _wd_con.close()
    if _wd_ic == 0 and WRONG_OPTIONS:
        send("⚠️ Watchdog 警告：互動模式從未啟動，144 條心智模型標籤完全閒置。\n"
             "停止守護進程後，執行 python3 cross_subject_bot.py interactive 啟動互動模式。")
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
        for _ in range(2):
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
        _con_s = sqlite3.connect(DB_PATH)
        _ic = _con_s.execute("SELECT COUNT(*) FROM answers WHERE source='interactive'").fetchone()[0]
        _con_s.close()
        _summary = {}
        for _subj, _concepts in _db.items():
            _weak_names = [c for c, d in _concepts.items() if d["seen"] > 0 and not is_mastered(d) and d["acc"] < 0.6]
            _almost = [c for c, d in _concepts.items() if d["hits"] == 2 and not is_mastered(d)]
            _summary[_subj] = {
                "total": len(QUESTIONS[_subj]),
                "seen": sum(1 for d in _concepts.values() if d["total_seen"] > 0),
                "mastered": sum(1 for d in _concepts.values() if is_mastered(d)),
                "weak": len(_weak_names),
                "weak_names": _weak_names,
                "almost_mastered": _almost,
            }
        _summary["interactive_mode_status"] = (
            f"active（{_ic}筆）" if _ic > 0 else "never_started（所有心智模型標籤閒置）"
        )
        print(_json.dumps(_summary, ensure_ascii=False))

    elif _cmd == "send":
        _msg = _sys.argv[2] if len(_sys.argv) > 2 else "（空訊息）"
        send(_msg)
        print("sent")

    elif _cmd == "interactive":
        run_interactive()

    else:
        main()
