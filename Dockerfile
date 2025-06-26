# Melbourne Celebrant Portal - Multi-stage Docker Build
# Supports both backend and frontend deployment

# ===========================================
# Backend Stage
# ===========================================
FROM python:3.11-slim as backend

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY celebrant-portal-v2/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY celebrant-portal-v2/backend/ .

# Expose backend port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start backend server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ===========================================
# Frontend Stage
# ===========================================
FROM node:18-alpine as frontend

WORKDIR /app/frontend

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./
COPY next.config.js ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY src/ ./src/
COPY public/ ./public/

# Build the application
RUN npm run build

# Expose frontend port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start frontend server
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
COPY --from=backend /app/backend ./backend
COPY --from=frontend /app/frontend ./frontend

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80 443

# Start services
CMD ["sh", "-c", "nginx && cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 & cd frontend && npm start"]
