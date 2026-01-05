"""
Mock server to simulate NestJS backend for testing
Run this server to test the AI backend without needing the actual NestJS backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

from mock_data import (
    MOCK_TASKS,
    MOCK_USERS,
    MOCK_TEAMS,
    MOCK_PROJECTS,
    MOCK_MANAGERS,
    MOCK_DECISION_LOGS,
    MOCK_CONFLICTS,
    MOCK_PERFORMANCE_RANKINGS,
    get_mock_data
)

app = FastAPI(title="Mock NestJS Backend")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def root():
    return {"message": "Mock NestJS Backend for testing"}


@app.get("/tasks")
async def get_tasks():
    """Get all tasks"""
    return MOCK_TASKS


@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    """Get a specific task"""
    task = next((t for t in MOCK_TASKS if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/users")
async def get_users():
    """Get all users"""
    return MOCK_USERS


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get a specific user"""
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/teams")
async def get_teams():
    """Get all teams"""
    return MOCK_TEAMS


@app.get("/teams/{team_id}")
async def get_team(team_id: int):
    """Get a specific team"""
    team = next((t for t in MOCK_TEAMS if t["id"] == team_id), None)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@app.get("/projects")
async def get_projects():
    """Get all projects"""
    return MOCK_PROJECTS


@app.get("/projects/{project_id}")
async def get_project(project_id: int):
    """Get a specific project"""
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/managers")
async def get_managers():
    """Get all managers"""
    return MOCK_MANAGERS


@app.get("/decision-logs")
async def get_decision_logs():
    """Get all decision logs for Use Case 5"""
    return MOCK_DECISION_LOGS


@app.get("/conflicts")
async def get_conflicts():
    """Get all conflicts for Use Case 2"""
    return MOCK_CONFLICTS


@app.get("/performance-rankings")
async def get_performance_rankings():
    """Get performance rankings for Use Case 3"""
    return MOCK_PERFORMANCE_RANKINGS


@app.get("/all-data")
async def get_all_data():
    """Get all mock data - useful for frontend testing"""
    return get_mock_data()


if __name__ == "__main__":
    print("Starting Mock NestJS Backend on http://localhost:3000")
    print("This simulates your NestJS backend for testing purposes")
    uvicorn.run("mock_server:app", host="localhost", port=3000, reload=True)
