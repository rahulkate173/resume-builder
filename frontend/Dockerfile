# ── Frontend multi-stage build ───────────────────────────────────────────────
FROM node:22-alpine AS deps

WORKDIR /app
COPY package.json ./
RUN npm install --frozen-lockfile

# ── Build stage ───────────────────────────────────────────────────────────────
FROM deps AS builder

COPY . .
RUN npm run build

# ── Production: Nginx ─────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/health.txt || exit 1

CMD ["nginx", "-g", "daemon off;"]
