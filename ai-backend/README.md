# HCAT AI Backend - Setup and Testing Guide

## Overview

This AI backend integrates with your NestJS project management system to provide intelligent, ethical task assignment decisions using:

- **LangGraph** for orchestrating multiple AI agents
- **Graph of Thoughts (GoT)** reasoning for transparent decision-making
- **Multiple specialized agents**: Data, Reasoning, Ethics, Risk, Performance, Decision, and Explainability
- **OpenAI GPT-4** for advanced language understanding

## Architecture

```
┌─────────────────┐
│  NestJS Backend │  (Your existing project management system)
│  (Port 3000)    │
└────────┬────────┘
         │
         │ HTTP API
         ▼
┌─────────────────┐
│   Data Agent    │  (Fetches data from NestJS)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         LangGraph Workflow (GoT)            │
│                                             │
│  ┌──────────────┐                          │
│  │   Reasoning  │  Generate options         │
│  └──────┬───────┘                          │
│         │                                  │
│         ▼                                  │
│  ┌──────────────┐                          │
│  │    Ethics    │  Evaluate fairness       │
│  └──────┬───────┘                          │
│         │                                  │
│         ▼                                  │
│  ┌──────────────┐                          │
│  │     Risk     │  Assess risks            │
│  └──────┬───────┘                          │
│         │                                  │
│         ▼                                  │
│  ┌──────────────┐                          │
│  │ Performance  │  Evaluate impact         │
│  └──────┬───────┘                          │
│         │                                  │
│         ▼                                  │
│  ┌──────────────┐                          │
│  │   Decision   │  Make final call         │
│  └──────┬───────┘                          │
│         │                                  │
│         ▼                                  │
│  ┌──────────────┐                          │
│  │Explainability│  Generate explanation    │
│  └──────────────┘                          │
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │  (AI Decision API)
│  (Port 8000)    │
└─────────────────┘
```

## Project Structure

```
ai-backend/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration & environment variables
├── agents/
│   ├── __init__.py
│   └── data_agent.py        # Fetches data from NestJS backend
├── workflows/
│   ├── __init__.py
│   └── decision_workflow.py # LangGraph workflow with GoT reasoning
├── services/
│   ├── __init__.py
│   └── decision_service.py  # Business logic
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic models
├── tests/
│   ├── mock_data.py         # Mock data for testing
│   ├── mock_server.py       # Mock NestJS backend
│   └── test_client.py       # Test client
├── main.py                  # FastAPI application
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (you create this)
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd ai-backend
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the `ai-backend` directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# NestJS Backend Configuration
NESTJS_BACKEND_URL=http://localhost:3000

# AI Model Configuration
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7

# Server Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

**Important**: Replace `sk-your-actual-openai-api-key-here` with your actual OpenAI API key.

### 3. Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and paste it in your `.env` file
5. Make sure you have credits in your OpenAI account

## Testing the System

### Option A: Test with Mock Backend (Recommended for First Test)

This option runs a mock NestJS backend so you can test the AI system immediately.

**Step 1: Start the Mock NestJS Backend**

Open a terminal in the `ai-backend/tests` directory:

```bash
cd ai-backend/tests
python mock_server.py
```

You should see:
```
Starting Mock NestJS Backend on http://localhost:3000
This simulates your NestJS backend for testing purposes
```

**Step 2: Start the AI Backend**

Open a new terminal in the `ai-backend` directory:

```bash
cd ai-backend
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Step 3: Run the Test Client**

Open a third terminal in the `ai-backend/tests` directory:

```bash
cd ai-backend/tests
python test_client.py
```

This will:
1. Test the health check endpoint
2. Request an AI decision for task assignment
3. Display the complete decision with explanation

### Option B: Test with Real NestJS Backend

Once your NestJS backend is running:

**Step 1: Start Your NestJS Backend**

```bash
cd HCAT-main
npm start
```

Make sure it's running on `http://localhost:3000`

**Step 2: Seed Your Database with Test Data**

Make sure you have some tasks and users in your database:

```bash
npm run seed
```

**Step 3: Start the AI Backend**

