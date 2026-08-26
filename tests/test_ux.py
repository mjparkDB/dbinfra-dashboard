# -*- coding: utf-8 -*-
"""드릴다운 · 정렬 · 해시라우팅 · 인쇄 동작 검증"""

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



URL = DOCS_URL

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(900)
    _login(pg)

    print("── KPI 드릴다운 ──")
    pg.eval_on_selector_all(".kpi.dd", "els => els[1].click()")   # 전환대상
    pg.wait_for_timeout(600)
    tab = pg.eval_on_selector(".tabs button.on", "e => e.dataset.t")
    print(f"  전환대상 KPI 클릭 → 탭={tab} · {pg.inner_text('#afc')}")
    print(f"  판정 필터값: '{pg.input_value('#af_v')}'")

    print("\n── 막대 드릴다운 ──")
    pg.click('button[data-t="dash"]')
    pg.wait_for_timeout(500)
    pg.eval_on_selector_all(".bar.dd", "els => els[3].click()")   # OS 계열 첫번째
    pg.wait_for_timeout(600)
    print(f"  탭={pg.eval_on_selector('.tabs button.on','e=>e.dataset.t')} · {pg.inner_text('#afc')}")
    print(f"  OS 필터값: '{pg.input_value('#af_fam')}'")

    print("\n── 업무별 위험도 링크 ──")
    pg.click('button[data-t="dash"]')
    pg.wait_for_timeout(500)
    risk = pg.eval_on_selector_all(".risk .lnk", "els => els.length")
    first = pg.eval_on_selector(".risk .risk-n", "e => e.innerText")
    pg.eval_on_selector_all(".risk .lnk", "els => els[0].click()")
    pg.wait_for_timeout(600)
    print(f"  위험도 항목 {risk}개 · 1위='{first[:24]}'")
    print(f"  클릭 후 → {pg.inner_text('#afc')} · 검색어='{pg.input_value('#afq')}'")

    print("\n── 표 정렬 ──")
    pg.click('button[data-t="asset"]')
    pg.wait_for_timeout(500)
    pg.eval_on_selector("#afreset", "e => e.click()")
    pg.wait_for_timeout(400)
    before = pg.eval_on_selector_all("#afr tbody tr td:first-child",
                                     "els => els.slice(0,3).map(e=>e.innerText)")
    ths = pg.eval_on_selector_all("#afr thead th.so", "els => els.length")
    pg.eval_on_selector_all("#afr thead th", "els => els[5].click()")  # 제품 정렬
    pg.wait_for_timeout(500)
    after = pg.eval_on_selector_all("#afr tbody tr td:nth-child(6)",
                                    "els => els.slice(0,3).map(e=>e.innerText)")
    print(f"  정렬 가능 헤더 {ths}개")
    print(f"  제품 오름차순 상위3: {after}")

    print("\n── 해시 라우팅 ──")
    pg.click('button[data-t="mtx"]')
    pg.wait_for_timeout(400)
    print(f"  탭 전환 후 URL 해시: {pg.evaluate('location.hash')}")
    pg.evaluate("location.hash = '#jdk'")
    pg.wait_for_timeout(500)
    print(f"  해시 직접 변경 → 활성탭: {pg.eval_on_selector('.tabs button.on','e=>e.dataset.t')}")
    pg.reload()
    pg.wait_for_timeout(800)
    print(f"  새로고침 후 활성탭: {pg.eval_on_selector('.tabs button.on','e=>e.dataset.t')}")

    print("\n── 키보드 탭 이동 ──")
    pg.evaluate("location.hash='#dash'")
    pg.wait_for_timeout(400)
    pg.eval_on_selector(".tabs button.on", "e => e.focus()")
    pg.keyboard.press("ArrowRight")
    pg.wait_for_timeout(400)
    print(f"  → 키: {pg.eval_on_selector('.tabs button.on','e=>e.dataset.t')}")

    print("\n── 챗봇 초기화/복사 ──")
    pg.evaluate("location.hash='#chat'")
    pg.wait_for_timeout(500)
    for sel, nm in [("#cbclear", "초기화"), ("#cbcopy", "복사")]:
        print(f"  {nm}:", "있음" if pg.query_selector(sel) else "없음")

    print("\n  JS 오류:", errs[:4] or "없음")
    b.close()
