"""
Models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TaskAssignmentRequest(BaseModel):
    """Request model for task assignment decision"""
    task_id: int = Field(..., description="ID of the task to assign")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1
            }
        }


class DecisionResponse(BaseModel):
    """Response model for AI decision"""
    task_id: str
    task_title: str
    assigned_user_id: str
    assigned_user_name: Optional[str] = None
    confidence: float
    explanation: str
    detailed_reasoning: Optional[str] = None  # New field for comprehensive explanation
    ethical_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    reasoning_trace: List[str]
    reassignment_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "1",
                "task_title": "Fix login page bug",
                "assigned_user_id": "5",
                "assigned_user_name": "Alice",
                "confidence": 0.85,
                "explanation": "Task assigned to Alice based on...",
                "ethical_analysis": {
                    "fairness_score": 0.9,
                    "ethical_concerns": []
                },
                "risk_assessment": {
                    "overall_risk_level": "low"
                },
                "performance_metrics": {
                    "performance_impact": "positive"
                },
                "reasoning_trace": ["Step 1...", "Step 2..."],
                "timestamp": "2025-12-20T10:30:00"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ===== Use Case 2: Conflict Resolution =====

class ConflictResolutionRequest(BaseModel):
    """Request model for conflict resolution"""
    conflict_type: str = Field(..., description="Type of conflict (speed_vs_quality, deadline_vs_wellbeing, etc.)")
    project_id: int = Field(..., description="ID of the project with conflict")
    task_ids: List[int] = Field(..., description="IDs of tasks involved in conflict")
    business_priorities: List[str] = Field(..., description="Business priorities")
    deadline_pressure: Optional[str] = Field("medium", description="Deadline pressure level (low|medium|high)")
    quality_concerns: Optional[List[str]] = Field(default_factory=list, description="Quality concerns")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conflict_type": "speed_vs_quality",
                "project_id": 1,
                "task_ids": [1, 2, 3],
                "business_priorities": ["customer_satisfaction", "revenue"],
                "deadline_pressure": "high",
                "quality_concerns": ["testing", "code_review"]
            }
        }


class ConflictResolutionResponse(BaseModel):
    """Response model for conflict resolution"""
    conflict_type: str
    decision: str
    timeline_adjustment: str
    scope_adjustment: str
    executive_summary: str
    detailed_reasoning: str
    ethical_justification: str
    action_items: List[Dict[str, str]]
    stakeholder_messaging: Dict[str, str]
    trade_offs: Dict[str, Any]
    success_metrics: List[str]
    contingency_plan: str
    reasoning_trace: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "conflict_type": "speed_vs_quality",
                "decision": "balanced_approach",
                "timeline_adjustment": "extend_by_1_day",
                "scope_adjustment": "none",
                "executive_summary": "Extended deadline by 1 day to maintain quality standards while minimizing delay.",
                "detailed_reasoning": "After analyzing stakeholder perspectives...",
                "ethical_justification": "Prioritized quality and team well-being over schedule adherence.",
                "action_items": [{"action": "Update testing schedule", "owner": "QA Team", "timeline": "Tomorrow"}],
                "stakeholder_messaging": {"team": "Communicated 1-day extension...", "business": "Explained quality rationale..."},
                "trade_offs": {"speed": -1, "quality": 2, "team_wellbeing": 2},
                "success_metrics": ["Quality maintained", "No burnout incidents"],
                "contingency_plan": "If further delays, reduce scope of feature X",
                "reasoning_trace": ["Step 1...", "Step 2..."],
                "timestamp": "2025-12-20T10:30:00"
            }
        }


# ===== Use Case 3: Performance Evaluation =====

class PerformanceReviewRequest(BaseModel):
    """Request model for performance review"""
    user_id: Optional[int] = Field(None, description="ID of the user to review (if single user)")
    team_id: Optional[int] = Field(None, description="ID of the team to review (if team-wide)")
    review_period: str = Field(..., description="Review period (weekly, monthly, quarterly)")
    include_peer_feedback: Optional[bool] = Field(True, description="Include peer feedback in analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "team_id": 1,
                "review_period": "monthly",
                "include_peer_feedback": True
            }
        }


class PerformanceReviewResponse(BaseModel):
    """Response model for performance review"""
    user_id: str
    user_name: str
    review_period: str
    rating: float  # Overall rating out of 5.0
    summary: str  # Brief summary of performance
    recommendation: str
    justification: str
    metrics: Dict[str, Any]
    strengths: List[str]
    areas_for_improvement: List[str]
    growth_opportunities: List[str]
    recognition_suggested: bool
    fairness_check: str
    ethical_considerations: str
    comparison_to_peers: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "5",
                "user_name": "Priya",
                "review_period": "monthly",
                "recommendation": "recognition",
                "justification": "Consistent high performance, mentoring peers, and task completion rate 20% above average.",
                "metrics": {
                    "task_completion_rate": 0.95,
                    "avg_complexity": 7.8,
                    "peer_mentoring": 5,
                    "teamwork_score": 0.92
                },
                "strengths": ["High quality work", "Peer mentoring", "Consistent delivery"],
                "areas_for_improvement": ["Documentation", "Meeting attendance"],
                "growth_opportunities": ["Lead a project", "Technical workshops"],
                "recognition_suggested": True,
                "fairness_check": "Anti-bias filters applied",
                "ethical_considerations": "Evaluated objectively using quantitative metrics",
                "comparison_to_peers": {"percentile": 85},
                "timestamp": "2025-12-20T10:30:00"
            }
        }


# ===== Use Case 5: Decision Audit =====

class DecisionLogResponse(BaseModel):
    """Response model for decision log entry"""
    decision_id: str
    decision_type: str
    timestamp: str
    summary: str
    details: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "DEC-20251220103000-1",
                "decision_type": "task_assignment",
                "timestamp": "2025-12-20T10:30:00",
                "summary": "Assigned task 'Fix login bug' to Alice",
                "details": {"task_id": "1", "assigned_user_id": "5"}
            }
        }


# ===== Use Case 4: Risk Assessment & Conflict Analysis =====

class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment and conflict analysis"""
    project_id: int = Field(..., description="ID of the project to assess")
    team_id: Optional[int] = Field(None, description="ID of specific team (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "team_id": 1
            }
        }


