"""
Decision Logging Service - Implements audit trail and decision history
Use Case 5: Transparent Decision Logging
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class DecisionLogger:
    """
    Handles persistent logging of all AI decisions for audit and transparency
    
    In a production system, this would use a database (PostgreSQL, MongoDB, etc.)
    For now, we'll use JSON file storage for simplicity
    """
    
    def __init__(self, log_directory: str = "decision_logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        self.current_log_file = self.log_directory / f"decisions_{datetime.now().strftime('%Y%m')}.json"
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure the log file exists"""
        if not self.current_log_file.exists():
            self.current_log_file.write_text("[]")
    
    def _read_logs(self) -> List[Dict[str, Any]]:
        """Read all logs from current month's file"""
        try:
            return json.loads(self.current_log_file.read_text())
        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            return []
    
    def _write_logs(self, logs: List[Dict[str, Any]]):
        """Write logs to file"""
        try:
            self.current_log_file.write_text(json.dumps(logs, indent=2, default=str))
        except Exception as e:
            logger.error(f"Error writing logs: {e}")
    
    def log_task_assignment_decision(
        self,
        task_id: str,
        task_title: str,
        assigned_user_id: str,
        assigned_user_name: str,
        confidence: float,
        explanation: str,
        ethical_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        reasoning_trace: List[str],
        priority_factors: List[str],
        alternative_options: List[str],
        action_items: List[str]
    ) -> str:
        """
        Log a task assignment decision
        
        Returns:
            decision_id: Unique identifier for this decision
        """
        logs = self._read_logs()
        
        decision_id = f"DEC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(logs)+1}"
        
        decision_log = {
            "decision_id": decision_id,
            "decision_type": "task_assignment",
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task_id,
            "task_title": task_title,
            "assigned_user_id": assigned_user_id,
            "assigned_user_name": assigned_user_name,
            "confidence": confidence,
            "explanation": explanation,
            "ethical_analysis": ethical_analysis,
            "risk_assessment": risk_assessment,
            "performance_metrics": performance_metrics,
            "reasoning_trace": reasoning_trace,
            "priority_factors": priority_factors,
            "alternative_options": alternative_options,
            "action_items": action_items,
            "created_by": "AI_System",
            "version": "1.0"
        }
        
        logs.append(decision_log)
        self._write_logs(logs)
        
        logger.info(f"Logged decision: {decision_id}")
        return decision_id
    
    def log_conflict_resolution(
        self,
        conflict_type: str,
        project_id: str,
        resolution: Dict[str, Any],
        trade_offs: Dict[str, Any],
        ethical_justification: str,
        reasoning_trace: List[str]
    ) -> str:
        """
        Log a conflict resolution decision
        
        Returns:
            decision_id: Unique identifier for this decision
        """
        logs = self._read_logs()
        
        decision_id = f"DEC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(logs)+1}"
        
        decision_log = {
            "decision_id": decision_id,
            "decision_type": "conflict_resolution",
            "timestamp": datetime.utcnow().isoformat(),
            "conflict_type": conflict_type,
            "project_id": project_id,
            "resolution": resolution,
            "trade_offs": trade_offs,
            "ethical_justification": ethical_justification,
            "reasoning_trace": reasoning_trace,
            "created_by": "AI_System",
            "version": "1.0"
        }
        
        logs.append(decision_log)
        self._write_logs(logs)
        
        logger.info(f"Logged conflict resolution: {decision_id}")
        return decision_id
    
    def log_performance_review(
        self,
        user_id: str,
        user_name: str,
        review_period: str,
        recommendation: str,
        justification: str,
        metrics: Dict[str, Any],
        fairness_check: str,
        ethical_considerations: str
    ) -> str:
        """
        Log a performance review decision
        
        Returns:
            decision_id: Unique identifier for this decision
        """
        logs = self._read_logs()
        
        decision_id = f"DEC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(logs)+1}"
        
        decision_log = {
            "decision_id": decision_id,
            "decision_type": "performance_review",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "user_name": user_name,
            "review_period": review_period,
            "recommendation": recommendation,
            "justification": justification,
            "metrics": metrics,
            "fairness_check": fairness_check,
            "ethical_considerations": ethical_considerations,
            "created_by": "AI_System",
            "version": "1.0"
        }
        
        logs.append(decision_log)
        self._write_logs(logs)
        
        logger.info(f"Logged performance review: {decision_id}")
        return decision_id
    
    def get_decision_by_id(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific decision by ID"""
        logs = self._read_logs()
        for log in logs:
            if log.get("decision_id") == decision_id:
                return log
        return None
    
    def get_decisions_by_task(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all decisions related to a task"""
        logs = self._read_logs()
        return [log for log in logs if log.get("task_id") == str(task_id)]
    
    def get_decisions_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all decisions related to a user"""
        logs = self._read_logs()
        return [
            log for log in logs 
            if log.get("assigned_user_id") == str(user_id) or log.get("user_id") == str(user_id)
        ]
    
    def get_decisions_by_type(self, decision_type: str) -> List[Dict[str, Any]]:
        """Get all decisions of a specific type"""
        logs = self._read_logs()
        return [log for log in logs if log.get("decision_type") == decision_type]
    
    def get_all_decisions(
        self,
        limit: int = 100,
        offset: int = 0,
        decision_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all decisions with pagination
        
        Args:
            limit: Maximum number of decisions to return
            offset: Number of decisions to skip
            decision_type: Filter by decision type (optional)
            
        Returns:
            List of decision logs
        """
        logs = self._read_logs()
        
        # Filter by type if specified
        if decision_type:
            logs = [log for log in logs if log.get("decision_type") == decision_type]
        
        # Sort by timestamp (most recent first)
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply pagination
        return logs[offset:offset + limit]
    
    def get_audit_trail(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get audit trail for a date range
        
        Args:
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            List of decision logs within the date range
        """
        logs = self._read_logs()
        
        # Filter by date range
        filtered_logs = []
        for log in logs:
            timestamp = log.get("timestamp", "")
            if start_date <= timestamp <= end_date:
                filtered_logs.append(log)
        
        return filtered_logs
    
    def generate_decision_summary(self, decision_id: str) -> str:
        """
        Generate a human-readable summary of a decision for auditing
        
        Returns:
            Formatted text summary
        """
        decision = self.get_decision_by_id(decision_id)
        if not decision:
            return f"Decision {decision_id} not found"
        
        decision_type = decision.get("decision_type", "Unknown")
        timestamp = decision.get("timestamp", "Unknown")
        
        if decision_type == "task_assignment":
            summary = f"""
=== DECISION LOG ===
Decision ID: {decision_id}
Type: Task Assignment
Timestamp: {timestamp}
Created By: {decision.get('created_by', 'Unknown')}

DECISION:
Task: {decision.get('task_title', 'Unknown')} (ID: {decision.get('task_id', 'Unknown')})
Assigned To: {decision.get('assigned_user_name', 'Unknown')} (ID: {decision.get('assigned_user_id', 'Unknown')})
Confidence: {decision.get('confidence', 0):.2f}

REASONING:
{decision.get('explanation', 'No explanation provided')}

ETHICAL ANALYSIS:
Fairness Score: {decision.get('ethical_analysis', {}).get('fairness_score', 'N/A')}
Ethical Concerns: {', '.join(decision.get('ethical_analysis', {}).get('ethical_concerns', []))}

RISK ASSESSMENT:
Overall Risk Level: {decision.get('risk_assessment', {}).get('overall_risk_level', 'N/A')}

PRIORITY FACTORS:
{chr(10).join(f'- {factor}' for factor in decision.get('priority_factors', []))}

ACTION ITEMS:
{chr(10).join(f'- {item}' for item in decision.get('action_items', []))}

===================
"""
        elif decision_type == "conflict_resolution":
            resolution = decision.get("resolution", {})
            summary = f"""
=== DECISION LOG ===
Decision ID: {decision_id}
Type: Conflict Resolution
Timestamp: {timestamp}
Created By: {decision.get('created_by', 'Unknown')}

CONFLICT:
Type: {decision.get('conflict_type', 'Unknown')}
Project ID: {decision.get('project_id', 'Unknown')}

RESOLUTION:
Decision: {resolution.get('decision', 'Unknown')}
Timeline Adjustment: {resolution.get('timeline_adjustment', 'None')}
Scope Adjustment: {resolution.get('scope_adjustment', 'None')}

EXECUTIVE SUMMARY:
{resolution.get('executive_summary', 'No summary provided')}

ETHICAL JUSTIFICATION:
{decision.get('ethical_justification', 'No justification provided')}

STAKEHOLDER MESSAGING:
Team: {resolution.get('stakeholder_messaging', {}).get('team', 'N/A')}
Business: {resolution.get('stakeholder_messaging', {}).get('business', 'N/A')}
Customer: {resolution.get('stakeholder_messaging', {}).get('customer', 'N/A')}

===================
"""
        else:
            summary = f"""
=== DECISION LOG ===
Decision ID: {decision_id}
Type: {decision_type}
Timestamp: {timestamp}
Created By: {decision.get('created_by', 'Unknown')}

{json.dumps(decision, indent=2)}
===================
"""
        
        return summary


# Create singleton instance
decision_logger = DecisionLogger()
