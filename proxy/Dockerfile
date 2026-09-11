# syntax=docker/dockerfile:1
FROM nginx:1.27-alpine
COPY proxy/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1/api/v1/health/companies || exit 1
