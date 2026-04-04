# syntax=docker/dockerfile:1
# ── Stage 1: Build ──
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci

COPY . .

ARG VITE_API_URL=/api
ARG BASE_URL=/
ENV VITE_API_URL=${VITE_API_URL}
ENV BASE_URL=${BASE_URL}

RUN npm run build

# ── Stage 2: Serve with nginx ──
FROM nginx:stable-alpine

ARG VERSION=latest
LABEL org.opencontainers.image.version="${VERSION}"

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
