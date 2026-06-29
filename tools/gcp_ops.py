# -*- coding: utf-8 -*-
"""
gcp_ops.py — GCP kitchen HTTP 客戶端
用途：本機 Claude 透過 HTTPS 把任務送進 GCP kitchen，讀回結果，
      確保所有生成都在 GCP 引擎完成，本機只做轉交與讀取。

用法：
  python gcp_ops.py chat     <專案名稱> <訊息>
  python gcp_ops.py log      <專案名稱> [筆數，預設 5]
  python gcp_ops.py projects
  python gcp_ops.py reset    <專案名稱>
"""
import sys, json

KITCHEN = "https://forest-carbon.duckdns.org/kitchen"

try:
    import requests
except ImportError:
    sys.exit("[gcp_ops] 缺少 requests：pip install requests")


def chat(project, message):
    """送出訊息，串流印出回應，回傳完整回應文字。"""
    try:
        r = requests.post(
            f"{KITCHEN}/api/chat",
            json={"project": project, "userMsg": message},
            stream=True, timeout=300,
            headers={"Accept": "text/event-stream"}
        )
        r.raise_for_status()
        buf = []
        for raw in r.iter_lines():
            if not raw:
                continue
            line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            if line == "data: [DONE]":
                break
            if line.startswith("data: "):
                try:
                    d = json.loads(line[6:])
                    if "t" in d:
                        buf.append(d["t"])
                        print(d["t"], end="", flush=True)
                except json.JSONDecodeError:
                    pass
        print()
        return "".join(buf)
    except Exception as e:
        print(f"[gcp_ops chat] 錯誤：{e}", file=sys.stderr)
        return ""


def log(project, n=5):
    """印出最近 n 輪 kitchen 對話（從 /api/projects 讀取）。"""
    try:
        r = requests.get(f"{KITCHEN}/api/projects", timeout=15)
        r.raise_for_status()
        for p in r.json():
            if p["name"] == project:
                turns = p.get("logTurns", [])[-n:]
                for t in turns:
                    print(f"使用者：{t['user']}")
                    print(f"Claude ：{t['bot']}")
                    print("---")
                return turns
        print(f"[gcp_ops log] 找不到專案 {project!r}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[gcp_ops log] 錯誤：{e}", file=sys.stderr)
        return []


def projects():
    """列出所有專案名稱與待辦/完成數。"""
    try:
        r = requests.get(f"{KITCHEN}/api/projects", timeout=15)
        r.raise_for_status()
        for p in r.json():
            print(f"{p['name']:<35} 待辦 {p['pending']}  完成 {p['done']}")
        return r.json()
    except Exception as e:
        print(f"[gcp_ops projects] 錯誤：{e}", file=sys.stderr)
        return []


def reset(project):
    """清除 kitchen 對該專案的 in-memory 對話歷史，下次首輪重新注入 STATE.md。"""
    try:
        r = requests.post(f"{KITCHEN}/api/reset",
                          json={"project": project}, timeout=15)
        r.raise_for_status()
        print(f"已重置 {project} 的對話歷史")
        return r.json()
    except Exception as e:
        print(f"[gcp_ops reset] 錯誤：{e}", file=sys.stderr)
        return {}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    if cmd == "chat" and len(args) >= 3:
        chat(args[1], " ".join(args[2:]))
    elif cmd == "log" and len(args) >= 2:
        n = int(args[2]) if len(args) >= 3 else 5
        log(args[1], n)
    elif cmd == "projects":
        projects()
    elif cmd == "reset" and len(args) >= 2:
        reset(args[1])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
