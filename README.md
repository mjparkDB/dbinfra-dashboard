# IT인프라 표준화 조회시스템 v2.0

> JH.CORP IT Infrastructure Standardization Query System  
> GitHub Pages 배포용 · 완전 오프라인 동작 · Excel Import 지원

---

## 🚀 GitHub Pages 배포 방법

### 1단계: 저장소 생성

```bash
# GitHub에서 새 저장소 생성 후:
git init
git add .
git commit -m "IT인프라 표준화 조회시스템 v2.0"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
git push -u origin main
```

### 2단계: GitHub Pages 활성화

1. GitHub 저장소 → **Settings** 탭 클릭
2. 좌측 메뉴 → **Pages** 클릭
3. **Source** → `Deploy from a branch` 선택
4. **Branch** → `main` / `/ (root)` 선택 후 **Save**
5. 약 1~2분 후 → `https://<YOUR_USERNAME>.github.io/<REPO_NAME>/` 접속

---

## 📁 파일 구조

```
/
├── index.html          ← 시스템 전체 (단일 파일)
└── README.md           ← 이 파일
```

> **단일 파일** 구성으로 배포가 매우 간단합니다.  
> SheetJS (CDN) 한 개만 외부에서 로드합니다.

---

## 📊 엑셀 Import 방법

### 지원 파일 형식
- `.xlsx` (Excel 2007 이상) ✅
- `.xls` (Excel 97-2003) ✅  
- `.csv` (쉼표 구분) ✅

### 사용 방법
1. 좌측 메뉴 → **마스터파일 Import** 클릭
2. 엑셀 파일 드래그 또는 클릭하여 업로드
3. 시트 선택 (서버 시트 / 네트워크 시트)
4. 컬럼 매핑 확인 (자동 추측 적용됨)
5. **✅ 데이터 적용** 버튼 클릭
6. 대시보드에서 실시간 반영 확인

### 서버 시트 컬럼 형식

| 컬럼 | 예시 | 필수 |
|------|------|------|
| 서버ID | SRV-001 | ✅ |
| Hostname | p1x86sv001 | ✅ |
| IP주소 | 10.10.51.11 | - |
| 자산유형 | x86_물리서버 | - |
| 제조사 | DELL | - |
| 모델 | R750 | - |
| 현재OS | RHEL 8.4 | ✅ |
| 권고OS | RHEL 8.10 | - |
| 현재DB | Oracle 19.27 | - |
| 권고DB | 19.27 최신 | - |
| 현재WAS | Tomcat 9.0 | - |
| 권고WAS | Tomcat 10.1.40 | - |
| JDK | 1.8.0_282 | - |
| 상태 | **긴급 / 주의 / 양호** | ✅ |
| 우선순위 | 1 / 2 / 3 | - |

### 네트워크 시트 컬럼 형식

| 컬럼 | 예시 | 필수 |
|------|------|------|
| 장비ID | NET-056 | ✅ |
| Hostname | RTR-BR-001 | ✅ |
| MGMT IP | 10.10.20.1 | - |
| 모델명 | C8300-1N1S-6T | - |
| 장비유형 | Branch Router | - |
| 플랫폼 | IOS-XE | - |
| 현재펌웨어 | 17.6.5 | ✅ |
| 권고펌웨어 | 17.12.5 LTS | - |
| EOL/EOS | EOS완료 | - |
| CVE위험도 | **최고 / 고 / 중 / 저** | - |
| 상태 | **긴급 / 주의 / 양호** | ✅ |
| 위치 | BR-HQ | - |

> 💡 컬럼명이 다를 경우 업로드 후 **컬럼 매핑 UI**에서 직접 선택 가능합니다.

---

## 🔧 주요 기능

| 기능 | 설명 |
|------|------|
| 📊 종합 현황 | KPI 카드, 진행률 바, TOP 5 긴급 항목 |
| 🖥 서버 목록 | OS/DB/WAS 전체 현황 + 검색/필터 |
| 🌐 네트워크 장비 | 펌웨어/EOL/CVE 현황 + 검색/필터 |
| 🚨 긴급 조치 목록 | EOL 초과 전체 집계 |
| 📋 버전 참조 테이블 | AI 권고버전 기준 참조 |
| 💿 OS 버전 현황 | OS별 집계 자동화 |
| ⚙️ MW/DB 현황 | 미들웨어/DB 집계 자동화 |
| 🔗 호환성 그룹 (GRP) | 표준화 목표 스택 |
| ⬆️ Excel Import | .xlsx/.xls/.csv 파일 업로드 + 컬럼 매핑 |
| 📤 Excel Export | 현재 데이터 다운로드 |
| 🔍 상세 패널 | 행 클릭 시 슬라이드 패널 |

---

## 🔒 보안 / 개인정보

- 업로드한 파일은 **브라우저 내에서만 처리**됩니다
- 서버 전송 없음 · 완전 클라이언트 사이드
- GitHub Pages는 정적 파일만 서빙하므로 데이터 유출 없음

---

## 📦 사용 라이브러리

| 라이브러리 | 용도 | 출처 |
|-----------|------|------|
| SheetJS (xlsx 0.18.5) | Excel 파싱/생성 | CDN (cdnjs) |

> 나머지는 순수 HTML/CSS/JS — 외부 의존성 없음

---

*IT인프라 표준화 조회시스템 v2.0 · JH.CORP · 2026*
