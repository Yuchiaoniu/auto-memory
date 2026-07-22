# -*- coding: utf-8 -*-
"""arcus 統一自適應機制：思考原則與語言偏好共用一套學習骨架，加觸發閘門與機械掃描。

兩種自適應規則寫在同一支模組：
  kind='principle' → 設計思考原則，存 arcus_user_model.jsonl
  kind='style'     → 語言偏好，存 arcus_style_model.jsonl

三部分：
  A 學習骨架：add / hit / list / promote，用離散計數，不做梯度、不存浮點權重。
  B 觸發閘門：每條規則帶觸發條件，比對這一輪情境，只注入命中的少數幾條，切斷注入膨脹。
  C 機械掃描：語言偏好裡能純比對字樣的部分（本研究→此研究、絕對詞標記），
             走生成後確定性掃描，不佔系統提示。
"""
import io, os, json, datetime

_STORE = {
    'principle': '/home/yuchi/.claude/arcus_user_model.jsonl',
    'style':     '/home/yuchi/.claude/arcus_style_model.jsonl',
}
_ID_PREFIX = {'principle': 'p', 'style': 's'}
_PROMOTE_EVIDENCE = 2   # evidence 達此值且未被打臉 → tentative 升 live


# ============ A 學習骨架（兩種 kind 共用）============

def _now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
    if int(it.get('evidence', 0)) >= _PROMOTE_EVIDENCE and int(it.get('contradicted', 0)) == 0:
        it['status'] = 'live'

def _norm_triggers(triggers):
    triggers = triggers or {}
    return {
        'keywords': [k.strip() for k in (triggers.get('keywords') or []) if k and str(k).strip()],
        'mode': (triggers.get('mode') or 'any').strip(),   # any / chat / article
    }

def rule_add(kind, when, then, because=None, scope=None, triggers=None):
    """收料：寫入一條候選規則，初始 tentative、evidence=1。完全相同的既有規則改為再觀察一次。"""
    when = (when or '').strip()
    then = (then or '').strip()
    if not when or not then:
        return {'ok': False, 'error': 'when 與 then 皆不可空'}
    items = _load(kind)
    for it in items:
        if (it.get('when', '').strip() == when and it.get('then', '').strip() == then
                and it.get('status') != 'retired'):
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
        'evidence': 1, 'contradicted': 0, 'status': 'tentative',
        'born': _now(), 'last': _now(),
    }
    items.append(rec)
    _save(kind, items)
    return {'ok': True, 'id': rec['id'], 'status': rec['status'], 'record': rec}

def rule_hit(kind, rid, what):
    """固化／打臉：confirm→evidence+1，達門檻且未被打臉即升 live；contradict→contradicted+1，退回 tentative。"""
    items = _load(kind)
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
    else:
        return {'ok': False, 'error': 'what 必須是 confirm 或 contradict'}
    hit['last'] = _now()
    _save(kind, items)
    return {'ok': True, 'id': rid, 'status': hit['status'],
            'evidence': hit['evidence'], 'contradicted': hit['contradicted']}

def rule_list(kind, status=None):
    """列出規則供檢視；status 可填 live／tentative／retired，不填給全部。"""
    items = _load(kind)
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
    """把 live 且觸發命中的規則做成注入文字。無命中回空字串，注入量跟「這輪相關幾條」走、不跟總量走。"""
    live = [it for it in _load(kind) if it.get('status') == 'live']
    picked = [it for it in live if _match(it, context_text, mode)]
    if not picked:
        return ''
    picked = picked[-limit:]
    head = header or ('【已萃取的規則——命中就照做，並附一句報備'
                      '「依你〔id〕原則我做了X（不對就說一聲）」；被更正就呼叫 rule_hit(kind,id,"contradict")】')
    lines = ['\n' + head]
    for it in picked:
        lines.append('- 〔%s｜%s〕當 %s → 偏好 %s（本質：%s）'
                     % (it.get('id'), it.get('scope', '全域'),
                        it.get('when'), it.get('then'), it.get('because', '')))
    return '\n'.join(lines) + '\n'


# ============ C 機械掃描（語言偏好，生成後確定性處理，不佔提示）============

_SUBS = [('本研究', '此研究'), ('本專案', '此專案')]
_ABSOLUTE = ['證明', '必然', '一定', '絕對', '完全', '永遠', '所有', '毫無']

def mechanical_scan(text):
    """對寫完的文字做確定性處理：安全詞直接替換、絕對詞只標記不改。
    回傳 {text 改後文字, substituted 已替換清單, absolute_flags 絕對詞旗標}。"""
    fixed = text or ''
    applied = []
    for a, b in _SUBS:
        c = fixed.count(a)
        if c:
            fixed = fixed.replace(a, b)
            applied.append({'from': a, 'to': b, 'count': c})
    flags = []
    for w in _ABSOLUTE:
        c = fixed.count(w)
        if c:
            flags.append({'word': w, 'count': c})
    return {'text': fixed, 'substituted': applied, 'absolute_flags': flags}
