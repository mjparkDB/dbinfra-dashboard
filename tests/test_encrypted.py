# -*- coding: utf-8 -*-
"""봉투 암호화 배포본 검증 — 로그인 전 데이터 비노출 · 복호 · 오답 차단"""
import os, sys, json, subprocess, tempfile, shutil
from playwright.sync_api import sync_playwright

_R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(_R, "sample", "ITS_Master_sample.xlsx")
OUT = os.path.join(_R, "dist", "_enc_test.html")

PW_OK = "test-admin-pw-9911"
PW_NG = "wrong-password-0000"

# ── 임시 계정으로 암호화 빌드 ──
import hashlib, binascii
ITER = 200_000
salt = binascii.hexlify(os.urandom(16)).decode()
kek = binascii.hexlify(hashlib.pbkdf2_hmac(
    "sha256", PW_OK.encode(), binascii.unhexlify(salt), ITER, 32)).decode()
cfg = {"enabled": True, "encrypt": True, "iterations": ITER,
       "users": [{"id": "admin", "name": "관리자", "role": "admin",
                  "salt": salt, "hash": kek, "kek": kek}]}

auth_path = os.path.join(_R, "auth.json")
backup = None
if os.path.exists(auth_path):
    backup = auth_path + ".testbak"
    shutil.copy(auth_path, backup)
try:
    with open(auth_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False)

    r = subprocess.run([sys.executable, os.path.join(_R, "build.py"), XLSX, OUT],
                       capture_output=True, text=True, cwd=_R)
    print("── 빌드 ──")
    for ln in r.stdout.strip().split("\n"):
        if any(k in ln for k in ("암호화", "출력", "로그인")):
            print("  " + ln.strip())
    assert os.path.exists(OUT), "빌드 실패\n" + r.stdout + r.stderr

    # ── 파일 안에 평문이 있는지 ──
    src = open(OUT, encoding="utf-8").read()
    leaks = [k for k in ("대외연계", "통합포털", "WAS-001", "고객관리", "청구지급")
             if k in src]
    print("\n── 파일 내 평문 검사 ──")
    print("  유출 키워드:", leaks or "없음")
    assert not leaks, f"평문 유출: {leaks}"

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 940})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://" + OUT)
        pg.wait_for_timeout(1100)

        print("\n── 로그인 전 ──")
        print("  게이트    :", "표시" if pg.eval_on_selector("#gate", "e=>!e.hidden") else "없음")
        print("  EMBEDDED  :", pg.evaluate("EMBEDDED === null ? 'null (평문 없음)' : '노출!'"))
        print("  자산 건수 :", pg.evaluate("DATA.assets.length"), "건 (0이어야 정상)")
        assert pg.evaluate("EMBEDDED === null")
        assert pg.evaluate("DATA.assets.length") == 0

        print("\n── 틀린 비밀번호 ──")
        pg.fill("#gid", "admin"); pg.fill("#gpw", PW_NG)
        pg.click("#gbtn"); pg.wait_for_timeout(2600)
        print("  메시지:", pg.inner_text("#gmsg")[:34])
        print("  게이트:", "유지" if pg.eval_on_selector("#gate", "e=>!e.hidden") else "뚫림")
        print("  자산  :", pg.evaluate("DATA.assets.length"), "건")
        assert pg.eval_on_selector("#gate", "e=>!e.hidden")
        assert pg.evaluate("DATA.assets.length") == 0

        print("\n── 올바른 비밀번호 ──")
        pg.fill("#gid", "admin"); pg.fill("#gpw", PW_OK)
        pg.click("#gbtn"); pg.wait_for_timeout(3200)
        ok = not pg.eval_on_selector("#gate", "e=>!e.hidden")
        print("  복호  :", "성공" if ok else "실패")
        assert ok, pg.inner_text("#gmsg")
        print("  자산  :", pg.evaluate("DATA.assets.length"), "건")
        print("  KPI   :", pg.eval_on_selector_all(".kpi .v", "e=>e.map(x=>x.innerText)"))
        pg.click('button[data-t="chat"]'); pg.wait_for_timeout(500)
        pg.fill("#cbi", "Tomcat 몇 대?"); pg.click("#cbb"); pg.wait_for_timeout(600)
        print("  챗봇  :", pg.query_selector_all(".msg.bot")[-1].inner_text()[:40].replace("\n", " "))

        print("\n── 새로고침 ──")
        pg.reload(); pg.wait_for_timeout(1300)
        again = pg.eval_on_selector("#gate", "e=>!e.hidden")
        print("  재로그인 요구:", "O (정상)" if again else "X ← 세션에 평문이 남음")
        assert again

        print("\n  JS 오류:", errs[:3] or "없음")
        b.close()
    print("\n  전체 통과")
finally:
    os.remove(auth_path)
    if backup:
        shutil.move(backup, auth_path)
    if os.path.exists(OUT):
        os.remove(OUT)
