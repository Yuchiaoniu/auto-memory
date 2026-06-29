#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設計演化 Bot v1.0
每 5 分鐘用 explorer 模式迭代優化「跨科目學習系統設計」
六問自檢 + 跨時間宏觀視角 + 版本評分
"""
import requests, subprocess, time, datetime, os, re, json, tempfile

_cfg_path = os.path.expanduser("~/.claude/.telegram-config")
_cfg = {}
if os.path.exists(_cfg_path):
    with open(_cfg_path) as _f:
        for _line in _f:
            _k, _, _v = _line.strip().partition("=")
            _cfg[_k.strip()] = _v.strip()
TOKEN    = _cfg.get("TOKEN", "")
CHAT_ID  = _cfg.get("CHAT_ID", "")
OUT_DIR  = "/home/yuchi/cognitive-tests"
LOG_PATH   = os.path.join(OUT_DIR, "design_log.md")
STATE_PATH = os.path.join(OUT_DIR, "design_state.md")
CTR_PATH   = os.path.join(OUT_DIR, "design_iter.json")
INTERVAL   = 300  # 5 分鐘

TOPIC = """跨科目學習系統設計問題：
1. 如何主動推送題目（Proactive Push to Telegram）
2. 如何分析使用者學習情況（Learning Analytics）
3. 如何為使用者補充前情提要（Context Briefing）
4. 如何降低推送內容造成的認知負荷（Cognitive Load Reduction）
科目範圍：finance、stats、accounting"""

SIX_QUESTIONS = """每輪必須依序回答以下六個問題（每題不超過 3 句話）：

Q1. 有沒有什麼值得優化的地方？（當前設計的缺口）
Q2. 有沒有什麼值得保留的優點？（已確認有效的機制）
Q3. 有沒有什麼沒有注意到的問題？（隱藏風險或盲點）
Q4. 有沒有可以降低使用者認知負荷的可能？
Q5. 有沒有跨時間和跨輪迭代的宏觀視角？（考量第 10 輪後 / 100 個使用者後的狀態）
Q6. 有沒有為各項機制做評分？（0–10 分，需說明比較基準）

最後必須輸出更新後的設計狀態，格式如下（標記不可省略）：

=== STATE_UPDATE_START ===
# 跨科目學習系統 — 設計狀態 v{版本號}

## 版本說明
{本輪做出的最重要設計決策，一句話}

## 核心設計決策
{條列已確定的設計決策}

## 當前機制清單（含評分）
{機制名稱}: {分數}/10 — {一句理由}

## 待解決問題
{條列仍未決定的問題}

## 最新宏觀視角
{跨時間分析，2–3 句}
=== STATE_UPDATE_END ==="""

INITIAL_STATE = """# 跨科目學習系統 — 設計狀態 v0.0

## 版本說明
初始狀態，尚未設計

## 核心設計決策
（尚未做出任何決策）

## 當前機制清單（含評分）
Telegram 基礎設施: 7/10 — Bot token 已設定、Chat ID 確認、send() 函式可用
pick_subject() v1: 1/10 — 死鎖 bug，第一輪後只選 stats

## 待解決問題
- 使用者如何回答（Telegram inline button / 文字輸入？）
- 如何定義「前情提要」的最小單元
- 推送頻率：時間觸發 vs 使用者主動觸發
- 如何保存每位使用者的學習狀態

## 最新宏觀視角
目前僅有 1 位使用者（開發者本人），但設計時需預設多使用者架構。
"""

SYSTEM_PROMPT = """你是一個設計演化分析師，正在迭代優化一個跨科目學習系統的設計。

規則：
- 保持 explorer 模式：只思考和設計，不實作
- 使用跨時間宏觀視角：第 N 輪後系統會是什麼狀態
- 精簡：每個 Q 的回答不超過 3 句話，總長控制在 700 字以內
- 必須輸出 STATE_UPDATE 區塊（格式見題目要求）
- 版本號規則：每輪小版本 +0.1；當本輪有重大架構決策時，升主版本（例如 v0.9 → v1.0）"""


def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text[:4000]}, timeout=15)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[Telegram] {e}")
        return False


def read_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return f.read()
    return INITIAL_STATE


def write_state(content):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def read_counter():
    if os.path.exists(CTR_PATH):
        with open(CTR_PATH) as f:
            return json.load(f).get("iteration", 0)
    return 0


def write_counter(n):
    with open(CTR_PATH, "w") as f:
        json.dump({"iteration": n}, f)


def append_log(text):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(text)


def call_claude(user_text):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".sys", delete=False, dir="/tmp") as sf:
        sf.write(SYSTEM_PROMPT)
        sys_path = sf.name
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".usr", delete=False, dir="/tmp") as uf:
        uf.write(user_text)
        usr_path = uf.name

    script = f"""
