# AI Backend Setup Guide

## Overview
The AI backend is a FastAPI-based service that provides intelligent task assignment, performance reviews, risk assessment, and conflict resolution using LangGraph and Groq LLM.

**Port:** 8000
**Technology:** FastAPI, LangGraph, Groq API, Python 3.8+

---

## Prerequisites

- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
- **Groq API Key** - Sign up at [console.groq.com](https://console.groq.com)
- **pip** (Python package manager) - Usually comes with Python

---

## Installation Steps

### 1. Navigate to Backend Directory
```powershell
cd ai-backend
```

### 2. Create a Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

**Key packages installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain` - LLM orchestration
- `langgraph` - Graph-based workflows
- `groq` - Groq API client
- `pydantic` - Data validation

---

## Configuration

### 1. Set Environment Variables
Create a `.env` file in the `ai-backend` directory:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768

# Backend Configuration
BACKEND_PORT=8000
MOCK_SERVER_URL=http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

**Get your Groq API Key:**
1. Go to [console.groq.com](https://console.groq.com)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key
5. Copy and paste into `.env`

### 2. File Structure
```
ai-backend/
├── main.py                    # FastAPI entry point (uses Groq)
├── main_ollama.py            # Alternative entry point (uses Ollama)
├── start.py                  # Startup script
├── requirements.txt          # Python dependencies
├── SETUP.md                  # This file
│
├── config/
│   └── settings.py           # Configuration management
│
├── models/
│   └── schemas.py            # Pydantic data models
│
├── services/
│   ├── decision_service.py   # Task assignment & decisions
│   └── decision_logger.py    # Audit trail logging
│
├── workflows/
│   ├── decision_workflow.py  # LangGraph workflow (Graph of Thoughts)
│   └── conflict_resolution_workflow.py
│
├── agents/
│   └── data_agent.py         # Data retrieval agent
│
├── utils/
│   ├── groq_client.py        # Groq API wrapper
│   ├── llm_factory.py        # LLM provider factory
│   └── llm_utils.py          # LLM utilities
│
└── tests/
    ├── mock_server.py        # Mock data server (port 3000)
    ├── test_client.py        # API test client
    └── mock_data.py          # Test data fixtures
```

---

## Running the Backend

### Option 1: Using FastAPI + Groq (Recommended)
```powershell
python start.py
```

The server will start on `http://localhost:8000`

**What it does:**
- Loads environment variables
- Initializes FastAPI app
- Connects to Groq API
- Starts ASGI server with auto-reload

### Option 2: Direct Execution
```powershell
uvicorn main:app --reload --port 8000
```

### Option 3: Using Ollama (Local LLM)
If you have Ollama installed:
```powershell
python main_ollama.py
```

---

## Starting Mock Data Server

The mock server provides test data on port 3000 (required for frontend).

**In a separate terminal:**
```powershell
cd ai-backend/tests
python mock_server.py
```

The mock server will be available at `http://localhost:3000`

---

## API Endpoints

### Health Check
```
GET /health
```

### Task Assignment
```
POST /assign-task
```
Request body:
```json
{
  "task_id": "TASK-001",
  "task_name": "Build user authentication",
  "difficulty": "HIGH",
  "required_skills": ["Python", "FastAPI", "Database"],
  "team_members": [
    {
      "id": "USR-001",
      "name": "John Doe",
      "skills": ["Python", "FastAPI", "Database"],
      "current_workload": 60
    }
  ]
}
```

### Performance Review
```
POST /performance-review
```

### Risk Assessment
```
POST /risk-assessment
```

### Audit Trail
```
GET /audit-trail
```

### Conflict Resolution
```
POST /conflict-resolution
```

---

## Key Features

### 1. Graph of Thoughts Architecture
The decision workflow uses LangGraph to orchestrate multiple specialized agents:
- **Reasoning Agent** - Analyzes task requirements
- **Ethics Agent** - Evaluates bias, workload balance, wellbeing
- **Risk Agent** - Identifies potential risks
- **Performance Agent** - Assesses performance metrics
- **Decision Agent** - Makes final assignment
- **Explainability Agent** - Generates reasoning trace

### 2. Expertise-First Assignment
- **HIGH/CRITICAL tasks:** 40% experience, 35% skill match, 20% confidence, 5% workload
- **MEDIUM tasks:** 30% experience, 30% skill, 25% confidence, 15% workload
- **LOW tasks:** 25% experience, 25% skill, 30% confidence, 20% workload

### 3. Ethical Analysis
Every decision includes:
- **bias_check** - Evaluates for unconscious bias
- **workload_balance** - Assesses team member wellbeing
- **wellbeing_impact** - Considers work-life balance

### 4. Detailed Reasoning
- Decision workflow trace showing all agent decisions
- Scoring breakdown for transparency
- Audit trail for compliance

---

## Testing

### Run Tests
```powershell
cd tests
python test_client.py
```

### Test Mock Server
```powershell
python mock_server.py
```

---

## Troubleshooting

### 1. "ModuleNotFoundError: No module named 'fastapi'"
**Solution:** Install dependencies
```powershell
pip install -r requirements.txt
```

### 2. "Connection refused: Groq API"
**Solution:** 
- Check your `GROQ_API_KEY` in `.env`
- Verify internet connection
- Try alternative LLM with `main_ollama.py`

### 3. "Port 8000 already in use"
**Solution:** 
- Kill existing process:
  ```powershell
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```
- Or use different port:
  ```powershell
  uvicorn main:app --port 8001
  ```

### 4. "GROQ_API_KEY not found"
**Solution:**
- Create `.env` file in `ai-backend` directory
- Add `GROQ_API_KEY=your_key_here`
- Restart the server

### 5. Mock server not responding
**Solution:**
```powershell
# Kill and restart
taskkill /F /IM python.exe
cd ai-backend/tests
python mock_server.py
```

---

## Performance Tuning

### Temperature Settings
- **0.3 (Low)** - More focused, consistent responses
- **0.6 (Balanced)** - Default, good balance of creativity and consistency
- **0.9 (High)** - More creative, varied responses

Current setting: **0.6** (balanced)

### Timeout
- Default: **180 seconds** for complex decisions
- Adjust in `decision_service.py` if needed

---

## Environment Variables Reference

```env
# Required
GROQ_API_KEY=...              # Your Groq API key

# Optional
GROQ_MODEL=mixtral-8x7b-32768  # LLM model (default)
BACKEND_PORT=8000             # Server port
MOCK_SERVER_URL=http://localhost:3000  # Mock data endpoint
LOG_LEVEL=INFO                # Logging level
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure `.env` with Groq API key
3. ✅ Start backend: `python start.py`
4. ✅ Start mock server: `python ai-backend/tests/mock_server.py`
5. ➡️ Set up frontend (see `frontend/SETUP.md`)
6. ➡️ Test full system: `http://localhost:5173`

---

## Support

For issues or questions:
1. Check logs in the terminal
2. Verify `.env` configuration
3. Review troubleshooting section above
4. Check Groq API status at [console.groq.com](https://console.groq.com)

---

**Version:** 1.0  
**Last Updated:** January 3, 2026
