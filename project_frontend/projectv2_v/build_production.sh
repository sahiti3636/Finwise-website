#!/bin/bash

# FinWise Frontend - Production Build Script
# This script builds the frontend for production deployment

echo "Building FinWise Frontend for Production"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "Error: Please run this script from the project_frontend/projectv2_v directory"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi

echo "Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "Building for production..."
npm run build

if [ $? -ne 0 ]; then
    echo "Error: Build failed"
    exit 1
fi

echo "Build completed successfully!"
echo "Production files are in the 'dist' directory"
echo ""
echo "To deploy:"
echo "1. Copy the 'dist' folder to your web server"
echo "2. Configure your web server to serve static files"
echo "3. Set up proper routing for SPA (Single Page Application)"
echo ""
echo "For Nginx, add this location block:"
echo "location / {"
echo "    try_files \$uri \$uri/ /index.html;"
echo "}" 