# -*- coding: utf-8 -*-
"""
server.py — Project Arcus Flask HTTP Server（port 7800）
=========================================================
URL prefix: /arcus/
所有路由都有 /arcus 前綴，以便 nginx proxy_pass 可獨立代理。

nginx 設定範例：
  location /arcus/ {
    proxy_pass http://127.0.0.1:7800/arcus/;
    proxy_set_header X-Real-IP $remote_addr;
    add_header Cache-Control no-cache;
  }
"""
import os
import re
import json
import time
import queue
import threading
import subprocess
import tempfile
import urllib.parse as _urlparse
import hashlib

from flask import Flask, jsonify, Response, request, send_from_directory

# 六支合體：原 arcus_hooks／routing_law／smart_brake／weight_baker／context_meter／
# write_log 全部併入 arcus_core.py（走甲、不 import 子模組、不開子行程）。
# 這裡一次從 arcus_core 取齊掛鉤與 log 產生器介面。
from arcus_core import (
    before_prompt_hook, after_response_hook, generate_project_map,
    read_utf8, read_log_for_display, append_log_turn, trim_log_if_needed,
    _tool_summary, append_token_log, _strip_map_footer,
    build_system_prompt, parse_image_with_claude, build_turn_review,
    build_tasks_injection, est_tokens,
    write_log, read_log,
)

# ── 第三響：OpenRouter 405B 同級模型獨立第二意見（只動 server.py，不碰 core）──
# 只借 three_voices.py 的 OpenRouter 呼叫函式；金鑰讀取自己寫一份安全版，
# 避開 three_voices.load_key 找不到金鑰時 sys.exit 打斷伺服器串流的坑。
try:
    from three_voices import ask_openrouter as _tv_ask_or, OR_MODELS as _TV_OR_MODELS
    _THIRD_VOICE_IMPORT_OK = True
except Exception as _e_tv:
    _THIRD_VOICE_IMPORT_OK = False
    _THIRD_VOICE_IMPORT_ERR = str(_e_tv)

_THIRD_VOICE_ENABLED = False  # §關閉第三響（2026-07-22 使用者要求關掉 OpenRouter 第二意見）；改 True 即恢復

_THIRD_VOICE_CREDS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '.web_creds.json')

def _third_voice_key():
    """安全讀 OpenRouter 金鑰；缺就丟一般例外（不 sys.exit）。"""
    with open(_THIRD_VOICE_CREDS, encoding='utf-8') as f:
        k = __import__('json').load(f).get('openrouter_api_key')
    if not k:
        raise RuntimeError('.web_creds.json 缺 openrouter_api_key')
    return k

def _third_voice(user_msg):
    """OpenRouter 獨立第二意見：乾淨提問（不看主回應），回 (文字, 用到的模型)。"""
    if not _THIRD_VOICE_IMPORT_OK:
        return ('（第三響模組未載入：%s）' % _THIRD_VOICE_IMPORT_ERR, 'unavailable')
    key = _third_voice_key()
    return _tv_ask_or(key, _TV_OR_MODELS, [{'role': 'user', 'content': user_msg}])


# ── 路徑常數 ──────────────────────────────────────────────────────────────────

_CLAUDE_HOME = os.path.expanduser('~/.claude')
CHANGES = os.path.join(_CLAUDE_HOME, 'openspec', 'changes')

# §30 跨裝置分頁狀態同步：已開啟分頁集合存這裡，所有裝置回前景時 GET 調和，
# 使手機與電腦顯示同一組已開啟專案（last-writer-wins）。
PANES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'open-panes.json')

# §26 串流心跳保活：主回覆串流若靜默超過此秒數（只思考／工具執行等空檔），
# 就送一則 SSE 註解行「: hb」，防止手機行動網路的 NAT 把閒置連線回收、
# 導致主回覆串流中途斷線。前端只認 data: 開頭封包，此註解行會被忽略。
HEARTBEAT_SECS = 10

# ── Flask app ─────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder='.')

# === ARCUS ADDON · 常駐 HTTP MCP 端點，取代每輪 stdio 臨時行程 (2026-07-21) ===
# claude 以 {"type":"http","url":".../arcus/mcp"} 連上這條路由；工具原樣派進
# arcus_core._arcus_mcp_handle（真 arcus_do 分派）。伺服器常駐 → 工具第一輪即 connected，
# 消除 stdio 版「還在 pending 就被拍照」的競速。畫圖仍走子行程，不進常駐。
import uuid as _uuid_addon
from arcus_core import _arcus_mcp_handle as _mcp_handle_addon
from arcus_core import _arcus_set_request_project as _set_proj_addon, _arcus_clear_request_project as _clr_proj_addon
try:
    from arcus_core import _adaptive as _adaptive
except Exception:
    _adaptive = None
def _arcus_mcp_reply(payload, accept):
    if 'text/event-stream' in accept:
        return Response('event: message\ndata: ' + json.dumps(payload, ensure_ascii=False) + '\n\n',
                        mimetype='text/event-stream')
    return Response(json.dumps(payload, ensure_ascii=False), mimetype='application/json')
@app.route('/arcus/mcp', methods=['POST'])
def _arcus_mcp_post():
    accept = request.headers.get('Accept', '')
    try:
        _msg = json.loads(request.get_data(as_text=True))
    except Exception:
        return Response('bad json', status=400)
    _proj = request.args.get('project')
    _root = None
    if _proj:
        _cbase = os.path.join('/home/yuchi/.claude/openspec/changes', _proj)
        _cand = os.path.join(_cbase, 'runtime') if _proj == 'arcus' else _cbase
        if os.path.isdir(_cand):
            _root = _cand
    _set_proj_addon(_root)
    try:
        _resp = _mcp_handle_addon(_msg)
    finally:
        _clr_proj_addon()
    if _resp is None:
        return Response('', status=202)
    _r = _arcus_mcp_reply(_resp, accept)
    if _msg.get('method') == 'initialize':
        _r.headers['Mcp-Session-Id'] = _uuid_addon.uuid4().hex
    return _r
@app.route('/arcus/mcp', methods=['GET'])
def _arcus_mcp_get():
    def _gen():
        for _ in range(8):
            yield ': keepalive\n\n'
            time.sleep(15)
    return Response(_gen(), mimetype='text/event-stream')
