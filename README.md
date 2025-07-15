# 🌙 SolDegen - Multi-Agent Solana Yield Hunter

An intelligent multi-agent system that discovers and analyzes high-yield opportunities on Solana using LangChain and OpenAI.

![SolDegen Dashboard](https://via.placeholder.com/800x400?text=SolDegen+Dashboard)

## 🚀 Features

- **Multi-Agent AI System**: 4 specialized agents working together
  - 🔍 **Scanner Agent**: Discovers new high-APY pools
  - 📊 **Analyzer Agent**: Performs deep risk assessment
  - 👁️ **Monitor Agent**: Tracks positions and alerts
  - 🎯 **Coordinator Agent**: Orchestrates all agents

- **Real-Time Data**: Integration with DeFiLlama, Helius, Jupiter
- **Risk Assessment**: Comprehensive "Degen Score" algorithm
- **Natural Language**: Ask in plain English
- **Professional UI**: AAVE-inspired dark theme

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LangChain
- **Frontend**: Next.js 14, TypeScript, TailwindCSS
- **AI**: OpenAI GPT-4 (or OpenRouter)
- **Data**: Helius RPC, DeFiLlama API, Jupiter

## 🏃‍♂️ Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key (or OpenRouter key)
- Helius API key (optional)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/solana-degen-hunter.git
cd solana-degen-hunter
```

2. **Backend Setup**
```bash
cd backend
cp .env.example .env
# Add your API keys to .env
pip install -r requirements.txt
python main.py
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the app**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🌐 Deployment

Deployed on Railway:
- Frontend: https://soldegen.up.railway.app
- Backend API: https://soldegen-api.up.railway.app

## 📸 Screenshots

### Dashboard
Real-time discovery of high-yield opportunities with risk assessment.

### Multi-Agent System
Watch as specialized AI agents collaborate to find the best yields.

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Next.js UI    │────▶│  Coordinator    │
└─────────────────┘     │     Agent       │
                        └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐       ┌───────▼────────┐
            │ Scanner Agent  │       │ Analyzer Agent │
            └────────────────┘       └────────────────┘
                    │                         │
            ┌───────▼────────┐       ┌───────▼────────┐
            │  Real APIs     │       │ Risk Scoring   │
            └────────────────┘       └────────────────┘
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com)
- Powered by [OpenAI](https://openai.com)
- Data from [Helius](https://helius.xyz) and [DeFiLlama](https://defillama.com)