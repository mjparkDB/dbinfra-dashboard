# 인프라 표준화 포털 — 폐쇄망 배포용
# 정적 HTML 1개만 서빙. 외부 통신·CDN 의존 없음.
FROM nginx:1.27-alpine

LABEL org.opencontainers.image.title="ITS Portal" \
      org.opencontainers.image.description="인프라 표준화 포털 (인프라운영파트)" \
      org.opencontainers.image.vendor="JH.CORP"

RUN rm -rf /usr/share/nginx/html/* \
 && rm -f /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/its.conf
COPY html/ /usr/share/nginx/html/

# Basic 인증 파일 — 없으면 인증 없이 동작하도록 빈 파일을 만듭니다.
# 실제 계정은 make_htpasswd.sh 로 생성한 뒤 이미지를 다시 빌드하십시오.
COPY .htpasswd* /etc/nginx/
RUN if [ ! -s /etc/nginx/.htpasswd ]; then \
      sed -i '/auth_basic/d' /etc/nginx/conf.d/its.conf; \
      echo "[알림] .htpasswd 없음 — Basic 인증 없이 기동합니다."; \
    else \
      echo "[알림] Basic 인증 적용됨."; \
    fi

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD wget -qO- http://127.0.0.1/healthz || exit 1
