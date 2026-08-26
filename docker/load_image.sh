#!/bin/sh
# 폐쇄망 서버에서 실행 — 이미지 적재 + 기동
set -e
TAR=its-portal-2.0.tar.gz
TAG=its-portal:2.0

[ -f "$TAR" ] || { echo "오류: $TAR 파일이 없습니다."; exit 1; }

echo "[1/2] 이미지 적재"
gunzip -c "$TAR" | docker load

echo "[2/2] 컨테이너 기동"
docker rm -f its-portal 2>/dev/null || true
docker run -d --name its-portal --restart unless-stopped -p 8080:80 "$TAG"

echo ""
echo "완료. 브라우저에서 http://<서버IP>:8080 으로 접속하십시오."
docker ps --filter name=its-portal --format "  {{.Names}}  {{.Status}}  {{.Ports}}"