```bash
cd ai-backend
python main.py
```

**Step 4: Test with Real Data**

```bash
cd ai-backend/tests
python test_client.py
```

## API Endpoints

### Health Check

```bash
GET http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-20T10:30:00"
}
```

### Task Assignment Decision

```bash
POST http://localhost:8000/api/v1/decisions/task-assignment
Content-Type: application/json

{
  "task_id": 1
}
```

Response:
```json
{
  "task_id": "1",
  "task_title": "Fix critical login bug",
  "assigned_user_id": "101",
  "assigned_user_name": "Alice Johnson",
  "confidence": 0.85,
  "explanation": "Detailed explanation of the decision...",
  "ethical_analysis": {
    "fairness_score": 0.9,
    "ethical_concerns": [],
    "reasoning": "..."
  },
  "risk_assessment": {
    "overall_risk_level": "low",
    "risk_factors": [...],
    "recommendation": "approve"
  },
  "performance_metrics": {
    "performance_impact": "positive",
    "growth_opportunity": 0.8
  },
  "reasoning_trace": [
    "Reasoning: Generated 3 candidate options...",
    "Ethics: Evaluated fairness and workload distribution...",
    "Risk: Assessed deadline and quality risks...",
    "Performance: Evaluated growth opportunity...",
    "Decision: Made final decision based on all factors..."
  ],
  "timestamp": "2025-12-20T10:30:00"
}
```

## Using cURL for Testing

```bash
# Health check
curl http://localhost:8000/health

# Task assignment decision
curl -X POST http://localhost:8000/api/v1/decisions/task-assignment \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'
```

## Using Postman

1. Import the following request:
   - Method: POST
   - URL: `http://localhost:8000/api/v1/decisions/task-assignment`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```json
     {
       "task_id": 1
     }
     ```

## Troubleshooting

### "OpenAI API key not found"

Make sure your `.env` file exists in the `ai-backend` directory and contains:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### "Connection refused to localhost:3000"

Make sure either:
- The mock server is running: `python tests/mock_server.py`
- OR your NestJS backend is running: `npm start`

### "Task not found"

The task ID must exist in your database or mock data. Try with task_id=1 first.

### Slow responses

The AI decision process takes 30-60 seconds as it runs through multiple agents. This is normal.

## Next Steps

### 1. Integrate with Your NestJS Backend

Update your NestJS backend to call the AI service:

```typescript
// In your tasks service
async assignTaskWithAI(taskId: number) {
  const response = await fetch('http://localhost:8000/api/v1/decisions/task-assignment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_id: taskId })
  });
  
  const decision = await response.json();
  
  // Update the task with the assignment
  await this.tasksRepository.update(taskId, {
    assignee_id: parseInt(decision.assigned_user_id)
  });
  
  return decision;
}
```

### 2. Add More Agents

You can extend the system by:
- Adding conflict resolution agent
- Adding performance review agent
- Adding workload balancing agent

### 3. Enhance the Data Agent

The Data Agent can be enhanced to:
- Calculate more sophisticated workload metrics
- Fetch historical performance data
- Integrate with calendar/availability systems

### 4. Production Deployment

For production:
1. Set proper CORS origins in `main.py`
2. Use environment-specific configurations
3. Add authentication/authorization
4. Deploy with Docker
5. Add monitoring and logging
6. Use a production-grade API gateway

## Understanding the GoT Reasoning

The system uses Graph of Thoughts (GoT) reasoning:

1. **Reasoning Agent**: Generates multiple candidate options
2. **Ethics Agent**: Evaluates each option for fairness and ethical concerns
3. **Risk Agent**: Assesses risks associated with each option
4. **Performance Agent**: Evaluates performance and growth implications
5. **Decision Agent**: Weighs all factors and makes final decision
6. **Explainability Agent**: Generates human-readable explanation

Each step is transparent and traceable, ensuring you understand why the AI made its decision.

## Support

For issues or questions:
1. Check the logs in the terminal
2. Verify your `.env` file configuration
3. Ensure all dependencies are installed
4. Check that ports 3000 and 8000 are available

## License

This project is part of the HCAT system.
