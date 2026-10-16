# ── Build ──────────────────────────────────────────────
FROM node:24-alpine AS builder

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# ── Runtime ────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Replace default config with SPA-friendly config (non-root: 8080)
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /build/dist /usr/share/nginx/html

# nginx user exists in the base image; binding 8080 is non-privileged
USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://127.0.0.1:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]