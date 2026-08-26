# -*- coding: utf-8 -*-
"""
포털 로그인 계정 설정 생성기

  python3 make_users.py                 대화형으로 계정 추가
  python3 make_users.py --list          현재 계정 목록
  python3 make_users.py --disable       로그인 끄기
  python3 make_users.py --encrypt      봉투 암호화 켜기 (데이터를 암호문으로 저장)
  python3 make_users.py --no-encrypt   끄기

결과는 auth.json 에 저장되며 build.py 가 자동으로 읽어 포털에 넣습니다.
auth.json 은 .gitignore 대상입니다 — 저장소에 올라가지 않습니다.

────────────────────────────────────────────────────────────
  중요 · 이 로그인이 지키는 것과 못 지키는 것
────────────────────────────────────────────────────────────
  지킵니다  · 역할 분리 (조회자가 실수로 데이터를 고치는 것 방지)
            · 화면을 우연히 본 사람의 캐주얼한 접근 억제
  못 지킵니다· (암호화를 끈 경우) HTML 을 텍스트로 열면 데이터가 보입니다

  --encrypt 를 켜면 자산 데이터가 AES-256-GCM 으로 암호화되어
  비밀번호 없이는 view-source·curl 로도 내용을 볼 수 없습니다.
  GitHub Pages 처럼 서버 인증이 없는 곳에 올릴 때는 반드시 켜십시오.

    python3 make_users.py --encrypt
────────────────────────────────────────────────────────────
"""
import os
import sys
import json
import hashlib
import binascii
import getpass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "auth.json")

ITER = 200_000          # PBKDF2 반복 횟수
ROLES = {
    "viewer": "조회자 · 모든 조회 화면 (편집·업로드 불가)",
    "editor": "편집자 · 조회 + 자산 편집 + 내보내기",
    "admin":  "관리자 · 전체 + 데이터 관리(엑셀 업로드·배포본 저장)",
}


def hash_pw(pw: str, salt_hex: str) -> str:
    salt = binascii.unhexlify(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, ITER, 32)
    return binascii.hexlify(dk).decode()


def load():
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            return json.load(f)
    return {"enabled": True, "iterations": ITER, "users": []}


def save(cfg):
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    os.chmod(OUT, 0o600)
    print(f"\n  저장 완료 · {OUT}")
    print("  다음 단계 · python3 build.py <엑셀> <출력경로>")


def cmd_list(cfg):
    if not cfg["users"]:
        print("  등록된 계정이 없습니다.")
        return
    print(f"  로그인 사용: {'켜짐' if cfg.get('enabled') else '꺼짐'}")
    print(f"  데이터 암호화: {'켜짐 (AES-256-GCM)' if cfg.get('encrypt') else '꺼짐'}")
    print(f"  {'아이디':<14}{'이름':<12}{'역할'}")
    print("  " + "─" * 46)
    for u in cfg["users"]:
        print(f"  {u['id']:<14}{u.get('name',''):<12}{u['role']}")


def cmd_add(cfg):
    print("  계정 추가 (빈 아이디로 종료)\n")
    while True:
        uid = input("  아이디      : ").strip()
        if not uid:
            break
        if any(u["id"] == uid for u in cfg["users"]):
            print("    이미 있는 아이디입니다.\n")
            continue
        name = input("  이름        : ").strip() or uid

        print("\n  역할")
        for k, v in ROLES.items():
            print(f"    {k:<8} {v}")
        role = input("  역할 선택   : ").strip().lower()
        if role not in ROLES:
            print("    잘못된 역할입니다. viewer 로 지정합니다.")
            role = "viewer"

        pw = getpass.getpass("  비밀번호    : ")
        if len(pw) < 8:
            print("    8자 이상이어야 합니다.\n")
            continue
        pw2 = getpass.getpass("  비밀번호 확인: ")
        if pw != pw2:
            print("    일치하지 않습니다.\n")
            continue

        salt = binascii.hexlify(os.urandom(16)).decode()
        cfg["users"].append({
            "id": uid, "name": name, "role": role,
            "salt": salt,
            "hash": hash_pw(pw, salt),   # 화면 게이트 검증용
            "kek":  hash_pw(pw, salt),   # 데이터 복호용 (암호화 배포 시)
        })
        print(f"    추가됨 · {uid} ({role})\n")
    return cfg


def main():
    cfg = load()
    args = sys.argv[1:]

    if "--list" in args:
        cmd_list(cfg)
        return
    if "--disable" in args:
        cfg["enabled"] = False
        save(cfg)
        print("  로그인이 꺼졌습니다. 누구나 전체 기능을 씁니다.")
        return
    if "--enable" in args:
        cfg["enabled"] = True
        save(cfg)
        return
    if "--encrypt" in args:
        missing = [u["id"] for u in cfg["users"] if not u.get("kek")]
        if missing:
            print(f"  [오류] KEK 없는 계정: {', '.join(missing)}")
            print("         이 계정들을 다시 만들어야 암호화 빌드를 쓸 수 있습니다.")
            return
        cfg["encrypt"] = True
        save(cfg)
        print("  봉투 암호화 켜짐 — 빌드 시 자산 데이터가 암호문으로 들어갑니다.")
        print("  로그인 전에는 view-source 로도 데이터를 볼 수 없습니다.")
        return
    if "--no-encrypt" in args:
        cfg["encrypt"] = False
        save(cfg)
        print("  봉투 암호화 꺼짐 — 데이터가 평문으로 들어갑니다.")
        return
    if "--encrypt" in args:
        if not cfg["users"]:
            print("  계정이 없습니다. 먼저 계정을 추가하십시오.")
            return
        cfg["encrypt"] = True
        cfg["enabled"] = True
        save(cfg)
        print("  암호화 배포가 켜졌습니다.")
        print("  자산 데이터가 AES-256-GCM 으로 암호화되어 파일에 들어갑니다.")
        print("  비밀번호 없이는 view-source 로도 내용을 볼 수 없습니다.")
        return
    if "--no-encrypt" in args:
        cfg["encrypt"] = False
        save(cfg)
        print("  암호화가 꺼졌습니다. 데이터가 평문으로 들어갑니다.")
        return

    print(__doc__.split("────")[0])
    if cfg["users"]:
        cmd_list(cfg)
        print()
    cfg = cmd_add(cfg)
    cfg["enabled"] = bool(cfg["users"])
    cfg["iterations"] = ITER

    if not cfg["users"]:
        print("  등록된 계정이 없어 로그인이 꺼진 상태로 저장합니다.")
    save(cfg)
    print()
    if not cfg.get("encrypt"):
        print("  ※ 암호화가 꺼져 있습니다. HTML 을 텍스트로 열면 데이터가 보입니다.")
        print("    공개된 곳(GitHub Pages 등)에 올리려면 암호화를 켜십시오.")
        print("      python3 make_users.py --encrypt")
    print()
    print("  ※ auth.json 은 비밀 파일입니다. 공유·커밋하지 마십시오.")


if __name__ == "__main__":
    main()
