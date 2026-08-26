# -*- coding: utf-8 -*-
"""
봉투 암호화 (envelope encryption)

  · 데이터키 K 를 무작위 생성하고 자산 데이터를 AES-256-GCM 으로 암호화
  · 사용자마다 K 를 자기 KEK(비밀번호 파생키)로 감싸서 보관
  · 로그인 시 비밀번호 → KEK → K 복호 → 데이터 복호

파일에는 암호문만 들어갑니다. view-source·curl 로 열어도 자산 정보가 보이지 않습니다.
"""
import os
import json
import base64
import hashlib
import binascii
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

B64 = lambda b: base64.b64encode(b).decode()
HEX = lambda b: binascii.hexlify(b).decode()
UNHEX = binascii.unhexlify


def derive_kek(password: str, salt_hex: str, iters: int) -> bytes:
    """비밀번호 → 키암호화키(KEK)"""
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                               UNHEX(salt_hex), iters, 32)


def pack(data_obj, users, iterations):
    """
    users: [{id, name, role, salt, kek(hex)}]
    반환: 포털에 넣을 ENC 구조
    """
    payload = json.dumps(data_obj, ensure_ascii=False,
                         separators=(",", ":")).encode("utf-8")

    K = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    ct = AESGCM(K).encrypt(nonce, payload, None)

    wrapped = []
    for u in users:
        kek = UNHEX(u["kek"])
        wn = os.urandom(12)
        wk = AESGCM(kek).encrypt(wn, K, None)
        wrapped.append({
            "id": u["id"], "name": u.get("name", u["id"]), "role": u["role"],
            "salt": u["salt"], "n": HEX(wn), "wk": B64(wk),
        })

    return {
        "v": 1,
        "iter": iterations,
        "p": {"n": HEX(nonce), "c": B64(ct)},
        "u": wrapped,
    }


def selftest():
    """Python 으로 봉인하고 Python 으로 풀어 왕복 확인"""
    iters = 1000
    pw = "test-password-1234"
    salt = HEX(os.urandom(16))
    kek = derive_kek(pw, salt, iters)
    users = [{"id": "u1", "name": "테스트", "role": "admin",
              "salt": salt, "kek": HEX(kek)}]
    obj = {"hello": "안녕", "n": [1, 2, 3]}
    enc = pack(obj, users, iters)

    # 복호
    u = enc["u"][0]
    kek2 = derive_kek(pw, u["salt"], enc["iter"])
    K = AESGCM(kek2).decrypt(UNHEX(u["n"]), base64.b64decode(u["wk"]), None)
    pt = AESGCM(K).decrypt(UNHEX(enc["p"]["n"]),
                           base64.b64decode(enc["p"]["c"]), None)
    got = json.loads(pt)
    assert got == obj, got
    print("  왕복 검증 OK ·", got)
    print("  암호문에 평문 없음:", "안녕" not in enc["p"]["c"])


if __name__ == "__main__":
    selftest()
