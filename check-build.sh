#!/bin/bash

echo "🔍 Running pre-deployment checks..."

# Frontend checks
echo "📦 Checking frontend build..."
cd frontend

echo "1️⃣ TypeScript check..."
npx tsc --noEmit
if [ $? -ne 0 ]; then
    echo "❌ TypeScript errors found!"
    exit 1
fi

echo "2️⃣ Linting..."
npm run lint
if [ $? -ne 0 ]; then
    echo "❌ Lint errors found!"
    exit 1
fi

echo "3️⃣ Building..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ All checks passed! Ready to deploy."