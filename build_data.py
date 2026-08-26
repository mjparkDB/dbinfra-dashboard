# -*- coding: utf-8 -*-
"""
추출 데이터 -> 포털용 JSON 가공
· 서버명 비식별
· 자산 판정(표준준수/전환권장/전환대상)
· 권고역전 탐지
· 제품명 정규화(자산 원장 <-> 표준 마스터 매칭)
"""
import re
import json
from collections import Counter, defaultdict
from extract import load, os_family, os_short, vcmp, same_line, clean_ver, COMPAT_COLS

# ─────────────────────────────────────────────
# 제품명 정규화 — 자산원장 표기 != 표준마스터 표기
# ─────────────────────────────────────────────
CANON = [
    (r"oracle\s*\(?(enterprise|standard)", "Oracle Database"),
    (r"^oracle\b(?!.*linux)",              "Oracle Database"),
    (r"ms-?\s*sql|sql\s*server",           "MS SQL Server"),
    (r"postgres",                          "PostgreSQL"),
    (r"maria",                             "MariaDB"),
    (r"\bmysql\b",                         "MySQL"),
    (r"hana",                              "SAP HANA"),
    (r"tibero",                            "Tibero"),
    (r"tomcat",                            "Apache Tomcat"),
    (r"websphere|^was\b",                  "IBM WebSphere"),
    (r"\bihs\b|ibm http",                  "IBM HTTP Server (IHS)"),
    (r"jeus",                              "TmaxSoft JEUS"),
    (r"webtob",                            "TmaxSoft WebtoB"),
    (r"lena\s*was",                        "LENA WAS (LG CNS)"),
    (r"lena\s*web",                        "LENA WEB (LG CNS)"),
    (r"jboss",                             "Red Hat JBoss EAP"),
    (r"weblogic",                          "Oracle WebLogic"),
    (r"nginx",                             "Nginx"),
    (r"\biis\b",                           "Microsoft IIS"),
    (r"apache",                            "Apache HTTP Server"),
    (r"mosquit",                           "Mosquitto (MQTT)"),
    (r"odm|decision manager",              "IBM ODM"),
]


def canon(name):
    s = (name or "").strip().lower()
    if not s:
        return ""
    for pat, out in CANON:
        if re.search(pat, s):
            return out
    return (name or "").strip()


def base_family(base):
    """01시트 'Linux (RHEL·Rocky·OL)' -> 'Linux'"""
    s = (base or "").lower()
    if "aix" in s:
        return "AIX"
    if "windows" in s:
        return "Windows"
    if "linux" in s:
        return "Linux"
    return base


# ─────────────────────────────────────────────
# 자산 판정
# ─────────────────────────────────────────────
def verdict(a):
    """EOS 도래/업데이트 불가 -> 전환대상, 상향 가능 -> 전환권장, 그 외 준수"""
    if a["eos"].upper() == "O":
        return "전환대상"
    u = a["upd"]
    if u.startswith("불가"):
        return "전환대상"
    if u.startswith("가능"):
        return "전환권장"
    if u in ("불필요", "해당없음", "", "-"):
        return "표준준수"
    return "검토"


