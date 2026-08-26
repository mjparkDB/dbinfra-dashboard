#!/bin/sh
# nginx Basic 인증 계정 생성
#   ./make_htpasswd.sh <아이디> [아이디2 ...]
#
# HTML 안의 로그인과 달리, 이 인증은 파일 자체를 보호합니다.
# 인증을 통과하지 못하면 HTML을 내려받을 수 없으므로 자산 데이터도 노출되지 않습니다.
set -e
OUT=.htpasswd
[ $# -ge 1 ] || { echo "사용법: ./make_htpasswd.sh <아이디> [아이디2 ...]"; exit 1; }

: > "$OUT"
for U in "$@"; do
  printf "  %s 비밀번호: " "$U"
  stty -echo 2>/dev/null || true
  read PW
  stty echo 2>/dev/null || true
  echo
  # openssl 이 있으면 bcrypt 대신 apr1 사용 (nginx 지원)
  HASH=$(openssl passwd -apr1 "$PW")
  echo "$U:$HASH" >> "$OUT"
done
chmod 600 "$OUT"
echo ""
echo "생성 완료 · docker/$OUT ($# 계정)"
echo "이미지를 다시 빌드하십시오 · ./build_image.sh"
