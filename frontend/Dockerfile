# Minimal dev image. For production, build static assets and serve via nginx.
FROM node:24-alpine AS dev

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
