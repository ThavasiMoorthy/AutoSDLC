# 🚀 AutoSDLC — AI-Powered Software Engineering Platform

AutoSDLC is an AI-powered SDLC (Software Development Life Cycle) automation platform that takes a project idea and generates a complete software blueprint — including requirements, project plan, cost estimation, code generation, and a live website prototype.

## ✨ Features

- **AI Requirement Analysis** — Generates detailed SRS from your project brief
- **Smart Project Planning** — Creates WBS with tasks, milestones, and timelines
- **Complexity-Based Cost Estimation** — Fair pricing based on project difficulty (Simple/Medium/Complex tiers)
- **Multi-File Code Generation** — Generates project structure with actual source files
- **Live Website Prototype** — Generates a beautiful, interactive website preview
- **AI Chat Assistant** — Ask questions about your project plan, architecture, or costs
- **3D SDLC-Themed UI** — Modern dark design with glassmorphism, animations, and gradient effects

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, Pydantic |
| **Frontend** | React, TypeScript, Tailwind CSS, Lucide Icons |
| **AI/LLM** | Groq API (Llama 3.3 70B) |
| **Build** | Vite |

## 📦 Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Groq API Key](https://console.groq.com/keys) (free)

### 1. Clone the repository
```bash
git clone https://github.com/ThavasiMoorthy/AutoSDLC.git
cd AutoSDLC
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install fastapi uvicorn groq pydantic python-dotenv

# Create .env file with your Groq API key
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start the backend server
python -m uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd client
npm install
npm run dev
```

### 4. Open the app
Visit [http://localhost:5173](http://localhost:5173)

## 🎯 How to Use

1. **Enter your project idea** in the text area (e.g., "Build a food delivery app with GPS tracking")
2. **Click "Launch Analysis"** — AI agents will generate:
   - Software Requirements Specification (SRS)
   - Work Breakdown Structure (WBS) with cost estimation
   - Project team roles and responsibilities
   - Multi-file code structure
3. **Click "Generate Live Prototype"** to see a beautiful website preview
4. **Use the AI Chat** to ask questions about your project

## 📁 Project Structure
```
AutoSDLC/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & endpoints
│   ├── models.py             # Pydantic data models
│   ├── llm.py                # Groq LLM integration
│   └── agents/
│       ├── base.py           # Base agent class
│       ├── requirement_agent.py  # SRS generation
│       ├── planning_agent.py     # WBS & cost estimation
│       ├── coding_agent.py       # Code generation
│       └── prototype_agent.py    # Website prototype
├── client/
│   ├── src/
│   │   ├── App.tsx           # Main React component
│   │   ├── types.ts          # TypeScript interfaces
│   │   └── index.css         # Tailwind + custom styles
│   ├── package.json
│   └── vite.config.ts
├── .env.example              # Environment variable template
├── .gitignore
└── README.md
```

## 🔑 Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key ([get one free](https://console.groq.com/keys)) |

## 📄 License

MIT License

---

Built with ❤️ using AI-powered automation