source /home/yuchi/.nvm/nvm.sh 2>/dev/null
SYSP=$(cat {sys_path})
cat {usr_path} | claude --print --dangerously-skip-permissions --system-prompt "$SYSP"
"""
    try:
        result = subprocess.run(
            ["bash", "-l"],
            input=script,
            capture_output=True,
            text=True,
            timeout=180,
            env={**os.environ, "HOME": "/home/yuchi", "USER": "yuchi"},
        )
        out = result.stdout.strip()
        if not out:
            err = result.stderr[:300] if result.stderr else "(no stderr)"
            return f"[Claude 無輸出 rc={result.returncode}: {err}]"
        return out
    except subprocess.TimeoutExpired:
        return "[Claude 逾時 180s]"
    except Exception as e:
        return f"[Claude 呼叫錯誤: {e}]"
    finally:
        for p in [sys_path, usr_path]:
            try:
                os.unlink(p)
            except Exception:
                pass


def extract_version(text):
    m = re.search(r"設計狀態 v(\d+\.\d+)", text)
    return m.group(1) if m else None


def extract_scores(text):
    scores = re.findall(r"(\d+(?:\.\d+)?)/10", text)
    if not scores:
        return None
    return sum(float(s) for s in scores) / len(scores)


def run_iteration():
    iteration = read_counter() + 1
    write_counter(iteration)

    now = datetime.datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    current_state = read_state()
    current_ver = extract_version(current_state) or "0.0"

    # 計算下一個版本號（給 Claude 參考）
    try:
        major, minor = current_ver.split(".")
        suggested_ver = f"{major}.{int(minor)+1}"
    except Exception:
        suggested_ver = "0.1"

    prompt = f"""迭代 #{iteration} | 時間：{ts}

## 設計主題
{TOPIC}

## 當前設計狀態
{current_state}

## 本輪任務
{SIX_QUESTIONS}

建議版本號：v{suggested_ver}（如本輪有重大決策可升主版本）"""

    response = call_claude(prompt)

    # 解析 STATE_UPDATE 區塊
    state_match = re.search(
        r"=== STATE_UPDATE_START ===(.*?)=== STATE_UPDATE_END ===",
        response,
        re.DOTALL,
    )
    if state_match:
        new_state = state_match.group(1).strip()
        write_state(new_state)
        analysis = response[: response.find("=== STATE_UPDATE_START ===")].strip()
        new_ver = extract_version(new_state) or suggested_ver
    else:
        analysis = response
        new_state = None
        new_ver = suggested_ver

    version_bumped = new_ver != current_ver
    avg_score = extract_scores(response)

    # 寫 log
    log_entry = f"""
## 迭代 #{iteration} | {ts} | v{new_ver}{" ★版本更新" if version_bumped else ""}

{analysis}

{"**設計狀態已更新至 v" + new_ver + "**" if version_bumped else ""}
{"平均評分：" + f"{avg_score:.1f}/10" if avg_score else ""}

---
"""
    append_log(log_entry)

    # Telegram 精簡版（前 20 行非空行）
    lines = [l for l in analysis.split("\n") if l.strip()]
    preview = "\n".join(lines[:20])
    score_str = f"平均評分：{avg_score:.1f}/10  " if avg_score else ""
    ver_str = "★ 版本更新" if version_bumped else ""
    tg = (
        f"[設計迭代 #{iteration}] v{new_ver}  {score_str}{ver_str}\n\n"
        f"{preview}"
        f"\n{'...' if len(lines) > 20 else ''}"
    )
    return tg


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.exists(LOG_PATH):
        append_log(
            f"# 跨科目學習系統設計演化日誌\n\n"
            f"啟動時間：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n"
        )

    if not os.path.exists(STATE_PATH):
        write_state(INITIAL_STATE)

    send(
        "設計演化 Bot v1.0 已啟動\n\n"
        "主題：跨科目學習系統設計\n"
        "六問自檢 + 跨時間宏觀視角 + 版本評分\n"
        "每 5 分鐘一輪，第一輪立即開始。"
    )

    # 第一輪立即執行
    try:
        tg = run_iteration()
        send(tg)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 迭代 #1 完成")
    except Exception as e:
        send(f"迭代 #1 錯誤：{e}")
        print(f"迭代 #1 錯誤：{e}")

    # 後續每 5 分鐘一輪
    while True:
        time.sleep(INTERVAL)
        try:
            tg = run_iteration()
            send(tg)
            ctr = read_counter()
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 迭代 #{ctr} 完成")
        except Exception as e:
            err = f"迭代錯誤：{e}"
            print(err)
            send(err)


if __name__ == "__main__":
    main()
