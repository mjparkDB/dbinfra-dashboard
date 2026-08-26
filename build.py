# -*- coding: utf-8 -*-
"""
인프라 표준화 포털 빌드

  python3 build.py [엑셀경로] [출력경로]
  기본값: sample/ITS_Master_sample.xlsx → docs/index.html

로그인 설정 우선순위
  1) auth.json        실 계정 — .gitignore 대상
  2) auth.demo.json   데모 계정 — 공개 저장소에 포함
  3) 없으면 로그인 없이 빌드
"""
import sys, json, os
from datetime import datetime
from collections import Counter
from build_data import build
try:
    import crypto_pack
except ImportError:
    crypto_pack = None

HERE = os.path.dirname(os.path.abspath(__file__))
TPL_DIR = os.path.join(HERE, "templates")
VENDOR = os.path.join(HERE, "vendor", "xlsx.full.min.js")
AUTH_FILE = os.path.join(HERE, "auth.json")
AUTH_DEMO = os.path.join(HERE, "auth.demo.json")

TEMPLATES = (
    "tpl_head.html", "tpl_auth.html", "tpl_parse.html", "tpl_js.html",
    "tpl_ref.html", "tpl_data.html",
    "tpl_chat.html",     # 라우팅·부팅 포함 — 반드시 마지막
)


def load_auth():
    """(공개설정, 원본설정, 출처설명) 반환 — kek 은 공개설정에서 제외합니다."""
    src = AUTH_FILE if os.path.exists(AUTH_FILE) else (
        AUTH_DEMO if os.path.exists(AUTH_DEMO) else None)
    if not src:
        return {"enabled": False, "users": []}, {}, "없음"
    with open(src, encoding="utf-8") as fp:
        cfg = json.load(fp)
    users = cfg.get("users", [])
    out = {
        "enabled": bool(cfg.get("enabled") and users),
        "demo": bool(cfg.get("demo")),
        "iterations": cfg.get("iterations", 200000),
        "hints": cfg.get("hints", []) if cfg.get("demo") else [],
        "users": [{k: u[k] for k in ("id", "name", "role", "salt", "hash") if k in u}
                  for u in users],
    }
    return out, cfg, os.path.basename(src)


def main():
    xlsx = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HERE, "sample", "ITS_Master_sample.xlsx")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "docs", "index.html")

    if not os.path.exists(xlsx):
        print(f"[오류] 엑셀 파일이 없습니다: {xlsx}")
        print("       샘플 생성: python3 sample/make_sample.py")
        sys.exit(1)

    # ── 안전장치 ──
    # docs/ 는 GitHub Pages 공개 경로입니다. 실 데이터를 여기에 쓰면 공개됩니다.
    is_sample = os.path.basename(xlsx) == "ITS_Master_sample.xlsx"
    in_docs = os.path.abspath(out).startswith(os.path.join(HERE, "docs") + os.sep)
    _a, _raw, _ = load_auth()
    _enc_ok = bool(_a["enabled"] and _raw.get("encrypt")
                   and all(u.get("kek") for u in _raw.get("users", [])))
    if in_docs and not is_sample and not _enc_ok:
        print()
        print("  " + "=" * 62)
        print("  [중단] docs/ 는 GitHub Pages 공개 경로입니다.")
        print(f"         입력 파일이 샘플이 아닙니다 · {os.path.basename(xlsx)}")
        print()
        print("         실 데이터는 저장소 밖이나 dist/ 로 출력하십시오.")
        print("         또는 봉투 암호화를 켜십시오 · python3 make_users.py --encrypt")
        print(f"         예: python3 build.py {os.path.basename(xlsx)} dist/portal.html")
        print("  " + "=" * 62)
        print()
        sys.exit(2)

    print(f"  입력 : {xlsx}")
    D = build(xlsx)
    D["meta"]["built"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    D["meta"]["src"] = os.path.basename(xlsx)

    # ── 로그인 · 암호화 여부 결정 ──
    auth, raw, asrc = load_auth()
    do_enc = bool(auth["enabled"] and raw.get("encrypt")
                  and all(u.get("kek") for u in raw.get("users", [])))
    if do_enc and crypto_pack is None:
        print("[오류] 암호화 빌드에는 cryptography 패키지가 필요합니다.")
        print("       pip install cryptography")
        sys.exit(1)

    parts = []
    for f in TEMPLATES:
        path = os.path.join(TPL_DIR, f)
        if not os.path.exists(path):
            print(f"[오류] 템플릿 없음: {path}")
            sys.exit(1)
        with open(path, encoding="utf-8") as fp:
            parts.append(fp.read())
    html = "\n".join(parts)
    if do_enc:
        enc = crypto_pack.pack(D, raw["users"], auth["iterations"])
        # 평문은 넣지 않습니다 — 로그인 성공 후 브라우저가 복호합니다.
        html = html.replace("__DATA__", "null")
        html = html.replace("__ENC__", json.dumps(enc, separators=(",", ":")))
        auth["users"] = []          # 해시도 넣지 않음 (복호 성공 = 인증)
        print(f"  암호화 : 봉투 암호화 적용 · AES-256-GCM · 계정 {len(enc['u'])}개")
        print("           로그인 전에는 view-source 로도 데이터를 볼 수 없습니다.")
    else:
        html = html.replace("__DATA__", json.dumps(D, ensure_ascii=False, separators=(",", ":")))
        html = html.replace("__ENC__", "null")

    # ── 로그인 ──
    if do_enc:
        pass          # 위에서 이미 출력했습니다
    elif auth["enabled"]:
        kind = "데모" if auth["demo"] else "실계정"
        roles = ", ".join(f"{u['id']}({u['role']})" for u in auth["users"])
        print(f"  로그인 : 사용 · {kind} {len(auth['users'])}개 · {roles}   [{asrc}]")
        if auth["demo"]:
            print("           ※ 데모 계정입니다. 실 운영은 make_users.py 로 auth.json 생성")
    else:
        print(f"  로그인 : 사용 안 함  [{asrc}]")
    html = html.replace("__AUTH__", json.dumps(auth, ensure_ascii=False, separators=(",", ":")))

    if not os.path.exists(VENDOR):
        print(f"[오류] SheetJS 없음: {VENDOR}")
        sys.exit(1)
    with open(VENDOR, encoding="utf-8") as fp:
        html = html.replace("__SHEETJS__", fp.read())

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fp:
        fp.write(html)

    A = D["assets"]
    vc = Counter(r[17] for r in A)
    size = os.path.getsize(out)
    print(f"  출력 : {out}  ({size:,} bytes / {size // 1024} KB)")
    print(f"  자산 {len(A)}건 · 표준 {len(D['std'])}행 · 호환성 {len(D['compat'])}행 "
          f"· JDK {len(D['jdk'])}행 · EOL {len(D['eol'])}행 · 필수SW {len(D['sw'])}행")
    print(f"  판정 : 전환대상 {vc['전환대상']} · 전환권장 {vc['전환권장']} · 표준준수 {vc['표준준수']}")
    print(f"  권고역전 {len(D['inversions'])}종 {sum(i['n'] for i in D['inversions'])}건")
    if D["meta"]["nDropped"]:
        print(f"  제외행 {D['meta']['nDropped']}건")


if __name__ == "__main__":
    main()
