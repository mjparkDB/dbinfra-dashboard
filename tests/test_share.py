# -*- coding: utf-8 -*-
"""공유폴더 시나리오 검증
  담당자: 엑셀 업로드 → 편집 → 배포용 HTML 저장 → 공유폴더 덮어쓰기
  구성원: 공유폴더 HTML 열기 → 최신 데이터 확인
"""

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


import os, shutil
from playwright.sync_api import sync_playwright



SRC = DOCS
SHARE = "/tmp/share2"
XLSX = XLSX

shutil.rmtree(SHARE, ignore_errors=True)
os.makedirs(SHARE)
shutil.copy(SRC, f"{SHARE}/포털.html")

with sync_playwright() as b0:
    br = b0.chromium.launch()

    # ── 담당자 PC
    admin = br.new_context(viewport={"width": 1440, "height": 950},
                           accept_downloads=True)
    pg = admin.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append("admin: " + str(e)))
    pg.goto(f"file://{SHARE}/포털.html")
    pg.wait_for_timeout(1200)
    _login(pg)
    print("── 담당자 ──")
    print("  최초 자산:", pg.evaluate("DATA.assets.length"), "건")

    pg.click('button[data-t="data"]')
    pg.wait_for_timeout(500)
    pg.set_input_files("#fin", XLSX)
    pg.wait_for_timeout(2500)
    print("  엑셀 업로드:", pg.evaluate("DATA.meta.src"))

    # 자산 하나 편집
    tid = pg.evaluate("DATA.assets[0][0]")
    pg.evaluate(f"openAsset('{tid}')")
    pg.wait_for_timeout(400)
    pg.click("#oedit")
    pg.wait_for_timeout(300)
    pg.fill('[data-i="15"]', "담당자 검토 완료 · 배포본 반영")
    pg.select_option('[data-i="14"]', "불가")
    pg.click("#esave")
    pg.wait_for_timeout(800)
    print(f"  {tid} 편집:", pg.evaluate(f"DATA.assets.find(r=>r[0]==='{tid}').slice(17,19)"))

    # 배포용 HTML 저장
    pg.evaluate("document.getElementById('ov').classList.remove('on')")
    pg.evaluate("location.hash='#data'")
    pg.wait_for_timeout(700)
    with pg.expect_download(timeout=30000) as di:
        pg.click("#dhtml")
    dl = di.value
    dl.save_as(f"{SHARE}/포털.html")      # 공유폴더에 덮어쓰기
    size = os.path.getsize(f"{SHARE}/포털.html")
    print(f"  배포본 저장: {dl.suggested_filename} ({size:,} B) → 공유폴더 덮어씀")

    # ── 구성원 PC (완전히 다른 브라우저 컨텍스트)
    print("\n── 구성원 (다른 PC) ──")
    user = br.new_context(viewport={"width": 1440, "height": 950})
    pu = user.new_page()
    pu.on("pageerror", lambda e: errs.append("user: " + str(e)))
    pu.goto(f"file://{SHARE}/포털.html")
    pu.wait_for_timeout(1500)
    print("  자산:", pu.evaluate("DATA.assets.length"), "건")
    print("  출처:", pu.evaluate("DATA.meta.src"))
    got = pu.evaluate(f"DATA.assets.find(r=>r[0]==='{tid}')")
    print(f"  담당자 편집 반영: 판정={got[17]} P{got[18]} · 사유='{got[15][:22]}'")
    pu.click('button[data-t="dash"]')
    pu.wait_for_timeout(700)
    print("  KPI:", pu.eval_on_selector_all(".kpi .v", "e=>e.map(x=>x.innerText)"))
    pu.click('button[data-t="chat"]')
    pu.wait_for_timeout(400)
    pu.fill("#cbi", "Tomcat 몇 대?")
    pu.click("#cbb")
    pu.wait_for_timeout(500)
    print("  챗봇 동작:", pu.eval_on_selector_all("#cbs .msg", "e=>e.length"), "메시지")

    # ── 옛 저장값이 새 배포본을 가리는지
    print("\n── 배포본 교체 감지 ──")
    old = br.new_context(viewport={"width": 1440, "height": 950})
    po = old.new_page()
    po.on("pageerror", lambda e: errs.append("old: " + str(e)))
    po.goto(f"file://{SHARE}/포털.html")
    po.wait_for_timeout(1200)
    # 옛 배포본에서 저장한 것처럼 위조
    po.evaluate("""() => {
      const d = JSON.parse(JSON.stringify(DATA));
      d.meta.baseBuilt = '2020-01-01 00:00';
      d.meta.built = '2020-01-01 00:00';
      d.assets = d.assets.slice(0, 5);
      localStorage.setItem('its_portal_data_v2', JSON.stringify(d));
    }""")
    po.reload()
    po.wait_for_timeout(1500)
    vis = po.eval_on_selector("#banner", "e => !e.hidden")
    print("  안내 배너:", "표시됨" if vis else "없음")
    print("  사용 데이터:", po.evaluate("DATA.assets.length"), "건 (옛 저장분 5건이 아니어야 정상)")
    if vis:
        print("  배너 문구:", po.inner_text("#banner").replace("\n", " ")[:70])

    print("\n  JS 오류:", errs[:4] or "없음")
    br.close()
