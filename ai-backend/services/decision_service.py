"""
Decision Service - Core business logic for AI decision making
"""
import logging
import json
import asyncio
from typing import Dict, Any, List
from agents.data_agent import data_agent
from workflows.decision_workflow import decision_workflow
from workflows.conflict_resolution_workflow import conflict_resolution_workflow
from services.decision_logger import decision_logger

logger = logging.getLogger(__name__)


class DecisionService:
    """Service for handling AI-powered task assignment decisions"""
    
    def __init__(self):
        self.data_agent = data_agent
        self.workflow = decision_workflow
        self.conflict_workflow = conflict_resolution_workflow
        self.logger = decision_logger
    
    async def make_task_assignment_decision(self, task_id: int) -> Dict[str, Any]:
        """
        Make an AI-powered decision for task assignment
        
        Args:
            task_id: ID of the task to assign
            
        Returns:
            Complete decision result with explanation
        """
        try:
            logger.info(f"Making decision for task {task_id}")
            
            # Step 1: Collect data using Data Agent
            logger.info("Collecting data from backend...")
            context = await self.data_agent.collect_decision_context(task_id)
            
            task = context["task"]
            users = context["users"]
            teams = context["teams"]
            
            logger.info(f"Collected: task={task['title']}, users={len(users)}, teams={len(teams)}")
            
            # Step 2: Run the decision workflow (GoT reasoning with LangGraph)
            logger.info("Running decision workflow...")
            try:
                # Run the synchronous/blocking workflow in a separate thread to avoid blocking the event loop.
                result = await asyncio.wait_for(
                    asyncio.to_thread(lambda: asyncio.run(self.workflow.run(task, users, teams))),
                    timeout=60.0
                )
            except asyncio.TimeoutError:
                logger.error("Decision workflow timed out")
                raise
            
            # Step 3: Find assigned user details
            final_decision = result.get("decision", {})
            assigned_user_id = final_decision.get("final_user_id", "")
            
            assigned_user = next(
                (u for u in users if str(u["id"]) == str(assigned_user_id)),
                None
            )
            
            # Step 4: Format the response
            response = {
                "task_id": str(task["id"]),
                "task_title": task["title"],
                "assigned_user_id": assigned_user_id,
                "assigned_user_name": assigned_user["name"] if assigned_user else None,
                "confidence": final_decision.get("confidence", 0.0),
                "explanation": result.get("explanation", ""),
                "ethical_analysis": result.get("ethical_analysis", {}),
                "risk_assessment": result.get("risk_assessment", {}),
                "performance_metrics": result.get("performance_metrics", {}),
                "reasoning_trace": result.get("reasoning_trace", []),
                "priority_factors": final_decision.get("priority_factors", []),
                "alternative_options": final_decision.get("alternative_options", []),
                "action_items": final_decision.get("action_items", [])
            }
            
            # Step 5: Log the decision for audit trail
            decision_id = self.logger.log_task_assignment_decision(
                task_id=response["task_id"],
                task_title=response["task_title"],
                assigned_user_id=response["assigned_user_id"],
                assigned_user_name=response["assigned_user_name"],
                confidence=response["confidence"],
                explanation=response["explanation"],
                ethical_analysis=response["ethical_analysis"],
                risk_assessment=response["risk_assessment"],
                performance_metrics=response["performance_metrics"],
                reasoning_trace=response["reasoning_trace"],
                priority_factors=response["priority_factors"],
                alternative_options=response["alternative_options"],
                action_items=response["action_items"]
            )
            
            response["decision_id"] = decision_id
            
            logger.info(f"Decision complete: Assigned to user {assigned_user_id}, logged as {decision_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error making decision: {e}", exc_info=True)
            raise
    
    async def resolve_conflict(
        self,
        conflict_type: str,
        project_id: int,
        task_ids: List[int],
        business_priorities: List[str],
        deadline_pressure: str = "medium",
        quality_concerns: List[str] = None
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between priorities (speed vs quality, deadlines vs wellbeing, etc.)
        Use Case 2: Conflict Resolution Between Priorities
        
        Args:
            conflict_type: Type of conflict (speed_vs_quality, deadline_vs_wellbeing, etc.)
            project_id: ID of the project with conflict
            task_ids: IDs of tasks involved in conflict
            business_priorities: List of business priorities
            deadline_pressure: Deadline pressure level (low|medium|high)
            quality_concerns: List of quality concerns
            
        Returns:
            Conflict resolution with recommendations and trade-offs
        """
        try:
            logger.info(f"Resolving conflict: {conflict_type} for project {project_id}")
            
            # Step 1: Collect data
            # Get project details
            project = await self.data_agent.fetch_project(project_id)
            
            # Get tasks involved in conflict
            tasks = []
            for task_id in task_ids:
                task_context = await self.data_agent.collect_decision_context(task_id)
                tasks.append(task_context["task"])
            
            # Get team details
            team = await self.data_agent.fetch_team(project.get("teamId"))
            users = await self.data_agent.fetch_users()
            
            # Calculate team wellbeing factors
            team_wellbeing_factors = {
                "average_workload": sum(u.get("workload", 0) for u in users) / len(users) if users else 0,
                "high_workload_users": [u["name"] for u in users if u.get("workload", 0) > 3],
                "deadline_pressure": deadline_pressure,
                "quality_concerns": quality_concerns or []
            }
            
            # Step 2: Run conflict resolution workflow
            logger.info("Running conflict resolution workflow...")
            result = await self.conflict_workflow.run(
                conflict_type=conflict_type,
                project=project,
                tasks=tasks,
                team=team,
                business_priorities=business_priorities,
                team_wellbeing_factors=team_wellbeing_factors
            )
            
            # Step 3: Extract resolution
            resolution = result.get("resolution", {})
            trade_offs = result.get("trade_offs", {})
            ethical_justification = result.get("ethical_justification", "")
            
            # Step 4: Format response
            response = {
                "conflict_type": conflict_type,
                "decision": resolution.get("decision", ""),
                "timeline_adjustment": resolution.get("timeline_adjustment", ""),
                "scope_adjustment": resolution.get("scope_adjustment", ""),
                "executive_summary": resolution.get("executive_summary", ""),
                "detailed_reasoning": resolution.get("detailed_reasoning", ""),
                "ethical_justification": ethical_justification,
                "action_items": resolution.get("action_items", []),
                "stakeholder_messaging": resolution.get("stakeholder_messaging", {}),
                "trade_offs": trade_offs,
                "success_metrics": resolution.get("success_metrics", []),
                "contingency_plan": resolution.get("contingency_plan", ""),
                "reasoning_trace": result.get("reasoning_trace", [])
            }
            
            # Step 5: Log the decision
            decision_id = self.logger.log_conflict_resolution(
                conflict_type=conflict_type,
                project_id=str(project_id),
                resolution=resolution,
                trade_offs=trade_offs,
                ethical_justification=ethical_justification,
                reasoning_trace=result.get("reasoning_trace", [])
            )
            
            response["decision_id"] = decision_id
            
            logger.info(f"Conflict resolution complete, logged as {decision_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}", exc_info=True)
            raise
    
    async def get_performance_review(
        self,
        user_id: int,
        review_period: str = "monthly",
        include_peer_feedback: bool = True
    ) -> Dict[str, Any]:
        """
        Get AI-powered performance review for a user
        Use Case 3: Performance Evaluation and Recognition
        
        Args:
            user_id: ID of the user to review
            review_period: Review period (weekly, monthly, quarterly)
            include_peer_feedback: Include peer feedback in analysis
            
        Returns:
            Performance review analysis with recognition recommendations
        """
        try:
            logger.info(f"Generating performance review for user {user_id}")
            
            # Step 1: Collect user data
            users = await self.data_agent.fetch_users()
            user = next((u for u in users if u["id"] == user_id), None)
            
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Step 2: Get user's task history
            tasks = await self.data_agent.fetch_tasks()
            user_tasks = [t for t in tasks if t.get("assignedUserId") == user_id]
            
            # Step 3: Calculate metrics
            total_tasks = len(user_tasks)
            completed_tasks = len([t for t in user_tasks if t.get("status") == "completed"])
            task_completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
            
            # Average complexity (assuming complexity is stored in task)
            avg_complexity = sum(t.get("complexity", 5) for t in user_tasks) / total_tasks if total_tasks > 0 else 5
            
            # Compare to team average
            all_users_workload = [u.get("workload", 0) for u in users]
            avg_workload = sum(all_users_workload) / len(all_users_workload) if all_users_workload else 0
            user_workload = user.get("workload", 0)
            
            metrics = {
                "task_completion_rate": round(task_completion_rate, 2),
                "avg_complexity": round(avg_complexity, 1),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "current_workload": user_workload,
                "team_avg_workload": round(avg_workload, 1),
                "workload_vs_average": round(user_workload - avg_workload, 1)
            }
            
            # Step 4: Use LLM to generate review and recommendations
            prompt = f"""
You are a Performance Review AI Agent.
Generate a fair, unbiased performance review for the following user.

USER: {user.get('name')} (ID: {user_id})
ROLE: {user.get('role', 'Developer')}
REVIEW PERIOD: {review_period}

METRICS:
{json.dumps(metrics, indent=2)}

TASKS COMPLETED: {completed_tasks}/{total_tasks}
TASK COMPLETION RATE: {task_completion_rate:.2%}
AVERAGE TASK COMPLEXITY: {avg_complexity}/10
CURRENT WORKLOAD: {user_workload} tasks
TEAM AVERAGE WORKLOAD: {avg_workload:.1f} tasks

Provide:
1. Overall recommendation (recognition|continue|improvement_needed)
2. Justification (2-3 sentences explaining the recommendation)
3. Strengths (list 3-5 specific strengths)
4. Areas for improvement (list 2-3 areas)
5. Growth opportunities (list 2-3 opportunities)
6. Recognition suggested: true/false
7. Fairness check: confirmation that anti-bias filters were applied
8. Ethical considerations: how objectivity was ensured

Return as JSON:
{{
    "rating": <numeric rating from 1.0 to 5.0>,
    "summary": "<2-3 sentence overall summary>",
    "recommendation": "<recognition|continue|improvement_needed>",
    "justification": "<detailed justification>",
    "strengths": ["<strength1>", "<strength2>", ...],
    "areas_for_improvement": ["<area1>", "<area2>", ...],
    "growth_opportunities": ["<opportunity1>", "<opportunity2>", ...],
    "recognition_suggested": <true|false>,
    "fairness_check": "<explanation>",
    "ethical_considerations": "<explanation>",
    "comparison_to_peers": {{
        "percentile": <0-100>,
        "ranking": "<top_performer|above_average|average|below_average>"
    }}
}}
"""
            
            from utils.llm_factory import create_llm
            from utils.llm_utils import invoke_llm_with_timeout

            llm = create_llm()
            response = await invoke_llm_with_timeout(llm, prompt, timeout=30.0)
            content = getattr(response, "content", str(response))

            review_result = json.loads(content)
            
            # Step 5: Format response
            response_data = {
                "user_id": str(user_id),
                "user_name": user.get("name"),
                "review_period": review_period,
                "rating": review_result.get("rating", 3.0),  # Default to 3.0 if not provided
                "summary": review_result.get("summary", review_result.get("justification", "")),  # Use justification as fallback
                "recommendation": review_result.get("recommendation"),
                "justification": review_result.get("justification"),
                "metrics": metrics,
                "strengths": review_result.get("strengths", []),
                "areas_for_improvement": review_result.get("areas_for_improvement", []),
                "growth_opportunities": review_result.get("growth_opportunities", []),
                "recognition_suggested": review_result.get("recognition_suggested", False),
                "fairness_check": review_result.get("fairness_check", ""),
                "ethical_considerations": review_result.get("ethical_considerations", ""),
                "comparison_to_peers": review_result.get("comparison_to_peers")
            }
            
            # Step 6: Log the decision
            decision_id = self.logger.log_performance_review(
                user_id=str(user_id),
                user_name=user.get("name"),
                review_period=review_period,
                recommendation=response_data["recommendation"],
                justification=response_data["justification"],
                metrics=metrics,
                fairness_check=response_data["fairness_check"],
                ethical_considerations=response_data["ethical_considerations"]
            )
            
            response_data["decision_id"] = decision_id
            
            logger.info(f"Performance review complete, logged as {decision_id}")
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating performance review: {e}", exc_info=True)
            raise


# Create singleton instance
decision_service = DecisionService()