class RiskAssessmentResponse(BaseModel):
    """Response model for risk assessment and conflict analysis"""
    project_id: int
    overall_risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: float  # 0.0 to 1.0
    executive_summary: str
    detailed_analysis: str
    critical_risks: List[Dict[str, Any]]
    conflicts_detected: List[Dict[str, Any]]
    blocked_tasks: List[Dict[str, Any]]
    overloaded_members: List[Dict[str, Any]]
    deadline_risks: List[Dict[str, Any]]
    mitigation_strategies: List[str]
    recommended_actions: List[Dict[str, str]]
    stakeholder_message: str
    confidence_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "overall_risk_level": "HIGH",
                "risk_score": 0.75,
                "executive_summary": "Project faces high deadline risk with 3 critical blocked tasks",
                "detailed_analysis": "Detailed analysis...",
                "critical_risks": [{"type": "deadline", "severity": "high", "description": "..."}],
                "conflicts_detected": [{"type": "speed_vs_quality", "tasks": [1, 2]}],
                "blocked_tasks": [{"task_id": 10, "blocked_by": [1], "impact": "high"}],
                "overloaded_members": [{"user_id": 201, "workload": 13, "threshold": 10}],
                "deadline_risks": [{"task_id": 1, "days_remaining": 2, "completion": 60}],
                "mitigation_strategies": ["Extend deadline by 2 days", "Reassign tasks"],
                "recommended_actions": [{"action": "Extend deadline", "priority": "high"}],
                "stakeholder_message": "Communicate timeline adjustment...",
                "confidence_score": 0.85,
                "timestamp": "2026-01-03T10:30:00"
            }
        }