@app.route('/arcus/mcp', methods=['DELETE'])
def _arcus_mcp_delete():
    return Response('', status=200)

# In-memory 對話歷史，格式：project -> [(user_str, bot_str), ...]
chat_histories: dict = {}
# §31 進行中的「輪」，格式：project -> turn dict
# turn = {proc, subs(訂閱者 queue 清單), backlog(已發佈 SSE), lock, done, stopped}
# 與 HTTP 連線解綁：整輪跑在背景 worker 執行緒，SSE 連線只當訂閱者，斷線不殺子行程。
active_turns: dict = {}


# ── §35 版本標記（治本：直接回報現行運作版本，取代比對檔案修改時間反推部署）──────────
# 在 process 啟動載入程式碼這一刻，把「啟動時戳＋五個核心檔的當下雜湊」算好快取進記憶體。
# 之後即使有人改了磁碟上的檔卻沒重啟，本標記仍是啟動當時那份，故 /health 回報的雜湊
# 對不上磁碟現檔＝「改了沒重啟」，比看檔案 mtime 反推可靠。
_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
_CORE_FILES = ['server.py', 'arcus_core.py']


def _hash_file(path: str) -> str:
    """回傳檔案內容的 sha256 前 12 碼；讀不到回 'MISSING'。"""
    try:
        with open(path, 'rb') as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:12]
    except OSError:
        return 'MISSING'


# 啟動當下就算好並快取（只算一次，代表這個 process 實際載入的那份程式碼）。
BOOT_TIME = time.time()
BOOT_TIME_STR = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(BOOT_TIME))
CORE_HASHES = {name: _hash_file(os.path.join(_CORE_DIR, name)) for name in _CORE_FILES}


# ── 路由 ──────────────────────────────────────────────────────────────────────

