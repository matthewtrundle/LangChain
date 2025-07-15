# 🚀 API Setup Guide for SolDegen

## Quick Start (Required APIs)

### 1. **OpenAI API** (Required for LangChain agents)
```bash
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-key-here
```

### 2. **Helius API** (You already have this!)
```bash
# Your existing Helius key
HELIUS_API_KEY=your-helius-key-here
```

## Enhanced Features (Optional APIs)

### 3. **CoinGecko API** (FREE - 5,000 calls/month)
```bash
# Sign up at: https://www.coingecko.com/en/api
# Free tier gives you 5,000 calls/month
COINGECKO_API_KEY=your-coingecko-key-here
```

### 4. **Twitter API v2** (FREE tier available)
```bash
# Get from: https://developer.twitter.com/en/portal/dashboard
# Free tier: 1,500 tweets/month
TWITTER_BEARER_TOKEN=your-twitter-bearer-token-here
```

### 5. **SerpAPI** (FREE tier: 100 searches/month)
```bash
# Sign up at: https://serpapi.com/
# Free tier gives you 100 searches/month
SERP_API_KEY=your-serp-api-key-here
```

## Setup Instructions

### 1. **Copy Environment File**
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

### 2. **Install Dependencies**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 3. **Start the System**
```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 4. **Test the System**
Open http://localhost:3000 and try:
- "Find me degen yields over 1000% APY"
- Quick scan buttons
- Check system status

## API Integration Status

### Currently Working (Mock Data)
- ✅ **DeFiLlama**: Real API call ready (no key needed)
- ✅ **Multi-Agent System**: Full LangChain coordination
- ✅ **Helius**: Ready for your existing key
- ✅ **Frontend**: Complete dashboard

### Ready to Enable (Add API keys)
- 🔧 **Jupiter Pricing**: TODO comments in code
- 🔧 **CoinGecko**: TODO comments in code  
- 🔧 **Twitter Search**: TODO comments in code
- 🔧 **Web Search**: TODO comments in code

## Finding TODO Comments

Search for "TODO: USER" in the codebase to find all integration points:

```bash
# Find all API integration points
grep -r "TODO: USER" backend/
```

## API Cost Breakdown

### Free Forever
- **DeFiLlama**: Unlimited
- **Jupiter**: Unlimited
- **Helius**: Your existing plan

### Free Tiers
- **CoinGecko**: 5,000 calls/month
- **Twitter**: 1,500 tweets/month  
- **SerpAPI**: 100 searches/month

### Paid (Optional)
- **OpenAI**: ~$20/month for GPT-4
- **Enhanced Twitter**: $100/month
- **Enhanced SerpAPI**: $50/month

## Interview-Ready Features

Even with just **OpenAI + Helius**, you have:
- ✅ Multi-agent LangChain system
- ✅ Real-time Solana data
- ✅ Intelligent coordination
- ✅ Professional frontend
- ✅ Degen scoring algorithm

## Next Steps

1. **Add your OpenAI key** - enables all agents
2. **Test with your Helius key** - real Solana data
3. **Add CoinGecko** - enhanced token data
4. **Add Twitter** - alpha discovery
5. **Add SerpAPI** - web search capabilities

The system is designed to work with any combination of APIs!