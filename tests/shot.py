# -*- coding: utf-8 -*-

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


import sys
from playwright.sync_api import sync_playwright



URL = DOCS_URL
TABS = sys.argv[1:] if len(sys.argv) > 1 else ["dash"]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 1000})
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(900)
    _login(pg)
    for t in TABS:
        if t != "dash":
            pg.click(f'button[data-t="{t}"]')
            pg.wait_for_timeout(600)
        pg.screenshot(path=_os.path.join(_R, f"shot_{t}.png"), full_page=(t in ("dash", "std")))
        print(f"  shot_{t}.png")
    if errs:
        print("\n  [JS 오류]")
        for e in errs[:12]:
            print("   ", e[:200])
    else:
        print("\n  JS 오류 없음")
    b.close()
