# Stage 1: Build
ARG CONTEXT=frontend
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files from context (supports repo-root or service folder builds)
COPY ${CONTEXT}/package*.json ./
COPY ${CONTEXT}/tsconfig.json ./
COPY ${CONTEXT}/vite.config.ts ./

# Install dependencies
RUN npm install

# Copy all source files, including index.html
COPY ${CONTEXT}/ ./

# Build the project
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:stable-alpine

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from previous stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]