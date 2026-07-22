# -*- coding: utf-8 -*-
"""arcus 統一自適應機制：思考原則與語言偏好共用一套學習骨架，加觸發閘門與機械掃描。

兩種自適應規則寫在同一支模組：
  kind='principle' → 設計思考原則，存 arcus_user_model.jsonl
  kind='style'     → 語言偏好，存 arcus_style_model.jsonl

三部分：
  A 學習骨架：add / hit / list / promote / sweep，用離散計數，不做梯度、不存浮點權重。
  B 觸發閘門：每條規則帶觸發條件，比對這一輪情境，只注入命中的少數幾條，切斷注入膨脹。
  C 機械掃描：語言偏好裡能純比對字樣的部分（本研究→此研究、絕對詞標記），
             走生成時／生成後確定性處理，不佔系統提示。

2026-07-23 五點弱點修正：
  弱點一 逐字去重 → 正規化＋字集重疊（Jaccard）合併，換句話講同一件事也能對上、累積證據。
  弱點二 機械替換 → hard_subs 供串流每段硬套（不靠引擎自律）；絕對詞改到生成前提示預防。
  弱點三 只增不減 → _sweep 淘汰暫定噪音、降級久未命中的 live，接通原本的死碼 retired。
  弱點四 永久判決 → 升級改用淨證據（evidence-contradicted），打臉不再永久封殺；新增 exception 一次性例外。
  弱點五 軟注入   → 靠提示端墊高地板（自審＋強語氣），本模組保留可讀語意的注入介面。
"""
import io, os, re, json, datetime

_STORE = {
    'principle': '/home/yuchi/.claude/arcus_user_model.jsonl',
    'style':     '/home/yuchi/.claude/arcus_style_model.jsonl',
}
_ID_PREFIX = {'principle': 'p', 'style': 's'}
_PROMOTE_NET = 2          # 淨證據（evidence-contradicted）達此值 → tentative 升 live
_TENTATIVE_TTL_DAYS = 30  # 暫定規則超過此天數又證據不足／淨值非正 → 退役 retired
_LIVE_IDLE_DAYS = 120     # live 規則超過此天數完全沒被再觀察 → 降回 tentative（保守、避免churn）
_SIM_WHEN = 0.65          # 去重：when 字集重疊係數門檻
_SIM_THEN = 0.55          # 去重：then 字集重疊係數門檻


# ============ A 學習骨架（兩種 kind 共用）============

def _now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def _age_days(ts):
    """從時間戳字串算到現在的天數；解析失敗當作 0（不誤淘汰）。"""
    try:
        t = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        return (datetime.datetime.now() - t).total_seconds() / 86400.0
    except Exception:
        return 0.0

def _store_path(kind):
    if kind not in _STORE:
        raise ValueError('未知 kind：%s' % kind)
    return _STORE[kind]

def _load(kind):
    items = []
    try:
        with io.open(_store_path(kind), encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return items

def _sweep(items):
    """確定性淘汰／降級（弱點三）：
      暫定太久又（證據不足或淨值非正）→ 退役 retired；
      live 太久完全沒被再觀察 → 降回 tentative。
    回傳是否有變動。"""
    changed = False
    for it in items:
        st = it.get('status')
        ev = int(it.get('evidence', 0))
        cn = int(it.get('contradicted', 0))
        age = _age_days(it.get('last', it.get('born', '')))
        if st == 'tentative':
            if age > _TENTATIVE_TTL_DAYS and (ev < _PROMOTE_NET or (ev - cn) <= 0):
                it['status'] = 'retired'
                it['retired_at'] = _now()
                changed = True
        elif st == 'live':
            if age > _LIVE_IDLE_DAYS:
                it['status'] = 'tentative'
                it['demoted_at'] = _now()
                changed = True
    return changed

def _load_swept(kind):
    """載入並就地淘汰／降級；有變動才落盤。所有寫入與檢視路徑都走這個。"""
    items = _load(kind)
    if _sweep(items):
        _save(kind, items)
    return items

def _save(kind, items):
    p = _store_path(kind)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + '\n')
    os.replace(tmp, p)

