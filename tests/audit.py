# -*- coding: utf-8 -*-
"""죽은 UI 감사 — 상호작용 가능해 보이는데 동작 안 하는 요소 탐지"""

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



TABS = ["dash", "std", "mtx", "jdk", "sw", "asset", "patch", "verify", "chat", "data"]

JS = """
() => {
  const out = [];
  const hasH = el => {
    for (const k of ['onclick','onchange','oninput','onkeydown']) if (el[k]) return true;
    if (el.tagName === 'A' && el.getAttribute('href')) return true;
    if (el.tagName === 'BUTTON' || el.tagName === 'SELECT' || el.tagName === 'INPUT') return true;
    return false;
  };
  // 조상에 위임 핸들러가 있는지
  const delegated = el => {
    let p = el;
    while (p && p !== document.body) { if (p.onclick) return true; p = p.parentElement; }
    return false;
  };
  document.querySelectorAll('.tab.on *').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.cursor === 'pointer' && !hasH(el) && !delegated(el)) {
      out.push({tag: el.tagName, cls: el.className, txt: (el.innerText||'').slice(0,40)});
    }
  });
  return out;
}
"""

# 클릭 유도 문구가 있는데 실제 링크가 없는 경우
PROMISE = ["탭에서 확인", "클릭", "확인하십시오", "참고"]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto(DOCS_URL)
    pg.wait_for_timeout(800)
    _login(pg)

    print("── 커서는 pointer인데 핸들러 없는 요소 ──")
    found = False
    for t in TABS:
        pg.click(f'button[data-t="{t}"]')
        pg.wait_for_timeout(400)
        dead = pg.evaluate(JS)
        if dead:
            found = True
            print(f"  [{t}]")
            for d in dead[:5]:
                print(f"     {d['tag']}.{d['cls'][:26]}  '{d['txt'][:30]}'")
    if not found:
        print("  없음")

    print("\n── 클릭 유도 문구 vs 실제 링크 ──")
    for t in TABS:
        pg.click(f'button[data-t="{t}"]')
        pg.wait_for_timeout(350)
        txt = pg.inner_text(f"#tab-{t}")
        for kw in PROMISE:
            if kw in txt:
                links = pg.eval_on_selector_all(
                    f"#tab-{t} a, #tab-{t} [role=button]", "els => els.length")
                print(f"  [{t}] '{kw}' 문구 있음 · 링크요소 {links}개")

    print("\n── 정렬 가능해 보이는 표 헤더 ──")
    pg.click('button[data-t="asset"]')
    pg.wait_for_timeout(400)
    sortable = pg.eval_on_selector_all(
        "#tab-asset thead th",
        "els => els.map(e => ({t: e.innerText, click: !!e.onclick}))")
    print("  헤더", len(sortable), "개 중 정렬 가능:",
          sum(1 for s in sortable if s["click"]))

    print("\n── URL 해시 라우팅 ──")
    pg.click('button[data-t="mtx"]')
    pg.wait_for_timeout(300)
    print("  탭 전환 후 URL:", pg.url.split("/")[-1][:60])

    print("\n── 챗봇 대화 관리 ──")
    pg.click('button[data-t="chat"]')
    pg.wait_for_timeout(300)
    for sel, name in [("#cbclear", "초기화"), ("#cbcopy", "복사")]:
        print(f"  {name} 버튼:", "있음" if pg.query_selector(sel) else "없음")

    b.close()
