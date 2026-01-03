"""
Data Agent - Collects data from NestJS backend APIs
"""
import httpx
from typing import Dict, List, Optional, Any
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class DataAgent:
    """Agent responsible for fetching and preprocessing data from backend APIs"""
    
    def __init__(self, backend_url: str = None):
        self.backend_url = backend_url or settings.nestjs_backend_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def fetch_tasks(self, task_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch tasks from the backend
        
        Args:
            task_id: Optional specific task ID to fetch
            
        Returns:
            List of task dictionaries
        """
        try:
            if task_id:
                url = f"{self.backend_url}/tasks/{task_id}"
                response = await self.client.get(url)
                response.raise_for_status()
                return [response.json()]
            else:
                url = f"{self.backend_url}/tasks"
                response = await self.client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
            return []
    
    async def fetch_users(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch users from the backend
        
        Args:
            user_id: Optional specific user ID to fetch
            
        Returns:
            List of user dictionaries
        """
        try:
            if user_id:
                url = f"{self.backend_url}/users/{user_id}"
                response = await self.client.get(url)
                response.raise_for_status()
                return [response.json()]
            else:
                url = f"{self.backend_url}/users"
                response = await self.client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
    
    async def fetch_teams(self, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch teams from the backend
        
        Args:
            team_id: Optional specific team ID to fetch
            
        Returns:
            List of team dictionaries
        """
        try:
            if team_id:
                url = f"{self.backend_url}/teams/{team_id}"
                response = await self.client.get(url)
                response.raise_for_status()
                return [response.json()]
            else:
                url = f"{self.backend_url}/teams"
                response = await self.client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching teams: {e}")
            return []
    
    async def fetch_projects(self, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch projects from the backend
        
        Args:
            project_id: Optional specific project ID to fetch
            
        Returns:
            List of project dictionaries
        """
        try:
            if project_id:
                url = f"{self.backend_url}/projects/{project_id}"
                response = await self.client.get(url)
                response.raise_for_status()
                return [response.json()]
            else:
                url = f"{self.backend_url}/projects"
                response = await self.client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return []
    
    async def fetch_project(self, project_id: int) -> Dict[str, Any]:
        """
        Fetch a specific project by ID (convenience method for single project)
        
        Args:
            project_id: Project ID
            
        Returns:
            Project dictionary
        """
        try:
            projects = await self.fetch_projects(project_id)
            return projects[0] if projects else {}
        except Exception as e:
            logger.error(f"Error fetching project {project_id}: {e}")
            return {}
    
    async def fetch_team(self, team_id: int) -> Dict[str, Any]:
        """
        Fetch a specific team by ID (convenience method for single team)
        
        Args:
            team_id: Team ID
            
        Returns:
            Team dictionary
        """
        try:
            teams = await self.fetch_teams(team_id)
            return teams[0] if teams else {}
        except Exception as e:
            logger.error(f"Error fetching team {team_id}: {e}")
            return {}
    
    async def fetch_user_workload(self, user_id: int) -> int:
        """
        Calculate user workload based on assigned tasks
        
        Args:
            user_id: User ID
            
        Returns:
            Total story points assigned to user
        """
        try:
            tasks = await self.fetch_tasks()
            user_tasks = [t for t in tasks if t.get('assignee_id') == user_id 
                         and t.get('status') != 'COMPLETED']
            
            workload = sum(t.get('story_points', 0) for t in user_tasks)
            return workload
        except Exception as e:
            logger.error(f"Error calculating user workload: {e}")
            return 0
    
    async def preprocess_task_data(self, task_id: int) -> Dict[str, Any]:
        """
        Fetch and preprocess task data for AI decision making
        
        Args:
            task_id: Task ID to process
            
        Returns:
            Dictionary with preprocessed task data
        """
        try:
            tasks = await self.fetch_tasks(task_id)
            if not tasks:
                raise ValueError(f"Task {task_id} not found")
            
            task = tasks[0]
            
            # Convert to format expected by agents
            processed_task = {
                "id": str(task.get('id')),
                "title": task.get('title'),
                "description": task.get('description'),
                "difficulty": task.get('difficulty', 'MEDIUM').lower(),
                "story_points": task.get('story_points', 0),
                "sprint": task.get('sprint'),
                "deadline": str(task.get('deadline')) if task.get('deadline') else None,
                "status": task.get('status'),
                "project_id": task.get('project_id'),
                "team_id": task.get('team_id'),  # Include team_id for team filtering
                "assigned_by": task.get('assigned_by'),
                "required_skills": task.get('required_skills', []),  # Include required_skills
            }
            
            return processed_task
        except Exception as e:
            logger.error(f"Error preprocessing task data: {e}")
            raise
    
    async def preprocess_user_data(self, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch and preprocess user data for AI decision making
        
        Args:
            project_id: Optional project ID to filter users
            
        Returns:
            List of preprocessed user dictionaries
        """
        try:
            users = await self.fetch_users()
            
            # Filter by project if specified
            if project_id:
                users = [u for u in users if u.get('project_id') == project_id]
            
            # Calculate workload and other feature metrics for each user
            # Fetch all tasks once to compute per-user aggregates
            all_tasks = await self.fetch_tasks()

            processed_users = []
            for user in users:
                user_id = user.get('id')
                # Active tasks assigned (not COMPLETED)
                user_tasks = [t for t in all_tasks if t.get('assignee_id') == user_id and t.get('status') != 'COMPLETED']
                completed_tasks = [t for t in all_tasks if t.get('assignee_id') == user_id and t.get('status') == 'COMPLETED']

                current_workload_count = len(user_tasks)
                # avg complexity: prefer explicit 'complexity' then 'story_points'
                complexities = [t.get('complexity', t.get('story_points', 5)) for t in user_tasks]
                avg_task_complexity = sum(complexities) / len(complexities) if complexities else 0.0

                # recent assignments in last N days (use created_at if available)
                recent_count = 0
                from datetime import datetime, timedelta
                cutoff = datetime.utcnow() - timedelta(days=14)
                for t in all_tasks:
                    if t.get('assignee_id') == user_id:
                        created = t.get('created_at') or t.get('created')
                        if created:
                            try:
                                dt = datetime.fromisoformat(created)
                                if dt >= cutoff:
                                    recent_count += 1
                            except Exception:
                                pass

                # completion confidence: completed / total assigned (fallback 0.8)
                total_assigned = len([t for t in all_tasks if t.get('assignee_id') == user_id])
                completion_confidence = (len(completed_tasks) / total_assigned) if total_assigned > 0 else 0.8

                processed_user = {
                    "id": str(user_id),
                    "name": user.get('name'),
                    "email": user.get('email'),
                    "role": user.get('role'),
                    "team_id": str(user.get('team_id')) if user.get('team_id') else None,
                    "project_id": str(user.get('project_id')) if user.get('project_id') else None,
                    "skills": user.get('skills', []),  # CRITICAL: Include skills for skill matching
                    "current_workload": current_workload_count,
                    "workload_story_points": await self.fetch_user_workload(user_id),
                    "availability": user.get('availability', True),
                    "joining_date": str(user.get('joining_date')) if user.get('joining_date') else None,
                    "experience_years": float(user.get('experience_years', 0)),
                    "recent_assignments_count": recent_count,
                    "avg_task_complexity": float(avg_task_complexity),
                    "completed_tasks_count": len(completed_tasks),
                    "total_assigned_count": total_assigned,
                    "estimated_completion_confidence": float(completion_confidence),
                }

                processed_users.append(processed_user)
            
            return processed_users
        except Exception as e:
            logger.error(f"Error preprocessing user data: {e}")
            raise
    
    async def preprocess_team_data(self) -> List[Dict[str, Any]]:
        """
        Fetch and preprocess team data for AI decision making
        
        Returns:
            List of preprocessed team dictionaries
        """
        try:
            teams = await self.fetch_teams()
            
            processed_teams = []
            for team in teams:
                processed_team = {
                    "team_id": str(team.get('id')),
                    "team_name": team.get('team_name'),
                    "team_type": "development",  # Can be enhanced based on team name/type
                    "manager_id": str(team.get('manager_id')) if team.get('manager_id') else None,
                }
                
                processed_teams.append(processed_team)
            
            return processed_teams
        except Exception as e:
            logger.error(f"Error preprocessing team data: {e}")
            raise
    
    async def collect_decision_context(self, task_id: int) -> Dict[str, Any]:
        """
        Collect all relevant context for making a decision about a task
        
        Args:
            task_id: Task ID to make decision for
            
        Returns:
            Dictionary with all context data (task, users, teams, projects)
        """
        try:
            task = await self.preprocess_task_data(task_id)

            # Get users from the same team (if task has team_id) or project
            team_id = task.get('team_id')
            project_id = task.get('project_id')
            
            # Filter by team if available, otherwise filter by project
            if team_id:
                # Filter users by team_id (convert to string since preprocess_user_data returns strings)
                all_project_users = await self.preprocess_user_data(project_id)
                team_id_str = str(team_id)
                users = [u for u in all_project_users if u.get('team_id') == team_id_str]
            else:
                # Fall back to project filtering
                users = await self.preprocess_user_data(project_id)

            # Build candidate features by combining task requirements and user metrics
            # Fetch all tasks to compute skill match and other dynamic fields
            all_tasks = await self.fetch_tasks()

            required_skills = task.get('required_skills') or []
            candidates = []
            for u in users:
                # compute skill match score (Jaccard over skill names)
                user_skills = u.get('skills') or []
                # normalize to lowercase
                set_req = set([s.lower() for s in required_skills]) if required_skills else set()
                set_usr = set([s.lower() for s in user_skills]) if user_skills else set()
                
                # DEBUG: Log skill matching for first user
                if u.get('id') == '202':  # Emily Rodriguez
                    logger.debug(f"DEBUG SKILL MATCH - User {u.get('name')} (ID: {u.get('id')})")
                    logger.debug(f"  Required skills: {required_skills}")
                    logger.debug(f"  User skills: {user_skills}")
                    logger.debug(f"  Set required: {set_req}")
                    logger.debug(f"  Set user: {set_usr}")
                    logger.debug(f"  Intersection: {set_req.intersection(set_usr) if set_req else 'N/A'}")
                    logger.debug(f"  Union: {set_req.union(set_usr) if set_req else 'N/A'}")
                
                if set_req:
                    intersection = set_req.intersection(set_usr)
                    union = set_req.union(set_usr)
                    skill_match = len(intersection) / len(union) if union else 0.0
                else:
                    # if no explicit required skills, use 0.5 neutral
                    skill_match = 0.5

                # fairness adjustment: inverse of recent_assignments_count (normalize)
                recent = u.get('recent_assignments_count', 0)
                fairness = 1.0 / (1 + recent)

                # wellbeing flag: overloaded if current_workload exceeds policy
                from config.settings import settings as cfg
                wellbeing_flag = True if u.get('current_workload', 0) >= cfg.max_allowed_workload else False

                # deadline urgency
                deadline_urgency = 0.0
                import datetime
                if task.get('deadline'):
                    try:
                        due = datetime.datetime.fromisoformat(task['deadline'])
                        now = datetime.datetime.utcnow()
                        delta = (due - now).total_seconds()
                        # map to 0-1 where 0 = plenty of time, 1 = urgent (<=0)
                        deadline_urgency = max(0.0, min(1.0, 1.0 - (delta / (7 * 24 * 3600))))
                    except Exception:
                        deadline_urgency = 0.0

                candidate = {
                    "id": u.get('id'),
                    "name": u.get('name'),
                    "availability": u.get('availability', True),
                    "current_workload": u.get('current_workload', 0),
                    "workload_story_points": u.get('workload_story_points', 0),
                    "experience_years": u.get('experience_years', 0),
                    "recent_assignments_count": u.get('recent_assignments_count', 0),
                    "avg_task_complexity": u.get('avg_task_complexity', 0.0),
                    "skill_match_score": round(float(skill_match), 3),
                    "estimated_completion_confidence": round(float(u.get('estimated_completion_confidence', 0.8)), 3),
                    "fairness_adjustment_score": round(float(fairness), 3),
                    "wellbeing_flag": wellbeing_flag,
                    "role": u.get('role'),
                    "deadline_urgency": round(float(deadline_urgency), 3)
                }

                candidates.append(candidate)

            teams = await self.preprocess_team_data()

            context = {
                "task": task,
                "candidates": candidates,
                "teams": teams,
                "raw_users": users
            }
            
            return context
        except Exception as e:
            logger.error(f"Error collecting decision context: {e}")
            raise


# Create a singleton instance
data_agent = DataAgent()