def _next_id(kind, items):
    mx = 0
    for it in items:
        try:
            n = int(str(it.get('id', '')).split('_')[-1])
            if n > mx:
                mx = n
        except Exception:
            pass
    return '%s_%d' % (_ID_PREFIX[kind], mx + 1)

def _promote(it):
    """升級改用淨證據（弱點四）：evidence-contradicted 達門檻即 live。
    打臉不再永久封殺——之後淨值重新達標仍可再上線。"""
    net = int(it.get('evidence', 0)) - int(it.get('contradicted', 0))
    if net >= _PROMOTE_NET:
        it['status'] = 'live'


# ---- 去重：正規化＋字集重疊（弱點一）----

_PUNCT = re.compile(r'[，。、；：！？,.;:!?\s（）()「」『』【】\[\]{}"\'`~—\-…·]+')

def _norm_text(s):
    return _PUNCT.sub('', (s or '').strip().lower())

def _tokens(s):
    """中文以字為粒度、英數以詞為粒度，取集合，用來估兩句是否講同一件事。"""
    s = s or ''
    zh = re.findall(r'[一-鿿]', s)
    en = re.findall(r'[a-zA-Z0-9]+', s.lower())
    return set(zh) | set(en)

def _overlap(a, b):
    """重疊係數（交集／較短集合）：比 Jaccard 更能容忍換句話塞入的虛詞把分母灌大。"""
    sa, sb = _tokens(a), _tokens(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / float(min(len(sa), len(sb)))

def _similar(a_when, a_then, b_when, b_then):
    """兩條規則是否算同一條：正規化後完全相同，或 when 與 then 兩句重疊係數雙雙過門檻。
    句子太短（字集<3）時只認正規化相同，避免短句誤合併；要求兩句都相似，擋掉不同規則誤併。"""
    if _norm_text(a_when) == _norm_text(b_when) and _norm_text(a_then) == _norm_text(b_then):
        return True
    if len(_tokens(a_when)) < 3 or len(_tokens(b_when)) < 3:
        return False
    return _overlap(a_when, b_when) >= _SIM_WHEN and _overlap(a_then, b_then) >= _SIM_THEN

def _norm_triggers(triggers):
    triggers = triggers or {}
    return {
        'keywords': [k.strip() for k in (triggers.get('keywords') or []) if k and str(k).strip()],
        'mode': (triggers.get('mode') or 'any').strip(),   # any / chat / article
    }

def rule_add(kind, when, then, because=None, scope=None, triggers=None):
    """收料：寫入一條候選規則，初始 tentative、evidence=1。
    語意上算同一條的既有規則（弱點一：換句話也算）改為再觀察一次、累積證據。"""
    when = (when or '').strip()
    then = (then or '').strip()
    if not when or not then:
        return {'ok': False, 'error': 'when 與 then 皆不可空'}
    items = _load_swept(kind)
    for it in items:
        if it.get('status') == 'retired':
            continue
        if _similar(when, then, it.get('when', ''), it.get('then', '')):
            it['evidence'] = int(it.get('evidence', 0)) + 1
            _promote(it)
            it['last'] = _now()
            _save(kind, items)
            return {'ok': True, 'id': it['id'], 'status': it['status'], 'deduped': True, 'record': it}
    rec = {
        'id': _next_id(kind, items),
        'when': when, 'then': then,
        'because': (because or '').strip(),
        'scope': (scope or '全域').strip(),
        'triggers': _norm_triggers(triggers),
        'evidence': 1, 'contradicted': 0, 'exceptions': 0, 'status': 'tentative',
        'born': _now(), 'last': _now(),
    }
    items.append(rec)
    _save(kind, items)
    return {'ok': True, 'id': rec['id'], 'status': rec['status'], 'record': rec}

def rule_hit(kind, rid, what):
    """固化／打臉／例外：
      confirm    → evidence+1，淨值達門檻即升 live；
      contradict → contradicted+1、當下降回 tentative，但不永久封殺（弱點四）；
      exception  → 一次性例外，不算打臉、不影響升級，只記次數供檢視（弱點四：分辨「這次例外」與「這條錯」）。"""
    items = _load_swept(kind)
    hit = None
    for it in items:
        if it.get('id') == rid:
            hit = it
            break
    if hit is None:
        return {'ok': False, 'error': '找不到規則 %s' % rid}
    if what == 'confirm':
        hit['evidence'] = int(hit.get('evidence', 0)) + 1
        _promote(hit)
    elif what == 'contradict':
        hit['contradicted'] = int(hit.get('contradicted', 0)) + 1
        hit['status'] = 'tentative'
    elif what == 'exception':
        hit['exceptions'] = int(hit.get('exceptions', 0)) + 1
    else:
        return {'ok': False, 'error': 'what 必須是 confirm／contradict／exception'}
    hit['last'] = _now()
    _save(kind, items)
    return {'ok': True, 'id': rid, 'status': hit['status'],
            'evidence': hit.get('evidence', 0), 'contradicted': hit.get('contradicted', 0),
            'exceptions': hit.get('exceptions', 0)}

def rule_list(kind, status=None):
    """列出規則供檢視；status 可填 live／tentative／retired，不填給全部。列出前先跑一次淘汰。"""
    items = _load_swept(kind)
    if status:
        items = [it for it in items if it.get('status') == status]
    return {'ok': True, 'count': len(items), 'rules': items}


# ============ B 觸發閘門（腳本管挑：只注入命中的少數幾條）============

def _match(it, context_text, mode):
    """確定性比對：模式相符（或規則不限模式）且情境含任一關鍵字（或規則沒設關鍵字），才算命中。"""
    trig = it.get('triggers') or {}
    tmode = trig.get('mode', 'any')
    if tmode != 'any' and mode and tmode != mode:
        return False
    kws = trig.get('keywords') or []
    if kws:
        ctx = context_text or ''
        if not any(k in ctx for k in kws):
            return False
    return True

def context_block(kind, context_text='', mode=None, header=None, limit=20):
    """把 live 且觸發命中的規則做成注入文字。無命中回空字串，注入量跟「這輪相關幾條」走、不跟總量走。
    走 _load_swept，讓純聊天回合也會定時淘汰／降級（弱點三），不必等到有人 add／hit。"""
    live = [it for it in _load_swept(kind) if it.get('status') == 'live']
    picked = [it for it in live if _match(it, context_text, mode)]
    if not picked:
        return ''
    picked = picked[-limit:]
    head = header or ('【已萃取的規則——命中就照做（這是你已確認過的偏好，優先於臨時直覺），'
                      '並附一句報備「依你〔id〕原則我做了X（不對就說一聲）」；'
                      '被更正就呼叫 rule_hit(kind,id,"contradict")，只是這次例外則用 "exception"】')
    lines = ['\n' + head]
    for it in picked:
        lines.append('- 〔%s｜%s〕當 %s → 偏好 %s（本質：%s）'
                     % (it.get('id'), it.get('scope', '全域'),
                        it.get('when'), it.get('then'), it.get('because', '')))
    return '\n'.join(lines) + '\n'


# ============ C 機械掃描（語言偏好，生成時／生成後確定性處理，不佔提示）============

_SUBS = [('本研究', '此研究'), ('本專案', '此專案')]
_ABSOLUTE = ['證明', '必然', '一定', '絕對', '完全', '永遠', '所有', '毫無']

def hard_subs(text):
    """只做確定性字詞替換，供串流每一段輸出前硬套（弱點二：不靠引擎記得呼叫）。
    串流事件每段是完整文字區塊、不是逐字，替換不會把詞切成兩半。回傳改後文字。"""
    fixed = text or ''
    for a, b in _SUBS:
        if a in fixed:
            fixed = fixed.replace(a, b)
    return fixed

def mechanical_scan(text):
    """對寫完的文字做確定性處理：安全詞直接替換、絕對詞只標記不改。
    回傳 {text 改後文字, substituted 已替換清單, absolute_flags 絕對詞旗標}。"""
    fixed = hard_subs(text)
    applied = []
    for a, b in _SUBS:
        c = (text or '').count(a)
        if c:
            applied.append({'from': a, 'to': b, 'count': c})
    flags = []
    for w in _ABSOLUTE:
        c = fixed.count(w)
        if c:
            flags.append({'word': w, 'count': c})
    return {'text': fixed, 'substituted': applied, 'absolute_flags': flags}
