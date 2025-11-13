# Stage 1: Build
ARG CONTEXT=frontend
FROM node:20-alpine AS build

# redeclare ARGs for the stage
ARG CONTEXT
ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE}

WORKDIR /app

# Copy package files (include lockfile)
COPY ${CONTEXT}/package*.json ./
COPY ${CONTEXT}/package-lock.json ./
COPY ${CONTEXT}/tsconfig.json ./
COPY ${CONTEXT}/vite.config.ts ./

# deterministic install
RUN npm ci --prefer-offline --no-audit

# Copy source
COPY ${CONTEXT}/ ./

# Bake Vite env from the build-time variable (Railway exposes service vars during build)
RUN printf "VITE_API_BASE=%s\n" "${VITE_API_BASE:-http://localhost:8000}" > .env.production

# Build (vite will read .env.production)
RUN npm run build

# Stage 2: Serve
FROM nginx:stable-alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]