@app.route('/arcus/')
@app.route('/arcus')
def index():
    """返回前端 index.html（禁用快取，確保每次拿到最新版）。"""
    response = send_from_directory('.', 'index.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.get('/arcus/api/health')
def health():
    """§35 治本健康／版本查詢：直接回報這個 process 實際跑的是哪一版。
    用法：比對回傳的 core['server.py'] 雜湊對不對得上磁碟現檔雜湊——
    一致＝跑的是現行版；不一致＝已改檔但尚未重啟。startedAt 亦可直接看
    process 啟動時間是否晚於你的修改時間。取代舊的「比對三檔 mtime 反推」儀式。"""
    now = time.time()
    live = {name: _hash_file(os.path.join(_CORE_DIR, name)) for name in _CORE_FILES}
    stale = [name for name in _CORE_FILES if live[name] != CORE_HASHES[name]]
    return jsonify({
        'status': 'ok',
        'pid': os.getpid(),
        'startedAt': BOOT_TIME,
        'startedAtStr': BOOT_TIME_STR,
        'uptimeSec': int(now - BOOT_TIME),
        'core': CORE_HASHES,          # 啟動當下（＝現行運作版）的雜湊
        'diskChanged': stale,         # 磁碟現檔已與運作版不同的核心檔（非空＝需重啟）
        'inSync': not stale,          # True＝運作版就是磁碟現檔
    })


@app.get('/arcus/api/projects')
def list_projects():
    """列出 openspec/changes 目錄下所有專案及其狀態。"""
    result = []
    if not os.path.isdir(CHANGES):
        return jsonify([])

    for name in sorted(os.listdir(CHANGES)):
        p = os.path.join(CHANGES, name)
        if not os.path.isdir(p):
            continue
        tp = os.path.join(p, 'tasks.md')
        pending = done = 0
        next_task = ''
        if os.path.exists(tp):
            with open(tp, encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            pending = sum(1 for l in lines if re.match(r'\s*-\s*\[ \]', l))
            done = sum(1 for l in lines if re.match(r'\s*-\s*\[x\]', l, re.IGNORECASE))
            first = next((l for l in lines if re.match(r'\s*-\s*\[ \]', l)), '')
            next_task = re.sub(r'^\s*-\s*\[ \]\s*', '', first).strip()[:80]
        turns = read_log_for_display(p, n=30)
        _attach_judges(turns, read_all_judge_reports(p))   # §29：每輪附判官報告，重整後仍顯示
        result.append({
            'name': name,
            'pending': pending,
            'done': done,
            'nextTask': next_task,
            'state': '',   # §87 STATE.md 已廢除，欄位留空只為舊前端相容
            'logTurns': turns,
        })
    return jsonify(result)


def _parse_judge_block(block):
    """解析單一判官區塊 → {time, userMsg, report}。
    只認標頭第一個 '## 時間戳' 與第一個 '**使用者：**'，報告本文自帶的 '## 判官' 等標題不誤判。"""
    lines = block.strip().split('\n')
    ts = user_msg = ''
    body_start = 0
    for i, l in enumerate(lines):
        if l.startswith('## '):
            ts = l[3:].strip()
            body_start = i + 1
            break
    for i in range(body_start, len(lines)):
        if lines[i].startswith('**使用者：**'):
            user_msg = lines[i].replace('**使用者：**', '').strip()
            body_start = i + 1
            break
    report = '\n'.join(lines[body_start:]).strip()
    return {'time': ts, 'userMsg': user_msg, 'report': report}


# ── §62.4 判官新落地：judge_log.jsonl（經中央 log 產生器 write_log）──────────────
JUDGE_JSONL = 'judge_log.jsonl'


def _split_report_sections(report):
    """把判官報告本文以 '## ' 標題切成結構化 sections dict（供未來讀取端使用）。
    報告本文原以 '## 判官' 等標題分段（可預先完成的工作／建議新增／框外發現…）；
    這裡把每個 '## 標題' 到下一個 '## ' 之間的內容收成 {標題: 內容}。
    報告全文另存 'report' key，讀取端可無損還原成舊 md 解析結構。"""
    sections = {}
    cur = None
    buf = []
    for line in (report or '').split('\n'):
        if line.startswith('## '):
            if cur is not None:
                sections[cur] = '\n'.join(buf).strip()
            cur = line[3:].strip()
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        sections[cur] = '\n'.join(buf).strip()
    return sections


def _write_judge_report(project_path, user_msg, report, ts=None):
    """§62.4 判官報告落地：組好 content 字典 → write_log 到 judge_log.jsonl。
    不自己 open/write、不自己蓋時間戳（write_log 統一蓋 top-level time）。
    content 內另保留一份 'time' 字串以與舊 md 的 '## 時間戳' 對齊（讀取端優先用它）。
    userMsg 與 report 為讀取端還原成 _parse_judge_block 相同結構的核心欄位。"""
    content = {
        'project': os.path.basename(project_path.rstrip('/')),
        'time': ts or time.strftime('%Y-%m-%d %H:%M:%S'),
        'userMsg': (user_msg or '')[:120],
        'report': report or '',
        'sections': _split_report_sections(report or ''),
    }
    write_log(os.path.join(project_path, JUDGE_JSONL), content)


def _read_judge_jsonl(project_path):
    """讀 judge_log.jsonl（新落地）→ list[{time,userMsg,report}]（檔案順序）。
    每筆 content 還原成與 _parse_judge_block 相同的 dict 結構，讓雙來源可直接接起。
    time 優先用 content['time']（與舊 md 的 '## 時間戳' 同來源），退回 write_log 蓋的 top-level time。"""
    out = []
    for rec in read_log(os.path.join(project_path, JUDGE_JSONL)):
        c = rec.get('content')
        if not isinstance(c, dict):
            continue
        out.append({
            'time': c.get('time') or rec.get('time') or '',
            'userMsg': c.get('userMsg', ''),
            'report': c.get('report', ''),
        })
    return out


def _read_judge_blocks(project_path):
    """讀 judge_log.md，回傳所有非空區塊（原始字串，檔案順序）。"""
    jp = os.path.join(project_path, 'judge_log.md')
    if not os.path.exists(jp):
        return []
    try:
        with open(jp, encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return []
    return [b for b in content.split('\n---\n') if b.strip()]


def read_all_judge_reports(project_path):
    """雙來源合併全部判官報告 → list[{time,userMsg,report}]（§29／§62.4）。
    來源一：舊 judge_log.md（凍結、原地保留），照 _read_judge_blocks/_parse_judge_block 解析（原邏輯不動）。
    來源二：新 judge_log.jsonl，用 read_log 讀出 content 還原成相同結構。
    兩段合併後照時間（'## 時間戳' / content.time）穩定排序回傳，前端仍看得到歷史與新報告。
    無時間戳者排在最前，且保持各來源內原檔案順序（穩定排序不打亂同時間者）。"""
    old = [_parse_judge_block(b) for b in _read_judge_blocks(project_path)]
    new = _read_judge_jsonl(project_path)
    merged = old + new
    # 時間格式為 'YYYY-MM-DD HH:MM:SS'（字典序＝時間序）；空字串排最前。sorted 為穩定排序，
    # 同時間戳者維持「舊 md 在前、新 jsonl 在後」與各自檔案順序，配對邏輯不亂。
    merged.sort(key=lambda r: r.get('time') or '')
    return merged


def read_last_judge_report(project_path, msg=''):
    """回傳判官報告：帶 msg 時回最後一筆使用者訊息相符者，否則回最後一筆（§27／§29）。
    §27：供前端在「關螢幕／切走」導致判官那則回覆訊息漏收時補回。
    §29：帶 msg 搜尋全部區塊，解決「新判官蓋掉舊判官抓不回」與「開頭相同訊息認錯輪」。
    judge_log 每筆格式：\\n---\\n## 時間戳\\n**使用者：** 訊息\\n\\n報告本文\\n
    """
    reports = read_all_judge_reports(project_path)
    if not reports:
        return None
    if msg:
        key = msg.strip()[:30]
        matched = [r for r in reports
                   if r['userMsg'] and (r['userMsg'][:30] == key
                                        or r['userMsg'].startswith(key)
                                        or key.startswith(r['userMsg'][:30]))]
        # 帶 msg 但無相符 → 回 None，不硬回最後一筆，避免補到錯輪
        return matched[-1] if matched else None
    return reports[-1]


def _judge_min_dist(a, b):
    """兩個時間戳字串（'YYYY-MM-DD HH:MM[:SS]'）的分鐘差絕對值；無法解析回 None。"""
    import datetime
    try:
        fa = datetime.datetime.strptime((a or '')[:16], '%Y-%m-%d %H:%M')
        fb = datetime.datetime.strptime((b or '')[:16], '%Y-%m-%d %H:%M')
    except Exception:
        return None
    return abs((fa - fb).total_seconds()) / 60.0


def _attach_judges(turns, reports):
    """把判官報告配到對應輪次（§29／§29b 時間錨配對，重整後顯示用）。
    舊法逐報告貪婪、只比使用者訊息前綴、指標只進不退；當報告數遠多於輪數（舊 md＋新 jsonl
    合併達數百份、畫面只顯示最近數十輪）、或訊息很短（如「好」前綴全中）時會連環錯位，
    把某一輪的判官頁尾漂到另一輪底下。
    新法改逐輪次：每輪只收「使用者訊息前綴相容」的候選，再以分鐘時間戳為主錨挑最接近者；
    有時間資訊時必須落在容忍分鐘內才貼、對不上寧可留空不硬貼；每份報告至多配一輪，杜絕漂移。"""
    TOL_MIN = 2.0  # 跨分鐘邊界容忍：每輪與其判官報告皆於同一輪流程內落地，通常同分鐘或相鄰分鐘
    used = set()
    for t in turns:
        tu = (t.get('user') or '').strip()
        tt = t.get('time') or ''
        cands = []  # (dist_or_None, idx, report)
        for i, r in enumerate(reports):
            if i in used:
                continue
            ju = (r.get('userMsg') or '').strip()
            if not (ju and tu and (tu.startswith(ju) or ju.startswith(tu))):
                continue
            cands.append((_judge_min_dist(tt, r.get('time') or ''), i, r))
        if not cands:
            continue
        timed = [c for c in cands if c[0] is not None]
        if timed:
            timed.sort(key=lambda c: c[0])
            dist, bi, br = timed[0]
            if dist > TOL_MIN:
                continue  # 時間對不上：寧可這輪不掛判官，也不硬貼錯輪
        else:
            _, bi, br = cands[0]  # 兩邊皆無時間資訊：退回訊息相容第一份（仍一輪一份）
        t['judge'] = br.get('report', '')
        used.add(bi)
    return turns


@app.get('/arcus/api/last-judge')
def last_judge():
    """回傳指定專案判官報告，供前端補回判官那則回覆訊息（§27／§29）。
    帶 msg 參數時搜尋全部區塊回傳最後一筆相符者，否則回檔尾最後一筆。"""
    project = request.args.get('project', '')
    msg = request.args.get('msg', '')
    project_path = os.path.join(CHANGES, project)
    if not os.path.isdir(project_path):
        return jsonify({})
    return jsonify(read_last_judge_report(project_path, msg) or {})


def _read_panes():
    """讀 open-panes.json → list[str]（§30）。檔案不存在或損壞時回空清單。"""
    try:
        with open(PANES_FILE, encoding='utf-8') as f:
            data = json.load(f)
        return [x for x in data if isinstance(x, str)] if isinstance(data, list) else []
    except Exception:
        return []


@app.get('/arcus/api/panes')
def get_panes():
    """回傳跨裝置共享的已開啟分頁集合（§30）。"""
    return jsonify(_read_panes())


@app.post('/arcus/api/panes')
def set_panes():
    """設定跨裝置共享的已開啟分頁集合（§30，last-writer-wins）。
    去重、只留字串、保留順序後寫回 open-panes.json。"""
    d = request.get_json(force=True, silent=True) or {}
    panes = d.get('panes', [])
    if not isinstance(panes, list):
        panes = []
    seen = set()
    clean = []
    for x in panes:
        if isinstance(x, str) and x and x not in seen:
            seen.add(x)
            clean.append(x)
    try:
        with open(PANES_FILE, 'w', encoding='utf-8') as f:
            json.dump(clean, f, ensure_ascii=False)
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    return jsonify({'ok': True, 'panes': clean})


def _stream_turn(turn):
    """§32 共用訂閱產生器：訂閱一個進行中的 turn，先補送 backlog（中途重連看得到目前
    進度），再收 live 直到結束哨兵。與 HTTP 連線解綁——GeneratorExit（關分頁／斷線）
    只退訂，絕不動背景 worker 或子行程。chat() 的 SSE 回應與 /api/attach 端點共用此函式。"""
    q = queue.Queue()
    with turn['lock']:
        backlog = list(turn['backlog'])
        done_already = turn['done']
        turn['subs'].append(q)
    try:
        for _sse in backlog:
            yield _sse
        if not done_already:
            while True:
                item = q.get()
                if item is None:
                    break
                yield item
    except GeneratorExit:
        # 瀏覽器關分頁／斷線：只退訂，絕不動 worker 或子行程。
        pass
    finally:
        with turn['lock']:
            if q in turn['subs']:
                turn['subs'].remove(q)


@app.post('/arcus/api/chat')
def chat():
    """
    主對話端點。接收 JSON {project, userMsg}，以 SSE 串流方式返回 Claude 回應。
    before_prompt_hook 負責 Step 1–5 注入，after_response_hook 負責 Step 6–8 觀察。
    """
    d = request.json or {}
    project = d.get('project', '')
    user_msg = d.get('userMsg', '')

    project_path = os.path.join(CHANGES, project)
    if not os.path.isdir(project_path):
        return jsonify({'error': '找不到專案'}), 404

    # 恢復或建立對話歷史
    if project not in chat_histories:
        turns = read_log_for_display(project_path, n=10)
        chat_histories[project] = [(t['user'], t['bot']) for t in turns]
    history = chat_histories[project]

    # §78 打底瘦身：停止每輪注入 tasks.md 與 STATE.md（兩者是被歷史反覆重讀的快取大宗），
    # context 只保留固定速查表 pinned-facts（其他不變）。tasks／STATE 全文仍在硬碟、
    # read_internal.py／Read 隨時可查；改為讓助理靠工具即時搜尋＋只看上一則訊息脈絡工作。
    # §24.2 固定回貼速查表：答案永不變的重複查詢（登入、重啟指令、檔案位置等）一次貼上，省去每輪重查
    context = ''
    pinned_raw = read_utf8(os.path.join(project_path, 'pinned-facts.md'), limit=2000)
    if pinned_raw.strip():
        context = f'=== 固定速查表（答案不變、不必再查）===\n{pinned_raw.strip()}'

    _SYSTEM = build_system_prompt(project, project_path, user_msg=user_msg)

    # §78 對話歷史取最近 2 輪（上兩則訊息脈絡），不再串接最多 5 輪長回覆。
    # 拼接對話歷史 + 當輪輸入
    recent_history = history[-2:] if history else []
    if recent_history:
        thread = '\n'.join(f'使用者：{u}\n助理：{b}' for u, b in recent_history)
        prompt = f'{context}\n\n{thread}\n\n使用者：{user_msg}' if context \
            else f'{thread}\n\n使用者：{user_msg}'
    else:
        prompt = f'{context}\n\n使用者：{user_msg}' if context else user_msg

    # §61 打底注入精確量測：打底＝每輪固定重貼、與當輪對話內容無關的注入總量
    #   ＝ _SYSTEM（制度文字）＋ context（§78 後僅 pinned-facts）
    #     ＋ before_prompt_hook 追加（法條＋結構地圖＋函式索引）。
    # 對話歷史 thread 與當輪 user_msg 不算打底。掛鉤前先存 prompt，掛鉤後對前後兩份各算
    # 一次估算 token 相減＝before_prompt_hook 的純追加量（不必拆鉤子內部、也不管它從哪插入）。
    # 字元數為確定精確值；token 用 est_tokens（中日韓×0.6＋其餘÷4）估、非精算。
    _prompt_before_hook = prompt
    # Step 1–5：before_prompt_hook 增強 prompt
    prompt = before_prompt_hook(project, project_path, user_msg, prompt)
    _hook_added_chars = max(0, len(prompt) - len(_prompt_before_hook))
    _base_inject_chars = len(_SYSTEM) + len(context) + _hook_added_chars
    _hook_added_tokens = max(0, est_tokens(prompt) - est_tokens(_prompt_before_hook))
    _base_inject_est_tokens = est_tokens(_SYSTEM) + est_tokens(context) + _hook_added_tokens

    # §31 本輪 turn 物件：整輪跑在背景 worker，與 HTTP 連線解綁。
    # §32 user_msg：供中途新連上的分頁取回「觸發這一輪的使用者訊息」重畫使用者泡泡。
    turn = {
        'proc': None, 'subs': [], 'backlog': [],
        'lock': threading.Lock(), 'done': False, 'stopped': False,
        'user_msg': user_msg,
    }

    def _publish(sse):
        # 把一段 SSE 字串發佈：進 backlog（供中途重連補看進度）＋推給現場訂閱者。
        with turn['lock']:
            turn['backlog'].append(sse)
            for _q in turn['subs']:
                _q.put(sse)

    def _finish():
        # worker 整輪跑完：標記 done，向所有訂閱者送結束哨兵。
        with turn['lock']:
            turn['done'] = True
            for _q in turn['subs']:
                _q.put(None)

    def _worker():
        text_chunks = []
        tool_events = []
        tool_count = 0                   # P0 工具呼叫計數器
        tool_call_budget_exceeded = False
        token_stats = {}
        turn_start = time.time()         # 11.1 本輪起點，供 per-round 時間拆帳
        round_idx = 0                    # 11.1 assistant 訊息序號＝回合序號
        cur_round_out = 0                # 11.1 當前回合的 output_tokens 快照
        round_notes = {}                 # 20.3 逐回合：{回合序號: {'t': 起始秒, 'text': 該回合輸出文字}}
        result_text = ''
        response_text = ''               # §25 供例外路徑補寫判官時安全引用（避免主對話早段出錯時未定義）
        tmp_path = sys_path = mcp_cfg_path = None
        proc = None
        try:
            # 把 prompt 和 system prompt 寫入 temp 檔
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.txt', encoding='utf-8', delete=False
            ) as f:
                f.write(prompt)
                tmp_path = f.name

            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.txt', encoding='utf-8', delete=False
            ) as f:
                f.write(_SYSTEM)
                sys_path = f.name

            # §路徑修正：每輪把當前專案帶在 MCP 網址上，讓常駐伺服器端分派據此解析專案檔路徑
            _mcp_url = 'http://127.0.0.1:7800/arcus/mcp?project=' + _urlparse.quote(project or '', safe='')
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.json', encoding='utf-8', delete=False
            ) as f:
                json.dump({'mcpServers': {'arcus': {'type': 'http', 'url': _mcp_url}}}, f, ensure_ascii=False)
                mcp_cfg_path = f.name
            env = dict(os.environ)
            env['CLAUDE_SUBPROCESS'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'
            # 把當前專案根傳進 MCP 子程序，讓 arcus_do 的 read/query/map 跟著打開的專案走；
            # arcus 自身程式碼在 runtime 子資料夾，故 arcus 專案以 runtime 為根，其餘專案以專案資料夾為根。
            env['ARCUS_PROJECT_PATH'] = os.path.join(project_path, 'runtime') if project == 'arcus' else project_path
            # §25 開啟思考預算：讓「只思考、沒動工具」的沉默回合把推理草稿吐成 thinking 區塊，
            # 供工作明細記錄。setdefault 保留外部覆寫（設 0 可關）。實測 claude 2.1.196 會吐 type:thinking。
            env['MAX_THINKING_TOKENS'] = '0'  # §25→0：使用者指示歸零思考預算（2026-07-14），回合數靠腳本鎖死、不靠思考
            env['CLAUDE_CODE_MAX_OUTPUT_TOKENS'] = '64000'  # 輸出上限對齊本機 settings.json（2026-07-14）

            # §68 主線模型偵測：使用者本輪原始訊息 strip 後少於 _SHORT_MSG_LEN=10 個字元 → 用 sonnet
            # （短訊息如「好」「請重啟」「確定關掉」多為簡單確認、不需 opus 全推理，改用較快的 sonnet 省成本）；
            # 否則維持 opus。半開區間：長度 0–9 用 sonnet、>=10 用 opus。判官另走 smart_brake._call_opus
            # 恆用 opus、不受此影響。要一句話切回全 opus：把 _main_model 直接設回 'opus'。
            _SHORT_MSG_LEN = 10
            _main_model = 'sonnet' if len((user_msg or '').strip()) < _SHORT_MSG_LEN else 'opus'
            # §72 機械層禁派子代理：在 CLI 層以 --disallowedTools 直接把子代理生成工具抽掉，
            # 主線再想派也拿不到工具（確定性機械閘、不靠自律，等同 scan() 的做法）。
            # 工具真名經實測為 Agent（非記憶誤以為的 Task；Task* 那組是背景任務管理、非子代理）
            # ＋ Workflow（多代理 fan-out 生成器），兩者一併禁；--dangerously-skip-permissions 不抵消此旗標。
            # 端到端實測：加旗標後工具清單裡 Agent／Workflow 皆消失。要一句話還原：把 _NO_SUBAGENTS 設為 ''。
            _NO_SUBAGENTS = '--disallowedTools Agent Workflow ToolSearch '  # §72→放行 Skill：使用者指示把 explore 技能還給 arcus（2026-07-14）
            script = (
                f'source ~/.nvm/nvm.sh 2>/dev/null; '
                f'SYSP=$(cat "{sys_path}"); '
                f'cat "{tmp_path}" | claude --print --model {_main_model} --output-format stream-json --verbose '
                f'--settings /home/yuchi/.claude/openspec/changes/arcus/runtime/arcus_settings.json '
                f'--mcp-config {mcp_cfg_path} --strict-mcp-config '
                f'--allowedTools mcp__arcus__arcus_do Skill {_NO_SUBAGENTS}--system-prompt "$SYSP"'
            )
            cmd = ['bash', '-lc', script]

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace',
                env=env,
            )
            turn['proc'] = proc

            # §26 背景執行緒把 proc.stdout 逐行推進 queue，主 generator 以 timeout 取行；
            # 這樣「只思考／工具執行」的靜默空檔不再讓迴圈阻塞在 readline，可定時送心跳。
            _line_q = queue.Queue()
            _EOF = object()

            def _pump(stream, q, sentinel):
                try:
                    for _ln in stream:
                        q.put(_ln)
                finally:
                    q.put(sentinel)

            _reader = threading.Thread(
                target=_pump, args=(proc.stdout, _line_q, _EOF), daemon=True
            )
            _reader.start()

            # 逐行解析 stream-json 事件並 SSE 推送
            while True:
                if tool_call_budget_exceeded:
                    break
                try:
                    raw_line = _line_q.get(timeout=HEARTBEAT_SECS)
                except queue.Empty:
                    # §26 靜默逾時 → 送 SSE 註解行保活（前端第 431 行只認 data: 開頭，
                    # 此註解行被忽略、對話泡泡不受影響），防手機 NAT 回收閒置連線。
                    _publish(": hb\n\n")
                    continue
                if raw_line is _EOF:
                    break
                raw = raw_line.rstrip('\n\r')
                if not raw.strip():
                    continue
                try:
                    event = json.loads(raw)
                    ev_type = event.get('type', '')
                    if ev_type == 'assistant':
                        # 11.1 每個 assistant 事件＝一回合，抓該回合 output_tokens 快照
                        round_idx += 1
                        _usage = event.get('message', {}).get('usage', {})
                        cur_round_out = _usage.get('output_tokens', 0)
                        # 55.2 該回合重刷的脈絡量：API 逐回合親報的 cache_read_input_tokens。
                        # 各回合值不同、加總＝result 結算的 cache_read（實測 14839+16764=31603）。
                        cur_round_cache_read = _usage.get('cache_read_input_tokens', 0)
                        # 20.3 記本回合起始秒，供工作明細顯示只思考回合的時間
                        round_notes[round_idx] = {
                            't': round(time.time() - turn_start, 1), 'text': ''
                        }
                        for block in event.get('message', {}).get('content', []):
                            if block.get('type') == 'text':
                                text = block.get('text', '')
                                if _adaptive is not None and text:
                                    text = _adaptive.hard_subs(text)
                                if text:
                                    text_chunks.append(text)
                                    # 20.3 累積該回合輸出文字（截斷，避免過長）
                                    _note = round_notes.get(round_idx)
                                    if _note is not None and len(_note['text']) < 400:
                                        _note['text'] += text
                                    _publish(f"data: {json.dumps({'t': text}, ensure_ascii=False)}\n\n")
                            elif block.get('type') == 'thinking':
                                # §25 記錄沉默回合的推理草稿：收進 round_notes 供工作明細顯示，
                                # 不推送瀏覽器，維持對話泡泡乾淨（外觀不動，只在明細/judge_log 呈現）。
                                _tk = block.get('thinking', '')
                                _note = round_notes.get(round_idx)
                                if _note is not None:
                                    # §28 只要出現 thinking 區塊就記旗標，即使明文為空（命令列在工具間
                                    # 的交錯思考只回簽章、不回明文），供工作明細分辨「有思考但明文被扣」
                                    # 與「真的空轉」，避免誤標成「什麼都沒做」。
                                    _note['had_thinking'] = True
                                    if _tk:
                                        _note['thinking'] = (_note.get('thinking', '') + _tk)[:600]
                            elif block.get('type') == 'tool_use':
                                tool_events.append({
                                    'tool': block.get('name', '?'),
                                    'id': block.get('id', ''),
                                    'input': block.get('input', {}),
                                    'summary': _tool_summary(
                                        block.get('name', ''), block.get('input', {})
                                    ),
                                    'round': round_idx,                        # 11.1
                                    't': round(time.time() - turn_start, 1),   # 11.1 起始秒
                                    '_t0': time.time(),                        # 11.1 供算工具耗時
                                    'out_tokens': cur_round_out,               # 11.1 該回合產出tok
                                    'cache_read': cur_round_cache_read,        # 55.2 該回合重刷脈絡量
                                })
                                tool_count += 1
                                if tool_count == 25:
                                    _publish(f"data: {json.dumps({'warnings': ['已用 25 次工具，請收斂任務範圍']}, ensure_ascii=False)}\n\n")
                                elif tool_count > 200:
                                    proc.terminate()
                                    _cutoff_msg = '[系統中斷] 工具呼叫超過 200 次（安全網），本輪已停止。請縮小任務範圍重試。'
                                    text_chunks.append(_cutoff_msg)
                                    _publish(f"data: {json.dumps({'t': _cutoff_msg}, ensure_ascii=False)}\n\n")
                                    tool_call_budget_exceeded = True
                                    break
                    elif ev_type == 'user':
                        # 擷取工具結果（tool_result），依 tool_use_id 回填對應 tool_event
                        for block in event.get('message', {}).get('content', []):
                            if block.get('type') != 'tool_result':
                                continue
                            tu_id = block.get('tool_use_id', '')
                            content = block.get('content', '')
                            if isinstance(content, list):
                                content = ''.join(
                                    b.get('text', '') for b in content
                                    if isinstance(b, dict) and b.get('type') == 'text'
                                )
                            content = str(content)
                            for ev in reversed(tool_events):
                                if ev.get('id') == tu_id:
                                    ev['result'] = content[:2000]
                                    # 11.1 工具耗時 = 結果到達 - 呼叫發出
                                    ev['dur'] = round(time.time() - ev.get('_t0', time.time()), 1)
                                    break
                    elif ev_type == 'result':
                        result_text = event.get('result', '')
                        usage = event.get('usage', {})
                        token_stats = {
                            'input_tokens': usage.get('input_tokens', 0),
                            'output_tokens': usage.get('output_tokens', 0),
                            'cache_read_input_tokens': usage.get('cache_read_input_tokens', 0),
                            'cache_creation_input_tokens': usage.get('cache_creation_input_tokens', 0),
                            'cost': event.get('total_cost_usd', 0),
                            'duration_ms': event.get('duration_ms', 0),
                            # §61 打底注入精確欄位（chat() 於 prompt 組裝時量好，_worker 閉包取用）
                            'base_inject_chars': _base_inject_chars,
                            'base_inject_est_tokens': _base_inject_est_tokens,
                        }
                except (json.JSONDecodeError, KeyError):
                    # 非 JSON 行（例如 stderr 混入）直接推送
                    if raw.strip():
                        text_chunks.append(raw)
                        _publish(f"data: {json.dumps({'t': raw_line.rstrip(chr(13))}, ensure_ascii=False)}\n\n")

            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

            # §63 取得回應文字：保留「中途敘述」。
            # text_chunks 是整段串流累積（含工具與工具之間的中途敘述），也正是瀏覽器
            # 即時顯示的全部（第 570 行每個 text 區塊都 _publish 給瀏覽器）；result_text
            # 只是 claude 結算的「最終那一則」、不推送瀏覽器。原本以 result_text 優先落地，
            # 等於把中途敘述丟掉（＝使用者所稱「最後那個整理動作」）。改為以 text_chunks
            # 為主、僅在串流為空時退回 result_text，讓 log／歷史保留完整中途敘述。
            response_text = _strip_map_footer(
                (''.join(text_chunks) or result_text).strip()
            )

            if response_text:
                history.append((user_msg, response_text))
                if len(history) > 5:
                    history[:] = history[-5:]
                append_log_turn(project_path, user_msg, response_text)
                trim_log_if_needed(project_path)

                # Step 6–8：after_response_hook 觀察與偵測違規
                scan_issues = (
                    after_response_hook(project, project_path, user_msg, response_text, tool_events)
                    or []
                )
                if scan_issues:
                    warn_labels = [i.get('pattern', '?') for i in scan_issues]
                    _publish(f"data: {json.dumps({'warnings': warn_labels}, ensure_ascii=False)}\n\n")

            if token_stats:
                append_token_log(project_path, user_msg, token_stats, tool_events)

            _publish(f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n")

            # 11.8 一回二：主回覆完成後，第二則泡泡送本輪體帳（時間拆帳）＋判官解析
            try:
                _report = build_turn_review(
                    project, project_path, user_msg, response_text,
                    tool_events, token_stats, round_notes
                )
            except Exception as _e:
                print(f'[turn_review] {_e}')
                _report = f'## 判官\n（判官這輪發生例外、無法產生，原因：{_e}）'
            if not _report:
                _report = '## 判官\n（判官這輪未產生內容：判官模組未載入或回傳空白，通常是 server 尚未重啟載入新碼。）'
            # 判官訊息一律送出，失敗就送白話原因，永不無聲消失（§23）
            _publish(f"data: {json.dumps({'report': _report}, ensure_ascii=False)}\n\n")
            # §24.1／§62.4 判官報告落地存檔：改經中央 log 產生器寫進 judge_log.jsonl
            # （舊 judge_log.md 凍結、不再寫）。write_log 永不拋例外，故不再需要外層 try。
            _write_judge_report(project_path, user_msg, _report)
            # 11.9 第三響：OpenRouter 第二意見——依使用者要求關閉（_THIRD_VOICE_ENABLED；2026-07-22）。
            if _THIRD_VOICE_ENABLED:
                try:
                    _or_text, _or_used = _third_voice(user_msg)
                    _or_report = '## 第三響 · OpenRouter（%s）\n\n%s' % (_or_used, _or_text)
                except Exception as _e_or:
                    _or_report = '## 第三響 · OpenRouter\n（第三響這輪失敗，原因：%s）' % _e_or
                _publish(f"data: {json.dumps({'report': _or_report}, ensure_ascii=False)}\n\n")

        except Exception as e:
            _publish(f"data: {json.dumps({'t': f'[錯誤] {e}'}, ensure_ascii=False)}\n\n")
            # §25 零前提保證：主對話中途出錯也一定送判官並落地 judge_log，
            # 關掉「這輪必須不出錯判官才會落地」這道隱形前提，永不因例外而漏寫。
            try:
                _er = build_turn_review(
                    project, project_path, user_msg, response_text,
                    tool_events, token_stats, round_notes
                ) or ''
            except Exception as _e2:
                _er = f'（判官這輪也失敗，原因：{_e2}）'
            _er = (f'## 判官\n（主對話這輪中途出錯：{e}；'
                   f'以下為出錯前已蒐集到的工作明細。）\n\n{_er}')
            _publish(f"data: {json.dumps({'report': _er}, ensure_ascii=False)}\n\n")
            # §25／§62.4 例外路徑同樣改經中央 log 產生器落地 judge_log.jsonl（永不因例外漏寫）。
            _write_judge_report(project_path, user_msg, _er)
            _publish(f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n")
        finally:
            # §31 連線斷掉不會跑到這裡（worker 不綁 HTTP 連線）。
            # 只有明確 /stop（turn['stopped']=True）才殺子行程；否則讓 claude 跑到完成、
            # 上面已把 log／判官寫好，關分頁也不丟結果。不 pop active_turns：留給同輪重連補看，
            # 下一輪 chat() 會以新 turn 覆蓋。
            if proc and proc.poll() is None and turn['stopped']:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
            for p in (tmp_path, sys_path, mcp_cfg_path):
                if p:
                    try:
                        os.unlink(p)
                    except OSError:
                        pass
        _publish('data: [DONE]\n\n')
        _finish()

    # §31 啟動背景 worker（不綁連線），SSE 連線只當訂閱者
    active_turns[project] = turn
    threading.Thread(target=_worker, daemon=True).start()

    # §31/§32 SSE 連線只當訂閱者，走共用的 _stream_turn（斷線只退訂、不殺子行程）。
    return Response(
        _stream_turn(turn),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


@app.post('/arcus/api/stop')
def stop_chat():
    """終止正在進行的 Claude CLI 子進程（§31：唯一會殺子行程的路徑）。"""
    project = (request.json or {}).get('project', '')
    turn = active_turns.get(project)
    proc = turn.get('proc') if turn else None
    if turn and proc and proc.poll() is None:
        turn['stopped'] = True   # §31 標記後 worker 收尾才會 terminate
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        return jsonify({'ok': True, 'msg': '子進程已終止'})
    return jsonify({'ok': False, 'msg': '無進行中的請求'})


@app.get('/arcus/api/turn-status/<path:project>')
def turn_status(project):
    """§32 供前端載入時判斷該專案有無進行中的一輪。
    active＝turn 存在且尚未 done；userMsg 供前端重畫使用者泡泡。"""
    turn = active_turns.get(project)
    active = bool(turn and not turn['done'])
    return jsonify({
        'active': active,
        'userMsg': turn.get('user_msg', '') if turn else '',
    })


@app.get('/arcus/api/active-turns')
def active_turns_summary():
    """§64 全專案「誰還在跑」總查詢：供 restart_detached.sh 動刀前排空輪詢用。
    Arcus 是單一 server.py 行程、單一 7800 埠、同時服務所有專案；重啟那一刀
    fuser -k 砍掉整個行程＝所有專案一起陪葬（thesis-learn 曾因此被誤殺）。
    此端點讓外部重啟腳本在殺之前先問：有沒有任何專案仍有未完成的一輪？
    busy＝仍在跑的專案名清單；count＝其數量；idle＝True 表示全部閒置、可放行動刀。"""
    busy = [proj for proj, turn in active_turns.items()
            if turn and not turn.get('done')]
    return jsonify({
        'busy': busy,
        'count': len(busy),
        'idle': len(busy) == 0,
    })


@app.get('/arcus/api/attach/<path:project>')
def attach_turn(project):
    """§32 讓新連上的分頁掛回進行中的那一輪：訂閱現有 turn（不啟新 worker），
    先補送 backlog（思考中內容）再收 live。無進行中或已完成則只送 [DONE]，
    前端據此退回讀 log.md 的既有路徑。"""
    turn = active_turns.get(project)
    if not turn or turn['done']:
        def _empty():
            yield 'data: [DONE]\n\n'
        return Response(
            _empty(),
            mimetype='text/event-stream',
            headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
        )
    return Response(
        _stream_turn(turn),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


@app.post('/arcus/api/reset')
def reset_history():
    """清除某專案的 in-memory 對話歷史（開新聊天時使用）。"""
    project = (request.json or {}).get('project', '')
    chat_histories.pop(project, None)
    return jsonify({'ok': True})


@app.get('/arcus/api/log/<path:project>')
def get_log(project):
    """回傳某專案最近 20 輪對話供前端重現（刷新頁面後恢復顯示）。"""
    project_path = os.path.join(CHANGES, project)
    if not os.path.isdir(project_path):
        return jsonify({'error': '找不到專案'}), 404
    turns = read_log_for_display(project_path, n=20)
    return jsonify(turns)


@app.post('/arcus/api/parse-image')
def parse_image():
    """
    接收 base64 圖片，呼叫 Claude CLI 識別題目，回傳 JSON。

    Request:  { "image_base64": "<PNG base64>", "prompt": "（可選）" }
    Response: { "ok": bool, "data": {...}, "raw": str, "error": str }
    """
    d = request.json or {}
    image_b64 = d.get('image_base64', '')
    prompt_hint = d.get('prompt', '識別這道題目的完整文字與選項')

    if not image_b64:
        return jsonify({'ok': False, 'error': '缺少 image_base64'}), 400

    result = parse_image_with_claude(image_b64, prompt_hint)
    if not result.get('ok') and 'timeout' in result.get('error', '').lower():
        return jsonify(result), 504
    return jsonify(result)


# ── 啟動 ──────────────────────────────────────────────────────────────────────

# === ARCUS ADDON v1 · arcus_log.md 自動分類 (2026-07-13) ===
import re as _re_addon


def classify_arcus_log():
    """讀唯一的 arcus_log.md，依固定格式 `## [分類] 時間戳` 把各筆記錄歸類。
    回傳 {分類: [{'ts':.., 'content':..}, ...]}，每類內時間新到舊。"""
    path = os.path.join(_CORE_DIR, 'arcus_log.md')
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            text = fh.read()
    except OSError:
        return {}
    groups: dict = {}
    pat = _re_addon.compile(r'^## \[(.+?)\]\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s*$', _re_addon.M)
    marks = list(pat.finditer(text))
    for i, m in enumerate(marks):
        cat = m.group(1).strip()
        ts = m.group(2)
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[start:end].strip()
        groups.setdefault(cat, []).append({'ts': ts, 'content': body})
    for cat in groups:
        groups[cat].sort(key=lambda e: e['ts'], reverse=True)
    return groups


@app.route('/arcus/api/log/classified')
def arcus_log_classified():
    """回傳 arcus_log.md 依分類歸類後的 JSON。"""
    return jsonify({'ok': True, 'groups': classify_arcus_log()})


# === ARCUS ADDON v1 END ===


# === ARCUS ADDON v2 · 分析查詢功能地圖端點 (2026-07-13) ===
@app.route('/arcus/api/functions')
def arcus_functions():
    """回傳功能群地圖；帶 ?names=a,b,c 則批次查那幾支（含 exists／doc）。"""
    from arcus_core import query_function_map
    names = request.args.get('names')
    if names:
        wanted = [n.strip() for n in names.split(',') if n.strip()]
        return jsonify({'ok': True, 'result': query_function_map(wanted)})
    return jsonify({'ok': True, 'map': query_function_map()})


# === ARCUS ADDON v2 END ===


# === ARCUS ADDON · 公開靜態頁面路由 (2026-07-19) ===
# 只放行 changes/_page 這一個資料夾，其餘專案資料夾一概碰不到。
PAGE_ROOT = os.path.realpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', '_page'))


@app.route('/arcus/page/<path:subpath>')
def serve_page(subpath):
    """把 changes/_page 底下的檔案唯讀送給瀏覽器，逃出該資料夾一律 404。"""
    target = os.path.realpath(os.path.join(PAGE_ROOT, subpath))
    if target != PAGE_ROOT and not target.startswith(PAGE_ROOT + os.sep):
        return Response('forbidden', status=404)
    if not os.path.isfile(target):
        return Response('not found', status=404)
    return send_from_directory(os.path.dirname(target), os.path.basename(target))


if __name__ == '__main__':
    print('Project Arcus → http://localhost:7800/arcus/')
    app.run(host='0.0.0.0', port=7800, debug=False, threaded=True)
