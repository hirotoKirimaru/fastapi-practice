# Minimal dev image. For production, build static assets and serve via nginx.
FROM node:24-alpine AS dev

WORKDIR /app

# package-lock.json のとおりに入れる（以前は lockfile が無く、ビルドのたびに版が変わり得た）
COPY package.json package-lock.json .npmrc ./
RUN npm ci

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
