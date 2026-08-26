# 인프라 표준화 포털

OS 기반 표준 버전과 자산 현황을 한 화면에서 조회하는 **단일 HTML 대시보드**입니다.
엑셀 마스터파일 하나로 대시보드·호환성 매트릭스·패치가이드·질의 챗봇이 생성됩니다.

외부 통신이 없어 **폐쇄망(air-gap)에서 그대로 동작**합니다.

> **데모** · 로그인 없이 배포하면 **샘플(더미) 데이터**가 공개됩니다.
> 실 데이터를 웹에 올리려면 반드시 **암호화 배포**를 쓰십시오 → [로그인](#로그인)

---

## 빠른 시작

```bash
pip install -r requirements.txt

python3 sample/make_sample.py        # 샘플 마스터파일 생성 (시드 고정)
python3 build.py                     # → docs/index.html
```

생성된 `docs/index.html` 을 브라우저로 열면 됩니다. 서버 불필요.

실제 데이터로 만들려면 **출력 경로를 반드시 지정**하십시오.
`docs/` 는 공개 경로라 샘플 외에는 빌드가 차단됩니다.

```bash
python3 build.py /사내경로/ITS_Master.xlsx dist/portal.html
```

---

## 화면

| 탭 | 내용 |
| --- | --- |
| 대시보드 | KPI · 분포 · 업무별 위험도 · 권고역전 · 데이터 품질 |
| 표준 버전 | OS 기반별 표준 스택 + 제품별 자산 건수·준수율 |
| 호환성 매트릭스 | 제품 × OS 조합 판정 (◎ ○ △ ✗ ?) |
| JDK 요구 | 제품별 최소·권고 JDK + 구버전 운영 자산 |
| 필수 SW | OS별 백신·백업·모니터링 버전 |
| 자산 조회 | 8중 필터 · 정렬 · CSV 내보내기 · 상세/편집 |
| 패치가이드 | 패치 유형 4종 · 표준 절차 7단계 · 계층별 점검·롤백 |
| 표준화 검증 | 선정 기준 · SPV 6단계 · 하드게이트 · 판정규칙 |
| 질의 챗봇 | 자연어 조회 (별칭 63종 · 의도 9종) |
| 데이터 관리 | 엑셀 업로드 · 편집 · 배포용 HTML 저장 |

정책 문서를 그대로 보여주는 데 그치지 않고, **각 항목의 해당 자산 건수를
현재 원장에서 자동 산출**합니다. 숫자를 클릭하면 해당 자산 목록으로 이동합니다.

---

## 두 가지 갱신 경로

동일한 파싱·판정 로직이 **Python과 브라우저 양쪽에 이식**되어 있어 결과가 같습니다.

| 경로 | 방법 | Python |
| --- | --- | --- |
| 명령줄 | `python3 build.py master.xlsx out.html` | 필요 |
| 브라우저 | 포털 → 데이터 관리 → 엑셀 끌어놓기 | 불필요 |

폐쇄망에서는 브라우저 경로를 쓰면 아무것도 설치할 필요가 없습니다.

---

## 로그인

배포 위치에 따라 방식이 다릅니다.

| 배포 위치 | 권장 방식 | 데이터 보호 |
| --- | --- | --- |
| **GitHub Pages · 웹** | **암호화 + 로그인** | 됨 (AES-256-GCM) |
| 도커 서버 | nginx Basic 인증 | 됨 (파일 자체 차단) |
| 공유폴더 · USB | 로그인만 (역할 분리) | 안 됨 |

### GitHub Pages 에 올릴 때 — 암호화 필수

GitHub Pages 는 **서버 인증이 없습니다.** 화면만 가리는 로그인은
`view-source` 나 `curl` 한 줄로 뚫립니다.
그래서 **자산 데이터 자체를 암호화**합니다.

```bash
python3 make_users.py            # 계정 추가
python3 make_users.py --encrypt   # 암호화 켜기
python3 build.py /사내경로/ITS_Master.xlsx docs/index.html
git add docs/index.html && git commit -m "배포본 갱신" && git push
```

**동작 방식 — 봉투 암호화**

```
무작위 데이터키 K 생성
  자산 데이터  ──AES-256-GCM(K)──▶  암호문        (파일에 들어감)
  K           ──AES-GCM(KEK_홍길동)──▶ 감싼 키      (파일에 들어감)
              ──AES-GCM(KEK_김철수)──▶ 감싼 키
  KEK = PBKDF2-SHA256(비밀번호, salt, 200,000회)
```

각자 **자기 비밀번호로** 같은 데이터를 엽니다. 공용 암호가 필요 없습니다.

파일을 그냥 내려받으면 이것만 보입니다.

```
const ENC = {"v":1,"iter":200000,
  "p":{"n":"3f9a…","c":"k+FKktyAx8zkVFC9K25nepKAdmi4E7CQrzIa0JvUw1zr…"},
  "u":[{"id":"admin","role":"admin","salt":"…","n":"…","wk":"…"}]}
```

자산ID·업무명·버전 어느 것도 평문으로 남지 않습니다.

> **한계** · 파일을 가진 사람은 비밀번호를 오프라인에서 대입할 수 있습니다.
> PBKDF2 20만 회가 이를 느리게 만들지만, **짧거나 흔한 비밀번호는 뚫립니다.**
> 12자 이상, 사전에 없는 문자열을 쓰십시오.
>
> 사내 규정상 자산 정보의 외부 저장이 금지된다면, 암호화 여부와 무관하게
> GitHub 대신 사내 도커 배포를 쓰십시오.

### 역할

| 역할 | 조회 | 자산 편집 · 내보내기 | 데이터 관리 |
| --- | --- | --- | --- |
| viewer (조회자) | O | X | X |
| editor (편집자) | O | O | X |
| admin (관리자) | O | O | O |

암호화 배포본은 데이터키를 저장하지 않으므로 **새로고침하면 다시 로그인**합니다.
평문 배포본은 세션 유지(최대 12시간)를 선택할 수 있습니다.
비밀번호 5회 오류 시 30초 잠깁니다.

### 계정 관리

```bash
python3 make_users.py              # 대화형 추가
python3 make_users.py --list       # 목록 · 암호화 상태
python3 make_users.py --encrypt    # 암호화 켜기
python3 make_users.py --no-encrypt # 끄기
python3 make_users.py --disable    # 로그인 끄기
```

> **`auth.json` 은 비밀 파일입니다.** 데이터를 복호할 수 있는 키 재료가 들어 있습니다.
> `.gitignore` 대상이며 권한은 600 입니다. 공유·커밋하지 마십시오.
> 분실하면 기존 암호화 배포본에 계정을 추가할 수 없습니다(재빌드 필요).

### 도커 — nginx Basic 인증

서버단에서 막으므로 **인증 전에는 파일을 내려받을 수 없습니다.**

```bash
cd docker
./make_htpasswd.sh 홍길동 김철수
./build_image.sh
```

`.htpasswd` 가 없으면 인증 없이 기동합니다.

---

## 배포

### 개인 · 공유폴더

`index.html` 파일 하나만 복사하면 됩니다.

담당자가 데이터를 갱신할 때는 **데이터 관리 → 배포용 HTML 저장**으로
데이터가 구워진 파일을 받아 공유폴더에 덮어씁니다.
받는 사람은 열기만 하면 최신 데이터가 보입니다.

> 화면에서 편집한 값은 `localStorage`에 저장되며 **그 브라우저에만** 남습니다.
> 배포본이 교체되면 이전 저장값은 자동으로 비활성화되고 안내가 표시됩니다.

### 도커

```bash
cd docker
./build_image.sh                     # html/index.html 사용 (Python 불필요)
./build_image.sh ../master.xlsx      # 엑셀로 새로 생성

# 폐쇄망 서버에서
./load_image.sh                      # → http://<서버IP>:8080
```

nginx alpine 기반이며 CSP로 외부 연결을 차단(`connect-src 'none'`)합니다.

---

## 저장소 구조

```
build.py                엑셀 → HTML 빌드
extract.py              시트 파싱 (시트 구조 변경 시 여기만 수정)
build_data.py           판정 · 역전탐지 · 비식별 · 제품명 정규화
make_users.py           로그인 계정 생성 (PBKDF2)
crypto_pack.py          봉투 암호화 (AES-256-GCM)
templates/
  tpl_head.html         스타일 · 마크업
  tpl_auth.html         로그인 게이트 · 역할 제어
  tpl_parse.html        브라우저 엑셀 파서 (extract+build_data 의 JS 이식)
  tpl_js.html           탭 렌더러
  tpl_ref.html          패치가이드 · 표준화 검증 (정책 기준)
  tpl_data.html         데이터 관리 · 편집
  tpl_chat.html         질의 챗봇 · 라우팅 (마지막에 병합)
vendor/xlsx.full.min.js SheetJS (오프라인 엑셀 읽기·쓰기)
sample/make_sample.py   더미 마스터파일 생성기
tests/                  playwright 기반 검증
docker/                 폐쇄망 배포 (nginx Basic 인증 포함)
docs/index.html         GitHub Pages 산출물 (샘플 데이터)
```

---

## 판정 규칙

| 판정 | 조건 |
| --- | --- |
| 전환대상 | EOS 도래(`EOS여부=O`) 또는 업데이트 `불가` |
| 전환권장 | 상위 버전 적용 `가능` |
| 표준준수 | `불필요` · `해당없음` |

| 우선순위 | 기준 | 기한 |
| --- | --- | --- |
| P1 | EOS 도래 · EOL 계열 | 72시간 |
| P2 | 그 외 전환대상 | 2주 |
| P3 | 전환권장 | 분기 |
| P4 | 표준준수 | 반기 |

### 자동 점검

**권고역전** — 원장의 권고버전이 현재 운영버전보다 낮으면 감지해 경고합니다.
그대로 적용하면 다운그레이드가 되기 때문입니다.
같은 메이저·마이너 라인일 때만 비교하며, 제품명이 섞인 문자열은 제외합니다.

**데이터 품질** — 현재버전 형식 불량 · OS 미기재 · 권고버전 미기재를 집계합니다.

---

## 데이터 취급

**서버명은 포털에 포함되지 않습니다.** 빌드 단계에서 제외되며 상세 화면에는
`(비식별)`로 표시되고, 엑셀로 내보낼 때도 공란으로 나갑니다.

포털에 포함되는 항목 · 자산ID · 계층 · 운영구분 · 업무명 · OS · 제품 · 버전 · 판정

### 실 데이터 보호 장치

이 저장소는 실제 자산 데이터가 공개되지 않도록 두 겹으로 막습니다.

**1. `.gitignore`** — 모든 `*.xlsx`, 빌드 산출물(`dist/`, `docker/html/index.html`,
내보낸 CSV·백업), **인증 정보**(`auth.json`, `docker/.htpasswd`)를 추적하지 않습니다. 샘플 엑셀도 커밋하지 않고 매번 생성합니다
(`make_sample.py` 는 시드가 고정되어 항상 같은 결과를 냅니다).

**2. `build.py` 안전장치** — 샘플이 아닌 엑셀을 `docs/` 로 빌드하려 하면 중단합니다.
`docs/` 는 GitHub Pages 공개 경로이기 때문입니다.

```
$ python3 build.py 실데이터.xlsx
  [중단] docs/ 는 GitHub Pages 공개 경로입니다.
         실 데이터는 저장소 밖이나 dist/ 로 출력하십시오.
```

실 데이터로 빌드할 때는 출력 경로를 명시하십시오.

```bash
python3 build.py /사내경로/ITS_Master.xlsx dist/portal.html
```

그래도 커밋 전 `git status` 확인을 권장합니다.

---

## 검증

```bash
pip install -r requirements-dev.txt
playwright install chromium

python3 tests/verify_csp.py      # 폐쇄망 CSP 환경 재현 · 전 탭 · 챗봇 · CSV
python3 tests/audit.py           # 동작하지 않는 UI 요소 탐지
python3 tests/test_ux.py         # 드릴다운 · 정렬 · 해시 · 키보드
python3 tests/test_portable.py   # 엑셀 업로드 · 편집 · 저장유지 · 내보내기
python3 tests/test_share.py      # 공유폴더 배포 흐름
python3 tests/test_auth.py       # 로그인 · 역할별 권한
python3 crypto_pack.py           # 봉투 암호화 왕복 검증
python3 tests/qa.py              # 챗봇 질의 14종
```

`test_portable.py` 는 브라우저 파서와 Python 파서의 결과가 일치하는지도 확인합니다.

---

## 새 제품이 추가될 때

원장 표기와 표준 마스터 표기가 다르면 정규화 표에 한 줄 추가합니다.
**두 곳 모두** 고쳐야 명령줄·브라우저 결과가 계속 일치합니다.

- `build_data.py` 의 `CANON`
- `templates/tpl_parse.html` 의 `CANON`

```python
(r"tibero", "Tibero"),
```
