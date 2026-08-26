# -*- coding: utf-8 -*-
"""nginx.conf 의 CSP 헤더를 그대로 적용한 로컬 서버로 폐쇄망 환경 재현 검증"""

# ── 저장소 기준 경로 ──
import os as _os
_R = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DOCS = _os.path.join(_R, "docs", "index.html")
DOCS_URL = "file://" + DOCS
XLSX = _os.path.join(_R, "sample", "ITS_Master_sample.xlsx")
CONF = _os.path.join(_R, "docker", "nginx.conf")
DOCSDIR = _os.path.join(_R, "docs")

def _login(pg, uid="admin", pw="admin"):
    """데모 로그인이 켜져 있으면 통과시킵니다."""
    try:
        if pg.eval_on_selector("#gate", "e=>!e.hidden"):
            pg.fill("#gid", uid); pg.fill("#gpw", pw)
            pg.click("#gbtn"); pg.wait_for_timeout(1800)
    except Exception:
        pass


import http.server, socketserver, threading, re, os, functools


csp = ""
with open(CONF, encoding="utf-8") as f:
    m = re.search(r'Content-Security-Policy\s*\n?\s*"([^"]+)"', f.read())
    if m:
        csp = m.group(1)
print("  적용 CSP:", csp[:100], "...\n")


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if csp:
            self.send_header("Content-Security-Policy", csp)
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, *a):
        pass


handler = functools.partial(H, directory=DOCSDIR)
srv = socketserver.TCPServer(("127.0.0.1", 8899), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

from playwright.sync_api import sync_playwright



viol, errs = [], []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, accept_downloads=True)
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: viol.append(m.text)
          if m.type == "error" and "Content Security" in m.text else None)

    pg.goto("http://127.0.0.1:8899/index.html")
    pg.wait_for_timeout(900)
    _login(pg)

    # 전 탭 순회
    for t in ["dash", "std", "mtx", "jdk", "sw", "asset", "patch", "verify", "chat", "data"]:
        pg.click(f'button[data-t="{t}"]')
        pg.wait_for_timeout(450)
        body = pg.inner_text(f"#tab-{t}")
        print(f"  [{t:5s}] 렌더 {len(body):>6,}자")

    # 챗봇 질의
    pg.click('button[data-t="chat"]')
    pg.wait_for_timeout(300)
    pg.fill("#cbi", "AIX에 Tomcat 되나?")
    pg.click("#cbb")
    pg.wait_for_timeout(400)
    print("  [chat ] 응답:", pg.query_selector_all(".msg.bot")[-1].inner_text()[:60].replace("\n", " "))

    # CSP 하에서 CSV 다운로드
    pg.click('button[data-t="asset"]')
    pg.wait_for_timeout(400)
    try:
        with pg.expect_download(timeout=12000) as di:
            pg.click("#afx")
        print("  [csv  ] 다운로드 OK:", di.value.suggested_filename)
    except Exception as e:
        print("  [csv  ] 실패:", str(e)[:90])

    b.close()

srv.shutdown()
print("\n  CSP 위반:", viol[:5] if viol else "없음")
print("  JS 오류 :", errs[:5] if errs else "없음")
