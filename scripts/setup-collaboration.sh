#!/bin/bash

echo "🤖 Setting up AI Collaboration Environment"
echo "========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

# Check for OPENROUTER_API_KEY
if ! grep -q "OPENROUTER_API_KEY=.*[^_]" .env; then
    echo ""
    echo "⚠️  OPENROUTER_API_KEY not configured!"
    echo ""
    echo "To enable AI collaboration between Claude CLI and GPT-4o:"
    echo "1. Get your OpenRouter API key from https://openrouter.ai/keys"
    echo "2. Add it to your .env file:"
    echo "   OPENROUTER_API_KEY=your_actual_key_here"
    echo ""
    echo "Then run: ./gpt5 \"test message\" to verify it works"
    exit 1
else
    echo "✅ OPENROUTER_API_KEY is configured"
fi

# Make gpt5 executable
chmod +x gpt5
echo "✅ Made gpt5 tool executable"

# Test the connection
echo ""
echo "🧪 Testing GPT-4o connection..."
./gpt5 "Hello, this is a test message. Please respond with: 'GPT-4o connection successful!'" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ AI Collaboration is ready!"
    echo ""
    echo "You can now use commands like:"
    echo "  ./gpt5 \"As Executive AI: What should we prioritize?\""
    echo "  ./gpt5 \"As DeFi Strategist: How to calculate IL?\""
    echo "  ./gpt5 \"As Builder: Best WebSocket approach?\""
else
    echo ""
    echo "❌ Connection test failed. Please check your API key."
fi