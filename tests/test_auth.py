# -*- coding: utf-8 -*-
"""로그인 · 역할별 권한 검증"""
from playwright.sync_api import sync_playwright

# ── 저장소 기준 경로 ──
import os as _os
_R = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DOCS = _os.path.join(_R, "docs", "index.html")
DOCS_URL = "file://" + DOCS

# auth.demo.json 기준 (비밀번호 = 아이디)
ACCOUNTS = [
    ("viewer", "viewer", "viewer"),
    ("editor", "editor", "editor"),
    ("admin",  "admin",  "admin"),
]


def login(pg, uid, pw):
    pg.fill("#gid", uid)
    pg.fill("#gpw", pw)
    pg.click("#gbtn")
    pg.wait_for_timeout(1600)          # PBKDF2 20만회


with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []

    print("── 게이트 노출 ──")
    ctx = b.new_context(viewport={"width": 1440, "height": 950})
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(DOCS_URL)
    pg.wait_for_timeout(1000)
    print("  로그인 화면:", "표시" if pg.eval_on_selector("#gate", "e=>!e.hidden") else "없음")
    print("  본문 렌더  :", len(pg.inner_text("#tab-dash")), "자 (0이어야 정상)")

    print("\n── 잘못된 비밀번호 ──")
    login(pg, "admin", "wrongpw123")
    print("  메시지:", pg.inner_text("#gmsg")[:36])
    print("  게이트:", "유지" if pg.eval_on_selector("#gate", "e=>!e.hidden") else "뚫림")
    ctx.close()

    for uid, pw, role in ACCOUNTS:
        print(f"\n── {role} 로그인 ──")
        ctx = b.new_context(viewport={"width": 1440, "height": 950})
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errs.append(f"{role}: {e}"))
        pg.goto(DOCS_URL)
        pg.wait_for_timeout(900)
        login(pg, uid, pw)

        gate = pg.eval_on_selector("#gate", "e=>!e.hidden")
        print("  로그인:", "실패" if gate else "성공")
        if gate:
            print("  메시지:", pg.inner_text("#gmsg")[:40])
            ctx.close()
            continue

        print("  표시   :", pg.inner_text("#who").replace("\n", " ")[:26])
        print("  대시보드:", len(pg.inner_text("#tab-dash")), "자")

        # 데이터 관리 탭
        dt = pg.eval_on_selector('.tabs button[data-t="data"]', "e=>!e.hidden")
        print(f"  데이터관리 탭: {'보임' if dt else '숨김':<4} (admin만 보여야 정상)")

        # CSV 버튼
        pg.evaluate("location.hash='#asset'")
        pg.wait_for_timeout(700)
        csv = pg.query_selector("#afx") is not None
        print(f"  CSV 내보내기 : {'있음' if csv else '없음':<4} (editor 이상)")

        # 편집 버튼
        pg.evaluate("openAsset(DATA.assets[0][0])")
        pg.wait_for_timeout(500)
        ed = pg.query_selector("#oedit") is not None
        print(f"  편집 버튼    : {'있음' if ed else '없음':<4} (editor 이상)")

        # 세션 유지
        pg.reload()
        pg.wait_for_timeout(1100)
        kept = not pg.eval_on_selector("#gate", "e=>!e.hidden")
        print("  새로고침 유지:", "O" if kept else "X")

        # 로그아웃
        if kept:
            pg.click("#lgout")
            pg.wait_for_timeout(1200)
            out = pg.eval_on_selector("#gate", "e=>!e.hidden")
            print("  로그아웃     :", "게이트 복귀" if out else "실패")
        ctx.close()

    print("\n  JS 오류:", errs[:4] or "없음")
    b.close()