def prio(a, v):
    """조치 우선순위 — 컨텍스트팩 4.3"""
    if v != "전환대상":
        return 3 if v == "전환권장" else 4
    if a["eos"].upper() == "O" or "EOL" in a["reason"].upper():
        return 1
    return 2


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────
def build(xlsx):
    d = load(xlsx)

    # ── 표준 마스터
    std = []
    for s in d["std"]:
        std.append({
            "fam":   base_family(s["base"]),
            "base":  s["base"],
            "layer": s["layer"],
            "prod":  s["prod"],
            "canon": canon(s["prod"]),
            "std":   s["std"],
            "floor": s["floor"],
            "jdk":   s["jdk"],
            "eos":   s["eos"],
            "note":  s["note"],
        })

    # 조회 인덱스: (fam, canon) -> 표준행
    sidx = {}
    for s in std:
        sidx.setdefault((s["fam"], s["canon"]), s)

    # ── 자산
    assets = []
    inv_seen = {}          # 권고역전 집계
    for a in d["assets"]:
        fam = os_family(a["os"])
        cn = canon(a["prod"])
        v = verdict(a)
        # 표준 대조
        srow = sidx.get((fam, cn))
        floor = srow["floor"] if srow else ""
        stdv = srow["std"] if srow else ""
        # 하한 미달 여부
        below = ""
        if floor and a["cur"]:
            c = vcmp(a["cur"], floor)
            below = "미달" if c == -1 else ("충족" if c is not None else "")
        # 권고역전: 원장 권고버전 < 현재버전 (같은 라인일 때만)
        if a["rec"] and a["cur"] and same_line(a["rec"], a["cur"]):
            if vcmp(a["rec"], a["cur"]) == -1:
                k = f"{cn}|{a['cur']}|{a['rec']}"
                inv_seen[k] = inv_seen.get(k, 0) + 1
        assets.append([
            a["id"],                       # 0
            a["layer"],                    # 1
            a["env"],                      # 2
            a["sys"],                      # 3
            a["os"],                       # 4
            fam,                           # 5
            os_short(a["os"]),             # 6
            a["prod"],                     # 7
            cn,                            # 8
            a["jdk"],                      # 9
            a["cur"],                      # 10
            a["rec"],                      # 11
            a["eosdate"],                  # 12
            a["eos"],                      # 13
            a["upd"],                      # 14
            a["reason"],                   # 15
            a["dual"],                     # 16
            v,                             # 17 판정
            prio(a, v),                    # 18 우선순위
            floor,                         # 19 표준하한
            stdv,                          # 20 표준지정
            below,                         # 21 하한 충족/미달
        ])

    # ── 데이터 품질 점검
    dq = []
    noVer = [a[0] for a in assets if not clean_ver(a[10])]
    noOS  = [a[0] for a in assets if not a[4]]
    noRec = [a[0] for a in assets if not a[11]]
    if noVer: dq.append({"k": "현재버전 형식 불량·미기재", "n": len(noVer),
                         "ex": noVer[:6], "why": "버전 대조·역전 판정에서 제외됩니다."})
    if noOS:  dq.append({"k": "OS 미기재", "n": len(noOS),
                         "ex": noOS[:6], "why": "OS 기반 표준 매칭이 불가합니다."})
    if noRec: dq.append({"k": "권고버전 미기재", "n": len(noRec),
                         "ex": noRec[:6], "why": "전환 목표가 지정되지 않았습니다."})

    inversions = [{"prod": k.split("|")[0], "cur": k.split("|")[1],
                   "rec": k.split("|")[2], "n": n}
                  for k, n in sorted(inv_seen.items(), key=lambda x: -x[1])]

    # ── 호환성
    compat = [{"cat": c["cat"], "prod": c["prod"], "canon": canon(c["prod"]),
               "ver": c["ver"], "syms": c["syms"], "note": c["note"]}
              for c in d["compat"]]

    jdk = [{"prod": j["prod"], "canon": canon(re.sub(r"[\d.]+$", "", j["prod"])),
            "min": j["min"], "rec": j["rec"], "obs": j["obs"], "note": j["note"]}
           for j in d["jdk"]]

    eol = [{"prod": e["prod"], "canon": canon(e["prod"]), "ver": e["ver"],
            "eos": e["eos"], "state": e["state"], "action": e["action"]}
           for e in d["eol"]]

    return {
        "meta": {
            "src": "ITS_Master_v2_1.xlsx",
            "dept": "인프라운영파트",
            "docno": "ITS-VER-2026-MASTER-v2.1",
            "nAsset": len(assets),
            "nDropped": len(d["dropped"]),
        },
        "std": std,
        "assets": assets,
        "compat": compat,
        "compatCols": COMPAT_COLS,
        "jdk": jdk,
        "eol": eol,
        "swNames": d["sw_names"],
        "sw": d["sw"],
        "inversions": inversions,
        "dq": dq,
    }


if __name__ == "__main__":
    D = build("ITS_Master_v2_1.xlsx")
    A = D["assets"]
    print(f"자산 {len(A)}건 / 표준 {len(D['std'])}행 / 호환성 {len(D['compat'])}행")
    print("\n[판정]", dict(Counter(r[17] for r in A)))
    print("[OS계열]", dict(Counter(r[5] for r in A)))
    print("[계층]", dict(Counter(r[1] for r in A)))
    print("[하한대조]", dict(Counter(r[21] for r in A)))
    matched = sum(1 for r in A if r[19])
    print(f"\n표준 매칭된 자산: {matched}/{len(A)} ({matched/len(A)*100:.0f}%)")
    unm = Counter(f"{r[5]}|{r[8]}" for r in A if not r[19])
    print("미매칭 상위:", unm.most_common(8))
    print(f"\n권고역전 {len(D['inversions'])}종:")
    for i in D["inversions"][:6]:
        print(f"  {i['prod']}: 현재 {i['cur']} > 권고 {i['rec']}  ({i['n']}건)")
