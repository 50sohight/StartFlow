FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ARG PUBLIC_API_URL=http://localhost:8078
ARG PUBLIC_AI_URL=http://localhost:8077
ENV PUBLIC_API_URL=${PUBLIC_API_URL} \
    PUBLIC_AI_URL=${PUBLIC_AI_URL}
RUN npm run build && npm prune --omit=dev

FROM node:22-alpine AS runner

WORKDIR /app

RUN apk add --no-cache curl

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000

COPY --from=builder /app/package.json ./
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl --fail http://127.0.0.1:3000/ || exit 1

EXPOSE 3000

CMD ["node", "build"]
