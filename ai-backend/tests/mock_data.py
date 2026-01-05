"""
Mock data for testing the AI backend - Enhanced for 6 Use Cases Demo
Supports: Task Assignment, Conflict Resolution, Performance Evaluation, 
Risk Assessment, Decision Logging, Stakeholder Communication
"""
from datetime import datetime, timedelta

# Current date for demo: Jan 3, 2026
# Project deadline: Jan 10, 2026 (7 days away - conflict scenario!)

# Mock tasks data - Enhanced with conflict scenarios
MOCK_TASKS = [
    # === DEVELOPMENT TEAM TASKS (Dev Manager: 200) ===
    # High priority tasks nearing deadline
    {
        "id": 1,
        "title": "Complete Payment Gateway Integration",
        "description": "Critical: Integrate Stripe API for subscription payments. Blocking QA testing.",
        "assignee_id": 201,
        "story_points": 8,
        "sprint": "Sprint 25",
        "deadline": "2026-01-05",  # 2 days away!
        "project_id": 1,
        "difficulty": "HIGH",
        "status": "IN_PROGRESS",
        "assigned_by": 200,
        "priority": "CRITICAL",
        "required_skills": ["Backend", "API Integration", "Security"],
        "progress": 60,
        "risk_level": "HIGH",
        "blocking_tasks": [10, 11]  # Blocking QA tasks
    },
    {
        "id": 2,
        "title": "User Dashboard Performance Optimization",
        "description": "Dashboard loading time exceeds 5 seconds. Need to optimize queries and caching.",
        "assignee_id": 202,
        "story_points": 5,
        "sprint": "Sprint 25",
        "deadline": "2026-01-06",  # 3 days away
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "IN_PROGRESS",
        "assigned_by": 200,
        "priority": "HIGH",
        "required_skills": ["Frontend", "Performance", "React"],
        "progress": 40,
        "risk_level": "MEDIUM"
    },
    {
        "id": 3,
        "title": "Implement Real-time Notifications",
        "description": "WebSocket implementation for real-time user notifications",
        "assignee_id": 203,
        "story_points": 8,
        "sprint": "Sprint 25",
        "deadline": "2026-01-08",  # 5 days away
        "project_id": 1,
        "difficulty": "HIGH",
        "status": "IN_PROGRESS",
        "assigned_by": 200,
        "priority": "MEDIUM",
        "required_skills": ["Backend", "WebSocket", "Node.js"],
        "progress": 30,
        "risk_level": "MEDIUM"
    },
    {
        "id": 4,
        "title": "API Documentation Update",
        "description": "Update Swagger docs for all new v2 endpoints",
        "assignee_id": None,  # UNASSIGNED - Use Case 1 demo
        "story_points": 3,
        "sprint": "Sprint 25",
        "deadline": "2026-01-07",
        "project_id": 1,
        "team_id": 1,  # Dev team
        "difficulty": "LOW",
        "status": "READY",
        "assigned_by": 200,
        "priority": "MEDIUM",
        "required_skills": ["Documentation", "API", "Technical Writing"],
        "progress": 0,
        "risk_level": "LOW"
    },
    {
        "id": 7,
        "title": "Frontend UI Refactoring - Complex Component Architecture",
        "description": "COMPLEX: Redesign React component hierarchy for performance and maintainability. Requires deep expertise in component optimization, state management patterns, and performance profiling.",
        "assignee_id": None,  # UNASSIGNED - Needs expert assignment
        "story_points": 13,
        "sprint": "Sprint 25",
        "deadline": "2026-01-09",
        "project_id": 1,
        "team_id": 1,  # Dev team
        "difficulty": "HIGH",
        "status": "READY",
        "assigned_by": 200,
        "priority": "HIGH",
        "required_skills": ["Frontend", "React", "Performance", "Architecture"],
        "progress": 0,
        "risk_level": "MEDIUM"
    },
    {
        "id": 8,
        "title": "Database Connection Pooling Optimization",
        "description": "SIMPLE: Configure and optimize database connection pooling for staging environment. Good learning opportunity for junior developers.",
        "assignee_id": 205,  # Assigned to Rajesh (Junior, learning task)
        "story_points": 2,
        "sprint": "Sprint 25",
        "deadline": "2026-01-08",
        "project_id": 1,
        "difficulty": "LOW",
        "status": "READY",
        "assigned_by": 200,
        "priority": "LOW",
        "required_skills": ["Database", "Configuration"],
        "progress": 0,
        "risk_level": "LOW"
    },
    {
        "id": 5,
        "title": "Database Migration Script",
        "description": "Write migration scripts for v2 schema changes",
        "assignee_id": 201,
        "story_points": 5,
        "sprint": "Sprint 25",
        "deadline": "2026-01-09",
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "READY",
        "assigned_by": 200,
        "priority": "HIGH",
        "required_skills": ["Database", "SQL", "Backend"],
        "progress": 0,
        "risk_level": "MEDIUM"
    },
    {
        "id": 6,
        "title": "Security Audit Fixes",
        "description": "Address vulnerabilities found in security audit",
        "assignee_id": 204,
        "story_points": 6,
        "sprint": "Sprint 25",
        "deadline": "2026-01-10",  # Final deadline!
        "project_id": 1,
        "difficulty": "HIGH",
        "status": "IN_PROGRESS",
        "assigned_by": 200,
        "priority": "CRITICAL",
        "required_skills": ["Security", "Backend", "Testing"],
        "progress": 50,
        "risk_level": "HIGH"
    },
    
    # === QA TEAM TASKS (QA Manager: 210) ===
    # Blocked by dev tasks - conflict scenario!
    {
        "id": 10,
        "title": "Payment Gateway Integration Testing",
        "description": "BLOCKED: Waiting for Task #1 completion. Critical path item.",
        "assignee_id": 211,
        "story_points": 5,
        "sprint": "Sprint 25",
        "deadline": "2026-01-07",  # 4 days away, but blocked!
        "project_id": 1,
        "difficulty": "HIGH",
        "status": "BLOCKED",
        "assigned_by": 210,
        "priority": "CRITICAL",
        "required_skills": ["Testing", "API Testing", "Automation"],
        "progress": 0,
        "risk_level": "HIGH",
        "blocked_by": [1]
    },
    {
        "id": 11,
        "title": "End-to-End Payment Flow Testing",
        "description": "BLOCKED: Complete payment flow testing including security scenarios",
        "assignee_id": 212,
        "story_points": 6,
        "sprint": "Sprint 25",
        "deadline": "2026-01-08",  # 5 days away, blocked!
        "project_id": 1,
        "difficulty": "HIGH",
        "status": "BLOCKED",
        "assigned_by": 210,
        "priority": "CRITICAL",
        "required_skills": ["Testing", "Security Testing", "Manual Testing"],
        "progress": 0,
        "risk_level": "HIGH",
        "blocked_by": [1]
    },
    {
        "id": 12,
        "title": "Performance Testing - Dashboard",
        "description": "Load testing and performance benchmarks for dashboard",
        "assignee_id": 213,
        "story_points": 4,
        "sprint": "Sprint 25",
        "deadline": "2026-01-07",
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "IN_PROGRESS",
        "assigned_by": 210,
        "priority": "HIGH",
        "required_skills": ["Performance Testing", "Automation"],
        "progress": 30,
        "risk_level": "MEDIUM"
    },
    {
        "id": 13,
        "title": "Regression Testing Suite Update",
        "description": "Update automated regression tests for v2 features",
        "assignee_id": 211,
        "story_points": 5,
        "sprint": "Sprint 25",
        "deadline": "2026-01-09",
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "IN_PROGRESS",
        "assigned_by": 210,
        "priority": "MEDIUM",
        "required_skills": ["Automation", "Testing", "Selenium"],
        "progress": 50,
        "risk_level": "LOW"
    },
    {
        "id": 14,
        "title": "Security Testing - Authentication",
        "description": "Penetration testing for authentication module",
        "assignee_id": 214,
        "story_points": 4,
        "sprint": "Sprint 25",
        "deadline": "2026-01-10",
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "READY",
        "assigned_by": 210,
        "priority": "HIGH",
        "required_skills": ["Security Testing", "Penetration Testing"],
        "progress": 0,
        "risk_level": "MEDIUM"
    },
    {
        "id": 15,
        "title": "Test Report Generation",
        "description": "Generate comprehensive test reports for stakeholders",
        "assignee_id": None,  # UNASSIGNED
        "story_points": 2,
        "sprint": "Sprint 25",
        "deadline": "2026-01-10",
        "project_id": 1,
        "difficulty": "LOW",
        "status": "READY",
        "assigned_by": 210,
        "priority": "MEDIUM",
        "required_skills": ["Testing", "Documentation", "Reporting"],
        "progress": 0,
        "risk_level": "LOW"
    },
    
    # === COMPLETED TASKS (for performance evaluation) ===
    {
        "id": 20,
        "title": "User Authentication Module",
        "description": "Completed OAuth 2.0 integration",
        "assignee_id": 201,
        "story_points": 8,
        "sprint": "Sprint 24",
        "deadline": "2025-12-28",
        "project_id": 1,
        "difficulty": "HIGH",
        "status": "COMPLETED",
        "assigned_by": 200,
        "priority": "HIGH",
        "required_skills": ["Backend", "Security"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-27",
        "quality_score": 95
    },
    {
        "id": 21,
        "title": "UI Component Library",
        "description": "Built reusable React component library",
        "assignee_id": 202,
        "story_points": 10,
        "sprint": "Sprint 24",
        "deadline": "2025-12-30",
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "COMPLETED",
        "assigned_by": 200,
        "priority": "MEDIUM",
        "required_skills": ["Frontend", "React"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-29",
        "quality_score": 92
    },
    {
        "id": 22,
        "title": "API Integration Tests",
        "description": "Comprehensive API test suite",
        "assignee_id": 211,
        "story_points": 6,
        "sprint": "Sprint 24",
        "deadline": "2025-12-30",
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "COMPLETED",
        "assigned_by": 210,
        "priority": "HIGH",
        "required_skills": ["Testing", "Automation"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-30",
        "quality_score": 98
    },
    # Additional completed tasks for better performance metrics
    {
        "id": 23,
        "title": "Code Review Process Implementation",
        "description": "Established automated code review workflow",
        "assignee_id": 201,
        "story_points": 5,
        "sprint": "Sprint 24",
        "deadline": "2025-12-25",
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "COMPLETED",
        "assigned_by": 200,
        "priority": "MEDIUM",
        "required_skills": ["DevOps", "Git"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-24",
        "quality_score": 93
    },
    {
        "id": 24,
        "title": "Mobile Responsive Design Fix",
        "description": "Fixed mobile layout issues across all pages",
        "assignee_id": 203,
        "story_points": 4,
        "sprint": "Sprint 24",
        "deadline": "2025-12-28",
        "project_id": 1,
        "difficulty": "LOW",
        "status": "COMPLETED",
        "assigned_by": 200,
        "priority": "MEDIUM",
        "required_skills": ["Frontend", "CSS"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-27",
        "quality_score": 90
    },
    {
        "id": 25,
        "title": "Database Optimization",
        "description": "Optimized slow queries and added indexes",
        "assignee_id": 204,
        "story_points": 6,
        "sprint": "Sprint 24",
        "deadline": "2025-12-29",
        "project_id": 1,
        "difficulty": "HIGH",
        "status": "COMPLETED",
        "assigned_by": 200,
        "priority": "HIGH",
        "required_skills": ["Database", "SQL"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-28",
        "quality_score": 96
    },
    {
        "id": 26,
        "title": "Unit Test Coverage Improvement",
        "description": "Increased test coverage from 60% to 85%",
        "assignee_id": 205,
        "story_points": 5,
        "sprint": "Sprint 24",
        "deadline": "2025-12-30",
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "COMPLETED",
        "assigned_by": 200,
        "priority": "MEDIUM",
        "required_skills": ["Testing", "Backend"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-29",
        "quality_score": 88
    },
    # QA team completed tasks
    {
        "id": 27,
        "title": "Automated Smoke Test Suite",
        "description": "Created comprehensive smoke test automation",
        "assignee_id": 212,
        "story_points": 7,
        "sprint": "Sprint 24",
        "deadline": "2025-12-27",
        "project_id": 1,
        "difficulty": "HIGH",
        "status": "COMPLETED",
        "assigned_by": 210,
        "priority": "HIGH",
        "required_skills": ["Automation", "Selenium"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-26",
        "quality_score": 97
    },
    {
        "id": 28,
        "title": "Accessibility Testing",
        "description": "WCAG 2.1 compliance testing and fixes",
        "assignee_id": 213,
        "story_points": 4,
        "sprint": "Sprint 24",
        "deadline": "2025-12-29",
        "project_id": 1,
        "difficulty": "MEDIUM",
        "status": "COMPLETED",
        "assigned_by": 210,
        "priority": "MEDIUM",
        "required_skills": ["Testing", "Accessibility"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-28",
        "quality_score": 91
    },
    {
        "id": 29,
        "title": "Cross-Browser Testing",
        "description": "Tested across Chrome, Firefox, Safari, Edge",
        "assignee_id": 214,
        "story_points": 3,
        "sprint": "Sprint 24",
        "deadline": "2025-12-30",
        "project_id": 1,
        "difficulty": "LOW",
        "status": "COMPLETED",
        "assigned_by": 210,
        "priority": "MEDIUM",
        "required_skills": ["Testing", "Manual Testing"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-29",
        "quality_score": 89
    },
    {
        "id": 30,
        "title": "Bug Tracking System Update",
        "description": "Migrated to new bug tracking platform",
        "assignee_id": 215,
        "story_points": 2,
        "sprint": "Sprint 24",
        "deadline": "2025-12-26",
        "project_id": 1,
        "difficulty": "LOW",
        "status": "COMPLETED",
        "assigned_by": 210,
        "priority": "LOW",
        "required_skills": ["Testing", "Tools"],
        "progress": 100,
        "risk_level": "LOW",
        "completion_date": "2025-12-25",
        "quality_score": 85
    }
]

# Mock users data - Enhanced with hierarchical structure
MOCK_USERS = [
    # === PROJECT MANAGER (sees overall progress only) ===
    {
        "id": 100,
        "name": "Sarah Martinez",
        "email": "sarah.martinez@company.com",
        "role": "PROJECT_MANAGER",
        "reports_to": None,
        "team_id": None,
        "project_id": 1,
        "joining_date": "2020-03-01",
        "experience_years": 8.5,
        "skills": ["Project Management", "Agile", "Leadership", "Stakeholder Communication"],
        "current_workload": 0,
        "availability": True,
        "recent_assignments_count": 0,
        "avg_task_complexity": 0.0,
        "estimated_completion_confidence": 0.95,
        "workload_story_points": 0
    },
    
    # === DEVELOPMENT MANAGER ===
    {
        "id": 200,
        "name": "Michael Chen",
        "email": "michael.chen@company.com",
        "role": "DEV_MANAGER",
        "reports_to": 100,
        "team_id": 1,
        "project_id": 1,
        "joining_date": "2021-01-15",
        "experience_years": 6.0,
        "skills": ["Backend", "Frontend", "Architecture", "Team Leadership"],
        "current_workload": 0,
        "availability": True,
        "recent_assignments_count": 0,
        "avg_task_complexity": 0.0,
        "estimated_completion_confidence": 0.90,
        "workload_story_points": 0
    },
    
    # === QA MANAGER ===
    {
        "id": 210,
        "name": "Priya Patel",
        "email": "priya.patel@company.com",
        "role": "QA_MANAGER",
        "reports_to": 100,
        "team_id": 2,
        "project_id": 1,
        "joining_date": "2021-06-01",
        "experience_years": 5.5,
        "skills": ["Testing", "Quality Assurance", "Automation", "Team Leadership"],
        "current_workload": 0,
        "availability": True,
        "recent_assignments_count": 0,
        "avg_task_complexity": 0.0,
        "estimated_completion_confidence": 0.92,
        "workload_story_points": 0
    },
    
    # === DEVELOPMENT TEAM (reports to Dev Manager 200) ===
    {
        "id": 201,
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@company.com",
        "role": "EMPLOYEE",
        "reports_to": 200,
        "team_id": 1,
        "project_id": 1,
        "joining_date": "2022-01-10",
        "experience_years": 4.0,
        "skills": ["Backend", "Node.js", "API Integration", "Database", "Security", "SQL"],
        "current_workload": 13,  # OVERLOADED: Tasks 1, 5 (8+5=13 points)
        "availability": True,
        "recent_assignments_count": 8,
        "avg_task_complexity": 0.85,
        "estimated_completion_confidence": 0.80,
        "workload_story_points": 13,
        "performance_metrics": {
            "completed_tasks_last_sprint": 5,
            "avg_quality_score": 94,
            "on_time_delivery_rate": 0.90,
            "mentoring_count": 3,
            "code_review_contributions": 45
        }
    },
    {
        "id": 202,
        "name": "Emily Rodriguez",
        "email": "emily.rodriguez@company.com",
        "role": "EMPLOYEE",
        "reports_to": 200,
        "team_id": 1,
        "project_id": 1,
        "joining_date": "2022-08-15",
        "experience_years": 3.5,
        "skills": ["Frontend", "React", "Performance", "UI/UX", "TypeScript"],
        "current_workload": 5,  # Balanced: Task 2 (5 points)
        "availability": True,
        "recent_assignments_count": 4,
        "avg_task_complexity": 0.65,
        "estimated_completion_confidence": 0.85,
        "workload_story_points": 5,
        "performance_metrics": {
            "completed_tasks_last_sprint": 4,
            "avg_quality_score": 92,
            "on_time_delivery_rate": 0.95,
            "mentoring_count": 2,
            "code_review_contributions": 38
        }
    },
    {
        "id": 203,
        "name": "James Thompson",
        "email": "james.thompson@company.com",
        "role": "EMPLOYEE",
        "reports_to": 200,
        "team_id": 1,
        "project_id": 1,
        "joining_date": "2023-02-01",
        "experience_years": 2.5,
        "skills": ["Backend", "WebSocket", "Node.js", "Real-time Systems"],
        "current_workload": 8,  # High: Task 3 (8 points)
        "availability": True,
        "recent_assignments_count": 3,
        "avg_task_complexity": 0.75,
        "estimated_completion_confidence": 0.70,
        "workload_story_points": 8,
        "performance_metrics": {
            "completed_tasks_last_sprint": 3,
            "avg_quality_score": 88,
            "on_time_delivery_rate": 0.85,
            "mentoring_count": 1,
            "code_review_contributions": 22
        }
    },
    {
        "id": 204,
        "name": "Linda Zhang",
        "email": "linda.zhang@company.com",
        "role": "EMPLOYEE",
        "reports_to": 200,
        "team_id": 1,
        "project_id": 1,
        "joining_date": "2021-11-20",
        "experience_years": 4.2,
        "skills": ["Security", "Backend", "Testing", "Penetration Testing", "API"],
        "current_workload": 6,  # Moderate: Task 6 (6 points)
        "availability": True,
        "recent_assignments_count": 5,
        "avg_task_complexity": 0.80,
        "estimated_completion_confidence": 0.88,
        "workload_story_points": 6,
        "performance_metrics": {
            "completed_tasks_last_sprint": 4,
            "avg_quality_score": 96,
            "on_time_delivery_rate": 0.92,
            "mentoring_count": 4,
            "code_review_contributions": 52
        }
    },
    {
        "id": 205,
        "name": "Alex Johnson",
        "email": "alex.johnson@company.com",
        "role": "EMPLOYEE",
        "reports_to": 200,
        "team_id": 1,
        "project_id": 1,
        "joining_date": "2022-05-10",
        "experience_years": 3.8,
        "skills": ["Documentation", "API", "Technical Writing", "Backend", "Frontend"],
        "current_workload": 0,  # AVAILABLE - perfect for Task 4!
        "availability": True,
        "recent_assignments_count": 3,
        "avg_task_complexity": 0.50,
        "estimated_completion_confidence": 0.90,
        "workload_story_points": 0,
        "performance_metrics": {
            "completed_tasks_last_sprint": 5,
            "avg_quality_score": 95,
            "on_time_delivery_rate": 1.0,
            "mentoring_count": 2,
            "code_review_contributions": 30
        }
    },
    
    # === QA TEAM (reports to QA Manager 210) ===
    {
        "id": 211,
        "name": "Nina Desai",
        "email": "nina.desai@company.com",
        "role": "EMPLOYEE",
        "reports_to": 210,
        "team_id": 2,
        "project_id": 1,
        "joining_date": "2022-03-15",
        "experience_years": 3.8,
        "skills": ["Testing", "API Testing", "Automation", "Selenium"],
        "current_workload": 10,  # OVERLOADED: Tasks 10, 13 (5+5=10 points)
        "availability": True,
        "recent_assignments_count": 6,
        "avg_task_complexity": 0.75,
        "estimated_completion_confidence": 0.82,
        "workload_story_points": 10,
        "performance_metrics": {
            "completed_tasks_last_sprint": 6,
            "avg_quality_score": 98,
            "on_time_delivery_rate": 0.88,
            "mentoring_count": 5,
            "code_review_contributions": 42
        }
    },
    {
        "id": 212,
        "name": "Omar Hassan",
        "email": "omar.hassan@company.com",
        "role": "EMPLOYEE",
        "reports_to": 210,
        "team_id": 2,
        "project_id": 1,
        "joining_date": "2023-01-20",
        "experience_years": 2.9,
        "skills": ["Testing", "Security Testing", "Manual Testing", "API Testing"],
        "current_workload": 6,  # Moderate: Task 11 (6 points)
        "availability": True,
        "recent_assignments_count": 4,
        "avg_task_complexity": 0.70,
        "estimated_completion_confidence": 0.78,
        "workload_story_points": 6,
        "performance_metrics": {
            "completed_tasks_last_sprint": 4,
            "avg_quality_score": 90,
            "on_time_delivery_rate": 0.82,
            "mentoring_count": 1,
            "code_review_contributions": 18
        }
    },
    {
        "id": 213,
        "name": "Sophie Martinez",
        "email": "sophie.martinez@company.com",
        "role": "EMPLOYEE",
        "reports_to": 210,
        "team_id": 2,
        "project_id": 1,
        "joining_date": "2022-09-01",
        "experience_years": 3.3,
        "skills": ["Performance Testing", "Automation", "Load Testing", "Testing"],
        "current_workload": 4,  # Light: Task 12 (4 points)
        "availability": True,
        "recent_assignments_count": 3,
        "avg_task_complexity": 0.65,
        "estimated_completion_confidence": 0.85,
        "workload_story_points": 4,
        "performance_metrics": {
            "completed_tasks_last_sprint": 3,
            "avg_quality_score": 91,
            "on_time_delivery_rate": 0.90,
            "mentoring_count": 2,
            "code_review_contributions": 25
        }
    },
    {
        "id": 214,
        "name": "Carlos Mendez",
        "email": "carlos.mendez@company.com",
        "role": "EMPLOYEE",
        "reports_to": 210,
        "team_id": 2,
        "project_id": 1,
        "joining_date": "2021-10-15",
        "experience_years": 4.2,
        "skills": ["Security Testing", "Penetration Testing", "Testing", "Automation"],
        "current_workload": 0,  # AVAILABLE - perfect for Task 14!
        "availability": True,
        "recent_assignments_count": 4,
        "avg_task_complexity": 0.80,
        "estimated_completion_confidence": 0.92,
        "workload_story_points": 0,
        "performance_metrics": {
            "completed_tasks_last_sprint": 5,
            "avg_quality_score": 97,
            "on_time_delivery_rate": 0.95,
            "mentoring_count": 4,
            "code_review_contributions": 48
        }
    },
    {
        "id": 215,
        "name": "Maya Singh",
        "email": "maya.singh@company.com",
        "role": "EMPLOYEE",
        "reports_to": 210,
        "team_id": 2,
        "project_id": 1,
        "joining_date": "2023-04-01",
        "experience_years": 2.7,
        "skills": ["Testing", "Documentation", "Reporting", "Manual Testing"],
        "current_workload": 0,  # AVAILABLE - perfect for Task 15!
        "availability": True,
        "recent_assignments_count": 2,
        "avg_task_complexity": 0.55,
        "estimated_completion_confidence": 0.88,
        "workload_story_points": 0,
        "performance_metrics": {
            "completed_tasks_last_sprint": 4,
            "avg_quality_score": 93,
            "on_time_delivery_rate": 0.93,
            "mentoring_count": 1,
            "code_review_contributions": 15
        }
    }
]

# Mock teams data - Enhanced hierarchy
MOCK_TEAMS = [
    {
        "id": 1,
        "team_name": "Development Team",
        "manager_id": 200,
        "manager_name": "Michael Chen",
        "member_count": 5,
        "current_sprint": "Sprint 25",
        "team_workload_points": 32,  # Total across all dev team members
        "completion_rate": 0.87
    },
    {
        "id": 2,
        "team_name": "Quality Assurance Team",
        "manager_id": 210,
        "manager_name": "Priya Patel",
        "member_count": 5,
        "current_sprint": "Sprint 25",
        "team_workload_points": 20,  # Total across all QA team members
        "completion_rate": 0.92
    }
]

# Mock projects data - Enhanced with conflict scenario
MOCK_PROJECTS = [
    {
        "id": 1,
        "name": "Customer Portal v2.0 Launch",
        "description": "Critical release: Payment integration, performance improvements, and security enhancements",
        "start_date": "2025-10-01",
        "end_date": "2026-01-10",  # 7 DAYS AWAY - CONFLICT!
        "status": "AT_RISK",
        "created_at": "2025-09-15",
        "completion_percentage": 68,
        "total_tasks": 25,
        "completed_tasks": 17,
        "in_progress_tasks": 6,
        "blocked_tasks": 2,  # CONFLICT: Tasks 10, 11 blocked by Task 1
        "at_risk_count": 4,
        "critical_path_items": [1, 10, 11],  # Payment integration chain
        "risks": [
            {
                "type": "TIMELINE",
                "severity": "HIGH",
                "description": "QA tasks blocked by incomplete dev work. 2 critical tasks at risk of missing deadline."
            },
            {
                "type": "QUALITY",
                "severity": "MEDIUM",
                "description": "Rushing to meet deadline may compromise testing coverage"
            },
            {
                "type": "RESOURCE",
                "severity": "HIGH",
                "description": "Dev team member (Rajesh) overloaded with 13 story points. Burnout risk."
            }
        ],
        "stakeholders": ["Product Team", "C-Level Executives", "Customer Success"],
        "business_impact": "HIGH - Revenue generation dependent on payment feature"
    }
]

# Mock managers data - Enhanced hierarchy
MOCK_MANAGERS = [
    {
        "id": 100,
        "name": "Sarah Martinez",
        "email": "sarah.martinez@company.com",
        "role": "PROJECT_MANAGER",
        "team_id": None,
        "project_id": 1,
        "manages_teams": [1, 2],
        "direct_reports": [200, 210]
    },
    {
        "id": 200,
        "name": "Michael Chen",
        "email": "michael.chen@company.com",
        "role": "DEV_MANAGER",
        "team_id": 1,
        "project_id": 1,
        "reports_to": 100,
        "direct_reports": [201, 202, 203, 204, 205]
    },
    {
        "id": 210,
        "name": "Priya Patel",
        "email": "priya.patel@company.com",
        "role": "QA_MANAGER",
        "team_id": 2,
        "project_id": 1,
        "reports_to": 100,
        "direct_reports": [211, 212, 213, 214, 215]
    }
]

# Mock decision logs - Use Case 5: Transparent Decision Logging
MOCK_DECISION_LOGS = [
    {
        "id": 1,
        "decision_type": "TIMELINE_ADJUSTMENT",
        "timestamp": "2026-01-02T14:30:00",
        "decision_maker": "Sarah Martinez",
        "decision": "Proposed 2-day deadline extension to Jan 12",
        "reasoning": "Payment integration (Task 1) is 60% complete but blocking 2 critical QA tasks. Team member Rajesh is overloaded (13 story points). Rushing increases defect risk by 35%.",
        "ethical_consideration": "Prioritized team well-being and quality over strict deadline adherence",
        "alternatives_considered": [
            "Skip thorough testing (rejected - quality risk)",
            "Reassign tasks from Rajesh (rejected - knowledge transfer overhead)",
            "Extend deadline by 2 days (recommended)"
        ],
        "impact": "Reduces burnout risk by 40%, increases QA coverage to 95%",
        "status": "PROPOSED",
        "requires_approval_from": [100]
    },
    {
        "id": 2,
        "decision_type": "TASK_ASSIGNMENT",
        "timestamp": "2026-01-03T09:15:00",
        "decision_maker": "AI System",
        "decision": "Assigned API Documentation (Task 4) to Alex Johnson",
        "reasoning": "Alex has perfect skill match (Documentation, API, Technical Writing), zero current workload, 90% confidence score, and 100% on-time delivery rate",
        "ethical_consideration": "Fair workload distribution - Alex has completed recent work and is available",
        "alternatives_considered": [
            "Emily Rodriguez (rejected - already loaded with Task 2)",
            "Alex Johnson (selected - available and skilled)"
        ],
        "impact": "Balanced workload distribution, high confidence completion",
        "status": "APPROVED"
    }
]

# Mock conflict scenarios - Use Case 2
MOCK_CONFLICTS = [
    {
        "id": 1,
        "conflict_type": "PRIORITY_CONFLICT",
        "severity": "HIGH",
        "description": "Business Priority (Speed) vs Quality & Team Wellbeing",
        "conflicting_goals": [
            {
                "goal": "Launch by Jan 10 deadline",
                "stakeholder": "Business/C-Level",
                "priority": "CRITICAL"
            },
            {
                "goal": "Ensure 95% test coverage",
                "stakeholder": "QA Team",
                "priority": "HIGH"
            },
            {
                "goal": "Prevent team burnout",
                "stakeholder": "Dev Team",
                "priority": "HIGH"
            }
        ],
        "root_cause": "Payment integration delayed, blocking QA critical path",
        "ai_recommendation": {
            "solution": "Request 2-day extension to Jan 12, 2026",
            "rationale": "A 2-day delay ensures quality compliance, reduces team stress, and maintains customer trust. The business impact of shipping defective payment features outweighs 2-day delay.",
            "trade_offs": {
                "speed": "2-day delay in launch",
                "quality": "Achieves 95% test coverage vs 60% if rushed",
                "wellbeing": "Reduces burnout risk from 65% to 25%",
                "business": "Minimal revenue impact vs high reputation risk"
            },
            "ethical_reasoning": "Prioritizes sustainable delivery over short-term speed. Long-term customer trust and team health outweigh immediate deadline pressure."
        }
    }
]

# Mock performance data - Use Case 3: Performance Evaluation
MOCK_PERFORMANCE_RANKINGS = [
    {
        "evaluation_period": "Sprint 24 (Dec 2025)",
        "top_performers": [
            {
                "user_id": 211,
                "name": "Nina Desai",
                "score": 97,
                "reasoning": "Highest quality score (98 avg), mentored 5 team members, completed 6 tasks with 88% on-time rate, consistently exceeded expectations",
                "recognition_category": "Excellence in Quality & Mentorship"
            },
            {
                "user_id": 204,
                "name": "Linda Zhang",
                "score": 96,
                "reasoning": "Exceptional security audit work (96 quality score), mentored 4 peers, 92% on-time delivery, expert in critical security domain",
                "recognition_category": "Technical Excellence & Leadership"
            },
            {
                "user_id": 201,
                "name": "Rajesh Kumar",
                "score": 94,
                "reasoning": "Delivered complex authentication module (95 quality), 90% on-time rate despite high workload, strong technical contributions",
                "recognition_category": "High Performance Under Pressure"
            }
        ],
        "criteria": {
            "quality_score": 0.30,
            "on_time_delivery": 0.25,
            "task_complexity": 0.20,
            "mentoring_contributions": 0.15,
            "code_review_activity": 0.10
        },
        "fairness_checks": [
            "No gender bias detected (balanced representation)",
            "Experience level normalized in scoring",
            "Objective metrics only - no subjective favoritism"
        ]
    }
]


def get_mock_data():
    """Get all mock data for 6 use cases demo"""
    return {
        "tasks": MOCK_TASKS,
        "users": MOCK_USERS,
        "teams": MOCK_TEAMS,
        "projects": MOCK_PROJECTS,
        "managers": MOCK_MANAGERS,
        "decision_logs": MOCK_DECISION_LOGS,
        "conflicts": MOCK_CONFLICTS,
        "performance_rankings": MOCK_PERFORMANCE_RANKINGS
    }

