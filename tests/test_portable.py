# -*- coding: utf-8 -*-
"""포터블 기능 검증 — 엑셀 업로드 · 편집 · 저장유지 · 내보내기"""

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
XLSX = XLSX

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(1200)
    _login(pg)

    print("── 초기 상태 ──")
    print("  SheetJS 로드:", pg.evaluate("typeof XLSX !== 'undefined'"))
    print("  파서 로드   :", pg.evaluate("typeof P.parseWorkbook === 'function'"))
    print("  자산        :", pg.evaluate("DATA.assets.length"), "건")

    print("\n── 엑셀 업로드 ──")
    pg.click('button[data-t="data"]')
    pg.wait_for_timeout(500)
    pg.set_input_files("#fin", XLSX)
    pg.wait_for_timeout(2500)
    print("  결과:", pg.inner_text("#fmsg")[:80])
    print("  자산:", pg.evaluate("DATA.assets.length"), "건 · 출처:", pg.evaluate("DATA.meta.src"))
    print("  브라우저 저장:", pg.evaluate("!!localStorage.getItem('its_portal_data_v2')"))

    print("\n── 업로드 후 대시보드 ──")
    pg.click('button[data-t="dash"]')
    pg.wait_for_timeout(700)
    kpi = pg.eval_on_selector_all(".kpi .v", "els => els.map(e=>e.innerText)")
    print("  KPI:", kpi)

    print("\n── 자산 편집 ──")
    pg.evaluate("location.hash='#asset'")
    pg.wait_for_timeout(700)
    first = pg.evaluate("DATA.assets[0][0]")
    before = pg.evaluate("DATA.assets.find(r=>r[0]==='%s').slice(17,19)" % first)
    print(f"  대상 {first} · 편집 전 판정/순위: {before}")
    pg.evaluate(f"openAsset('{first}')")
    pg.wait_for_timeout(500)
    pg.click("#oedit")
    pg.wait_for_timeout(400)
    # 업데이트 가능여부를 '불가'로 -> 전환대상 되어야
    pg.select_option('[data-i="14"]', "불가")
    pg.fill('[data-i="15"]', "테스트 편집 · EOL")
    pg.click("#esave")
    pg.wait_for_timeout(900)
    after = pg.evaluate("DATA.assets.find(r=>r[0]==='%s').slice(17,19)" % first)
    print(f"  편집 후 판정/순위: {after}")
    print("  수정 표시:", "수정됨" in pg.inner_text("#tmeta"))

    print("\n── 새로고침 후 유지 ──")
    pg.reload()
    pg.wait_for_timeout(1400)
    keep = pg.evaluate("DATA.assets.find(r=>r[0]==='%s').slice(17,19)" % first)
    print("  판정/순위:", keep, "· 유지:", keep == after)

    print("\n── 엑셀 내보내기 ──")
    pg.evaluate("location.hash='#data'")
    pg.wait_for_timeout(700)
    with pg.expect_download(timeout=20000) as di:
        pg.click("#dxlsx")
    d = di.value
    d.save_as(_os.path.join(_R, "export_test.xlsx"))
    print("  파일:", d.suggested_filename)

    print("\n── 되돌리기 ──")
    pg.on("dialog", lambda dlg: dlg.accept())
    pg.click("#dreset")
    pg.wait_for_timeout(1200)
    rst = pg.evaluate("DATA.assets.find(r=>r[0]==='%s').slice(17,19)" % first)
    print("  판정/순위:", rst, "· 원복:", rst == before)
    print("  저장 삭제:", not pg.evaluate("!!localStorage.getItem('its_portal_data_v2')"))

    print("\n  JS 오류:", errs[:4] or "없음")
    b.close()
