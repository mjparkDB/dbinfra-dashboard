#!/bin/sh
# 인터넷 되는 PC에서 실행 — 이미지 빌드 + tar 저장
#   ./build_image.sh                 → html/index.html 을 그대로 사용 (Python 불필요)
#   ./build_image.sh ../master.xlsx  → 엑셀로 HTML 새로 생성 후 빌드 (Python 필요)
set -e
TAG=its-portal:2.0
OUT=its-portal-2.0.tar

if [ -n "$1" ]; then
  echo "[1/3] 엑셀로 포털 HTML 생성: $1"
  ( cd .. && python3 build.py "$1" docker/html/index.html )
else
  echo "[1/3] 기존 html/index.html 사용 (Python 불필요)"
  if [ ! -f html/index.html ]; then
    echo "오류: html/index.html 이 없습니다."
    echo "      포털 HTML 파일을 html/index.html 로 복사한 뒤 다시 실행하십시오."
    exit 1
  fi
fi

echo "[2/3] 이미지 빌드"
docker build -t "$TAG" .

echo "[3/3] tar 저장"
docker save "$TAG" -o "$OUT"
gzip -f "$OUT"

echo ""
echo "완료: docker/$OUT.gz"
echo "이 파일을 USB로 폐쇄망에 옮긴 뒤 load_image.sh 를 실행하십시오."
