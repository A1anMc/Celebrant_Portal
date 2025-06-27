# Melbourne Celebrant Portal - Multi-stage Docker Build
# Supports both backend and frontend deployment

# ===========================================
# Backend Build Stage
# ===========================================
FROM python:3.11-slim as backend-build

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY celebrant-portal-v2/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY celebrant-portal-v2/backend/ .

# ===========================================
# Frontend Build Stage
# ===========================================
FROM node:18-alpine as frontend-build

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./
COPY next.config.js ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Install dependencies (including devDependencies for build)
RUN npm ci

# Copy frontend source code
COPY src/ ./src/
COPY public/ ./public/

# Set environment variable for production build
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=http://localhost:8000

# Build the application
RUN npm run build

# ===========================================
# Backend Production Stage
# ===========================================
FROM python:3.11-slim as backend-production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from build stage
COPY --from=backend-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=backend-build /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY --from=backend-build /app/ ./

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ===========================================
# Frontend Production Stage
# ===========================================
FROM node:18-alpine as frontend-production

WORKDIR /app

# Install production dependencies only
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application from build stage
COPY --from=frontend-build /app/.next ./.next
COPY --from=frontend-build /app/public ./public
COPY --from=frontend-build /app/next.config.js ./
COPY --from=frontend-build /app/package.json ./

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start command
CMD ["npm", "start"]

# ===========================================
# Development Stage (Both services)
# ===========================================
FROM node:18-alpine as development

WORKDIR /app

# Install Python for backend
RUN apk add --no-cache python3 py3-pip gcc musl-dev python3-dev

# Copy all files
COPY . .

# Install backend dependencies
RUN cd celebrant-portal-v2/backend && pip install -r requirements.txt

# Install frontend dependencies
RUN npm install

# Expose both ports
EXPOSE 3000 8000

# Start both services in development mode
CMD ["sh", "-c", "cd celebrant-portal-v2/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload & npm run dev"]

# ===========================================
# Production Multi-service
# ===========================================
FROM alpine:latest as production

WORKDIR /app

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    nodejs \
    npm \
    curl \
    nginx

# Copy built applications
COPY --from=backend-production /app/backend ./backend
COPY --from=frontend-production /app/frontend ./frontend

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80 443

# Start services
CMD ["sh", "-c", "nginx && cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 & cd frontend && npm start"]

# Frontend Dockerfile (for src/ directory)
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy application code and config files
COPY . .

# Build the Next.js app
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
USER nextjs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start the application
CMD ["npm", "start"]
