#!/bin/bash

# Build script for Melbourne Celebrant Portal
echo "Building Melbourne Celebrant Portal..."

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the application
echo "Building application..."
npm run build

echo "Build completed successfully!"
