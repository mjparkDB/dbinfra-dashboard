# -*- coding: utf-8 -*-
"""챗봇 질의 자동 테스트"""

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


from playwright.sync_api import sync_playwright



Q = [
    "AIX에 Tomcat 되나?",
    "WebSphere 몇 대?",
    "RHEL 8에 Oracle 19c 가능?",
    "Tomcat 10.1 JDK",
    "Oracle 11g EOS",
    "AIX 표준 스택",
    "전환 우선순위",
    "권고역전 현황",
    "톰캣 표준버전",          # 한글 별칭
    "웹스피어 판정",          # 한글 별칭 + 판정 의도
    "JDK 6 쓰는 서버",
    "Tomcat 8.5 전환",
    "레나 자산 현황",         # LENA 한글
    "존재하지않는제품 표준",   # 실패 케이스
]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(DOCS_URL)
    pg.wait_for_timeout(700)
    pg.click('button[data-t="chat"]')
    pg.wait_for_timeout(400)

    for q in Q:
        pg.fill("#cbi", q)
        pg.click("#cbb")
        pg.wait_for_timeout(260)
        msgs = pg.query_selector_all(".msg.bot")
        last = msgs[-1]
        title = last.query_selector("h4")
        title = title.inner_text() if title else "(제목없음)"
        txt = last.inner_text().replace("\n", " ")[:110]
        rows = len(last.query_selector_all("tbody tr"))
        print(f"  Q: {q}")
        print(f"     → [{title}] 표{rows}행 · {txt[:95]}")

    if errs:
        print("\n  [JS 오류]", errs[:5])
    else:
        print("\n  JS 오류 없음")
    pg.screenshot(path=_os.path.join(_R, "shot_chat_qa.png"))
    b.close()
