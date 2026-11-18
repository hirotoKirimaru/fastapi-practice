# Minimal dev image. For production, build static assets and serve via nginx.
FROM oven/bun:1.4.4-alpine AS dev

WORKDIR /app

# bun.lock のとおりに入れる。取得元は .npmrc の Takumi Guard、bunfig.toml で公開 3 日未満の版を除く
COPY package.json bun.lock bunfig.toml .npmrc ./
RUN bun install --frozen-lockfile

COPY . .

EXPOSE 5173
CMD ["bun", "run", "dev"]
