#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
커밋 전 사전 점검

  python3 preflight.py

GitHub 에 올리기 전에 민감 정보가 섞여 있지 않은지 확인합니다.
  · 커밋 대상에 실 데이터·인증 파일이 없는지
  · docs/index.html 에 평문 자산 데이터가 들어있지 않은지
  · 필수 파일이 빠지지 않았는지
"""
import os
import re
import sys
import json
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

OK, WARN, BAD = "  [OK]  ", "  [확인]", "  [위험]"
issues, warns = [], []


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()


print("=" * 62)
print("  커밋 전 사전 점검")
print("=" * 62)

# ── 1. git 상태 ──────────────────────────────────────
print("\n[1] 커밋 대상 파일")
if not os.path.isdir(".git"):
    print(WARN, "git 저장소가 아직 아닙니다 (git init 전)")
    tracked = []
else:
    run("git add -A -n")   # dry-run
    tracked = [l.split(maxsplit=1)[-1].strip('"')
               for l in run("git status --porcelain").split("\n") if l.strip()]
    print(f"        {len(tracked)}개 파일")

DANGER_PAT = [
    (r"\.xlsx$",              "엑셀 자산 파일"),
    (r"\.xlsm$",              "엑셀 자산 파일"),
    (r"^auth\.json$",         "실 계정 · 복호 키 재료"),
    (r"\.htpasswd$",          "서버 인증 계정"),
    (r"^dist/",               "실 데이터 빌드 산출물"),
    (r"자산현황_.*\.csv$",     "내보낸 자산 목록"),
    (r"포털백업_.*\.json$",    "데이터 백업"),
    (r"^docker/html/index\.html$", "실 데이터 배포본"),
]
found = []
for f in tracked:
    for pat, why in DANGER_PAT:
        if re.search(pat, f):
            # 샘플 엑셀은 허용
            if f == "sample/ITS_Master_sample.xlsx":
                continue
            found.append((f, why))
            break
if found:
    for f, why in found:
        print(BAD, f"{f}  ← {why}")
    issues.append(f"민감 파일 {len(found)}건이 커밋 대상입니다")
else:
    print(OK, "민감 파일 없음")

# ── 2. docs/index.html 내용 ──────────────────────────
print("\n[2] 배포본 (docs/index.html)")
doc = os.path.join("docs", "index.html")
if not os.path.exists(doc):
    print(BAD, "파일이 없습니다 · python3 build.py 를 먼저 실행하십시오")
    issues.append("docs/index.html 없음")
else:
    src = open(doc, encoding="utf-8").read()
    size = len(src)
    enc = "const ENC  = {" in src
    print(f"        크기 {size:,} bytes · {'암호화본' if enc else '평문본'}")

    # 데이터 출처 확인
    m = re.search(r'"src":"([^"]*)"', src)
    srcname = m.group(1) if m else "?"
    is_sample = srcname == "ITS_Master_sample.xlsx"
    print(f"        데이터 출처 · {srcname}")

    if enc:
        print(OK, "암호화 배포본 — 평문 자산 없음")
    elif is_sample:
        print(OK, "샘플 데이터 — 공개해도 안전")
    else:
        print(BAD, "실 데이터가 평문으로 들어있습니다")
        issues.append("docs/index.html 에 평문 실 데이터")

    # 계정 해시 노출
    ma = re.search(r"const AUTH = (\{.*?\});", src, re.S)
    if ma:
        try:
            a = json.loads(ma.group(1))
            if a.get("enabled"):
                kind = "데모" if a.get("demo") else "실계정"
                n = len(a.get("users", []))
                print(f"        로그인 · {kind} {n}개")
                if not a.get("demo") and n:
                    print(WARN, "실계정 해시가 공개 파일에 들어갑니다")
                    warns.append("실계정 해시 노출 — 데모 계정 사용 권장")
            else:
                print("        로그인 · 사용 안 함")
        except Exception:
            pass

# ── 3. 필수 파일 ─────────────────────────────────────
print("\n[3] 필수 파일")
NEED = ["build.py", "extract.py", "build_data.py", "README.md", ".gitignore",
        "requirements.txt", "sample/make_sample.py",
        "vendor/xlsx.full.min.js",
        "templates/tpl_head.html", "templates/tpl_auth.html",
        "templates/tpl_parse.html", "templates/tpl_js.html",
        "templates/tpl_ref.html", "templates/tpl_data.html",
        "templates/tpl_chat.html",
        ".github/workflows/build.yml"]
missing = [f for f in NEED if not os.path.exists(f)]
if missing:
    for f in missing:
        print(BAD, f"없음 · {f}")
    issues.append(f"필수 파일 {len(missing)}건 누락")
else:
    print(OK, f"{len(NEED)}개 모두 존재")

# ── 4. .gitignore 동작 ───────────────────────────────
print("\n[4] .gitignore 차단 확인")
if os.path.isdir(".git"):
    checks = ["auth.json", "docker/.htpasswd", "dist/x.html", "실데이터.xlsx"]
    for c in checks:
        blocked = subprocess.run(f"git check-ignore -q '{c}'", shell=True).returncode == 0
        print((OK if blocked else BAD), f"{c:<24} {'차단' if blocked else '통과 ← 위험'}")
        if not blocked:
            issues.append(f".gitignore 가 {c} 를 막지 못합니다")
else:
    print(WARN, "git init 후 다시 확인하십시오")

# ── 결과 ─────────────────────────────────────────────
print("\n" + "=" * 62)
if issues:
    print("  중단 — 아래를 먼저 해결하십시오")
    for i in issues:
        print("   ·", i)
    print("=" * 62)
    sys.exit(1)
if warns:
    print("  주의사항이 있습니다")
    for w in warns:
        print("   ·", w)
print("  이상 없음 — 커밋해도 됩니다")
print("=" * 62)
