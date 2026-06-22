FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --cache .npm-cache

COPY . .

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM node:22-alpine AS runner

ENV NODE_ENV=production

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev --cache .npm-cache

COPY --from=builder /app/dist ./dist

EXPOSE 4173

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]
