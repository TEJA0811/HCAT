"""
FastAPI Application - AI Decision Making Backend
Provider-agnostic: uses configured LLM provider (Groq by default)
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from datetime import datetime
import httpx
import json

from config.settings import settings
from models.schemas import (
    TaskAssignmentRequest,
    DecisionResponse,
    PerformanceReviewRequest,
    PerformanceReviewResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    HealthResponse,
    ErrorResponse
)
from services.decision_logger import decision_logger
from utils.llm_utils import invoke_llm_with_timeout
from utils.llm_factory import create_llm
from agents.data_agent import data_agent
from config.settings import settings as cfg

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HCAT AI Decision Backend",
    description="AI-powered decision making system using configured LLM provider",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_llm():
    """Get configured LLM instance (provider configured via settings)"""
    return create_llm()


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(status="running", version="2.0.0")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test LLM connection (quick timeout)
        llm = get_llm()
        try:
            await invoke_llm_with_timeout(llm, "test", timeout=5.0)
        except TimeoutError:
            return HealthResponse(status="healthy (LLM not responding)", version="2.0.0")
        return HealthResponse(status="healthy", version="2.0.0")
    except:
        return HealthResponse(status="healthy (LLM not available)", version="2.0.0")


@app.post("/api/v1/decisions/task-assignment", response_model=DecisionResponse)
async def make_task_assignment_decision(request: TaskAssignmentRequest):
    """
    AI-powered task assignment using Ollama with compact feature payload
    """
    try:
        logger.info(f"🤖 AI Task Assignment for task_id: {request.task_id}")

        # Collect enriched decision context (task + candidate features)
        context = await data_agent.collect_decision_context(request.task_id)
        task = context.get('task')
        candidates = context.get('candidates', [])
        raw_users = context.get('raw_users', [])

        llm = get_llm()

        # Build compact payload
        payload = {
            "task": {
                "id": task.get('id'),
                "title": task.get('title'),
                "priority": task.get('priority'),
                "difficulty": task.get('difficulty'),
                "required_skills": task.get('required_skills') or [],
                "estimated_hours": task.get('story_points') or 0,
                "due_in_days": None
            },
            "candidates": candidates,
            "policy": {"max_allowed_workload": cfg.max_allowed_workload, "prefer_experience_when_difficulty_gt": cfg.prefer_experience_when_difficulty_gt}
        }

        prompt = (
            "You are an Ethical Task Assignment System. You MUST assign the task to exactly ONE candidate.\n"
            "Input JSON follows with `task`, `candidates`, and `policy`.\n"
            "CRITICAL: Return ONLY JSON wrapped between <<<JSON>>> and <<<END_JSON>>> with NO other text.\n\n"
            "===== HARD FILTER RULES (NON-NEGOTIABLE - APPLY FIRST) =====\n"
            "RULE 1: For HIGH difficulty tasks: DO NOT ASSIGN if skill_match < 0.6\n"
            "        If NO candidate has skill_match >= 0.6, assign to highest skill_match available AND EXPLAIN the skill gap\n\n"
            "RULE 2: For MEDIUM difficulty tasks: DO NOT ASSIGN if skill_match < 0.5\n"
            "        If NO candidate has skill_match >= 0.5, assign to highest skill_match available\n\n"
            "RULE 3: For LOW difficulty tasks: Minimum skill_match >= 0.3\n\n"
            "RULE 4: NEVER assign a candidate with skill_match = 0.0 without explicit mention that this is NOT ideal\n"
            "        If you assign skill_match = 0.0, the entire explanation must focus on why no one better was available\n\n"
            "===== PRIORITY HIERARCHY (MOST IMPORTANT - READ SECOND) =====\n"
            "1. For HIGH difficulty or CRITICAL priority tasks: EXPERTISE AND SKILL MATCH ARE ABSOLUTE PRIORITIES\n"
            "   → If a candidate has skill_match >= 0.6 AND experience >= 3.0, ASSIGN TO THEM FIRST\n"
            "   → Do NOT reject qualified experts just because workload is high\n"
            "   → High workload is acceptable if they are the most qualified person\n\n"
            "2. For MEDIUM difficulty tasks: Balance skill match (>= 0.5) with workload\n"
            "   → Prefer candidates with reasonable workload but don't sacrifice skill match\n\n"
            "3. For LOW difficulty tasks: Workload becomes more important\n"
            "   → Can prioritize lower workload candidates (skill_match >= 0.3)\n\n"
            "KEY RULE: A candidate with HIGH expertise and good skill match should ALWAYS beat a candidate with low workload but poor skills\n"
            "WORKLOAD IS SECONDARY TO EXPERTISE FOR COMPLEX TASKS\n\n"
            "=== MANDATORY ASSIGNMENT RULES (Follow EXACTLY in order) ===\n\n"
            "STEP 1 - FILTER AVAILABLE CANDIDATES:\n"
            "- EXCLUDE: availability==false (unavailable)\n"
            "- EXCLUDE: wellbeing_flag==true (overworked) UNLESS truly no other options\n"
            "- If ALL candidates excluded, choose the one with lowest current_workload and flag wellbeing risk\n\n"
            "STEP 2 - APPLY TASK-SPECIFIC FILTERING (CRITICALITY-BASED):\n"
            "IF task.difficulty == 'HIGH' or task.priority == 'CRITICAL':\n"
            "  - MUST HAVE: experience_years >= 3.0 (solid expertise required)\n"
            "  - MUST HAVE: skill_match_score >= 0.6 (skill match is HARD MINIMUM - DO NOT IGNORE)\n"
            "  - If no one meets these, pick highest skill_match and EXPLAIN the gap in detail\n"
            "  - For these tasks, EXPERTISE AND SKILL OVERRIDE workload concerns\n"
            "  - Apply 40% weight to experience, 35% to skill_match, 20% to confidence, ONLY 5% to workload\n\n"
            "ELSE IF task.difficulty == 'MEDIUM':\n"
            "  - MUST HAVE: experience_years >= 2.0\n"
            "  - MUST HAVE: skill_match_score >= 0.5 (hard minimum)\n"
            "  - Apply 35% weight to skill_match, 25% to experience, 30% to confidence, 10% to workload\n\n"
            "ELSE (task.difficulty == 'LOW'):\n"
            "  - ACCEPT: experience_years >= 1.0\n"
            "  - ACCEPT: skill_match_score >= 0.3 (minimum 0.3)\n"
            "  - Apply 25% weight to skill_match, 20% to experience, 30% to confidence, 25% to workload\n\n"
            "STEP 3 - CALCULATE SCORE FOR EACH REMAINING CANDIDATE:\n"
            "Apply weights based on task difficulty (from STEP 2 above):\n\n"
            "FOR HIGH/CRITICAL DIFFICULTY:\n"
            "  Score = (skill_match * 0.35) + (experience/5 * 0.40) + (confidence * 0.20) + (1 - workload_ratio * 0.05)\n"
            "  → Skill and experience get 75% of weight, workload only 5%\n"
            "  → IMPORTANT: Do NOT heavily penalize high workload for qualified candidates\n"
            "  → A candidate with skill_match=0.8 and high workload scores higher than skill_match=0.4 with low workload\n\n"
            "FOR MEDIUM DIFFICULTY:\n"
            "  Score = (skill_match * 0.35) + (experience/5 * 0.25) + (confidence * 0.30) + (1 - workload_ratio * 0.10)\n"
            "  → Skill/experience/confidence weighted 90%, workload 10%\n\n"
            "FOR LOW DIFFICULTY:\n"
            "  Score = (skill_match * 0.25) + (experience/5 * 0.20) + (confidence * 0.30) + (1 - workload_ratio * 0.25)\n"
            "  → Workload gets more weight (25%) but skill still matters\n\n"
            "CRITICAL RULE: Never apply large penalties for workload on HIGH/CRITICAL tasks if skill_match >= 0.6\n"
            "→ A highly skilled person with full workload is BETTER than an unskilled person with empty workload\n\n"
            "STEP 4 - SELECT WINNER:\n"
            "- Choose candidate with HIGHEST score (expertise-weighted for HIGH tasks)\n"
            "- If tied in skill_match (within 0.05) on HIGH difficulty: Choose the more experienced one\n"
            "- If tied on experience: Choose lower workload\n"
            "- For HIGH/CRITICAL: Prefer skilled person with high workload over unskilled person with low workload\n"
            "- NEVER return null/empty chosen_user_id\n"
            "- ALWAYS assign based on QUALIFICATION FIRST, workload second\n\n"
            "STEP 5 - SMART REASSIGNMENT LOGIC (For complex HIGH difficulty tasks):\n"
            "- IF task.difficulty == 'HIGH' AND best_available_candidate has skill_match >= 0.6:\n"
            "  If their workload is very high, STILL ASSIGN TO THEM (expertise > workload)\n"
            "  But check if an overloaded expert (experience >= 3.0, skill_match >= 0.8) exists\n"
            "  If YES and they have LOW priority tasks: Suggest reassigning 1-2 of their lowest priority tasks\n"
            "  This allows the expert to focus on the critical task\n"
            "  Include in reassignment_suggestions the low-priority task ID and target person\n\n"
            "STEP 6 - PROVIDE DETAILED TRANSPARENT EXPLANATION (CRITICAL):\n"
            "Explain the decision based on TASK CRITICALITY AND REQUIRED EXPERTISE:\n"
            "1. WHO was selected and WHY based on task difficulty requirements and expertise level\n"
            "2. WHAT their skill match means (e.g., '3 out of 4 required skills: Frontend, React, Performance')\n"
            "3. WHY this person over alternatives (emphasize expertise/skill match for CRITICAL/HIGH tasks)\n"
            "4. TRADE-OFFS made (e.g., 'For this CRITICAL task, expertise overrides workload balance')\n"
            "5. RISK FACTORS if any (workload justified by expertise level for critical tasks)\n"
            "6. WORKLOAD IMPACT and mitigation strategy if applicable\n"
            "7. ALTERNATIVE APPROACHES (why expertise makes them the necessary choice)\n\n"
            "For CRITICAL/HIGH difficulty tasks: Explain why expertise and skill match trump workload concerns\n"
            "The rationale field should be 3-5 sentences minimum. The detailed_reasoning field should be formatted as BULLET POINTS (• symbol) with 5-8 points covering all aspects above.\n\n"
            "=== ETHICAL CHECKS (Required) ===\n"
            "- wellbeing_risks: List if chosen candidate has current_workload >= 3, or write 'None'\n"
            "- bias_checks: Confirm decision based only on metrics, write 'Decision based on objective metrics: skill_match, experience, confidence, workload'\n\n"
            "=== OUTPUT SCHEMA (MANDATORY) ===\n"
            "{\n"
            "  \"chosen_user_id\": <int REQUIRED, NEVER null>,\n"
            "  \"confidence\": <0.0-1.0, winner's calculated score>,\n"
            "  \"rationale\": \"DETAILED 3-5 sentence explanation covering: WHO selected, WHAT their skill match means (list matching skills), WHY chosen over alternatives, TRADE-OFFS made, and RISK factors.\",\n"
            "  \"detailed_reasoning\": \"Formatted as bullet points (use • symbol). Include 5-8 points:\\n• Selection Rationale: Why this person is the best fit despite any skill gaps\\n• Skill Match Details: List specific matching skills (e.g., '3 out of 4: Frontend, React, Performance')\\n• Comparison with Alternatives: Why top 2 alternatives weren't chosen\\n• Trade-offs Made: What was prioritized and what was compromised\\n• Risk Factors: Concerns and mitigation strategies\\n• Workload Impact: Effect on chosen person and team balance\\n• Recommendations: Suggested support (mentoring, pair programming, etc.)\",\n"
            "  \"alternatives\": [{\"user_id\":<int>,\"score\":<0-1>,\"reason\":\"Detailed explanation why NOT chosen despite strengths\"}],\n"
            "  \"reassignment_suggestions\": [],\n"
            "  \"ethical_checks\": {\"wellbeing_risks\":[\"specific concerns or 'None'\"],\"bias_checks\":[\"Decision based on objective metrics\"]}\n"
            "}\n\n"
            f"INPUT_JSON:\n{json.dumps(payload)}\n\n"
            "Remember: You MUST choose exactly ONE candidate. NEVER return null."
        )

        try:
            logger.debug("LLM payload (truncated): %s", json.dumps(payload)[:2000])
            logger.debug("LLM prompt (truncated): %s", prompt[:2000])
            response = await invoke_llm_with_timeout(llm, prompt, timeout=cfg.llm_timeout)
            # Normalize response content from different LLM wrappers
            raw = None
            if hasattr(response, 'content'):
                raw = response.content
            elif hasattr(response, 'text'):
                raw = response.text
            else:
                raw = response

            if isinstance(raw, bytes):
                try:
                    raw = raw.decode('utf-8')
                except Exception:
                    raw = raw.decode(errors='ignore')

            if raw is None:
                logger.error("LLM returned no content")
                raise HTTPException(status_code=502, detail="LLM returned empty response")

            raw_str = raw if isinstance(raw, str) else str(raw)

            # Strip explicit markers the prompt asks for, if present
            raw_str = raw_str.replace('<<<JSON>>>', '').replace('<<<END_JSON>>>', '').strip()

            # Try direct JSON parse
            try:
                ai_decision = json.loads(raw_str)
            except json.JSONDecodeError:
                # Attempt to extract first JSON object/array substring
                import re
                m = re.search(r"(\{.*\}|\[.*\])", raw_str, re.DOTALL)
                if m:
                    try:
                        ai_decision = json.loads(m.group(1))
                    except json.JSONDecodeError:
                        logger.error("Failed to parse JSON substring from LLM response")
                        logger.debug("LLM raw output: %s", raw_str[:1000])
                        raise HTTPException(status_code=502, detail="LLM returned invalid JSON")
                else:
                    logger.error("LLM returned non-JSON: %s", raw_str[:500])
                    raise HTTPException(status_code=502, detail="LLM returned non-JSON output")

            decision_source = 'LLM'
            logger.info("AI raw decision parsed: %s", json.dumps(ai_decision)[:200])

            # If model returned no chosen_user_id, retry once with a short clarifying prompt
            chosen_id_temp = ai_decision.get('chosen_user_id') or ai_decision.get('recommended_user_id')
            if chosen_id_temp in (None, '', 0):
                try:
                    logger.info("AI returned no chosen_user_id — retrying LLM once with clarifying prompt")
                    retry_prompt = (
                        "You previously returned an empty choice. Re-evaluate the INPUT_JSON below and RETURN ONLY the same JSON schema,\n"
                        "choosing the best available candidate (do NOT return null).\nINPUT_JSON:\n" + json.dumps(payload)
                    )
                    retry_resp = await invoke_llm_with_timeout(llm, retry_prompt, timeout=max(30.0, cfg.llm_timeout / 3))
                    retry_raw = getattr(retry_resp, 'content', getattr(retry_resp, 'text', str(retry_resp)))
                    if isinstance(retry_raw, bytes):
                        retry_raw = retry_raw.decode('utf-8', errors='ignore')
                    retry_raw = retry_raw.replace('<<<JSON>>>', '').replace('<<<END_JSON>>>', '').strip()
                    try:
                        retry_decision = json.loads(retry_raw)
                        if retry_decision.get('chosen_user_id') not in (None, '', 0):
                            ai_decision = retry_decision
                            decision_source = 'LLM-retry'
                            logger.info("Retry succeeded, parsed decision: %s", json.dumps(ai_decision)[:200])
                    except Exception:
                        logger.debug("Retry parsing failed. Raw retry output: %s", retry_raw[:500])
                except TimeoutError:
                    logger.warning("Retry LLM invocation timed out")
        except TimeoutError as e:
            logger.warning("LLM timeout, using deterministic fallback: %s", e)
            # deterministic fallback scoring
            scores = []
            weights = cfg.assignment_weights
            for c in candidates:
                # normalize fields
                skill = c.get('skill_match_score', 0)
                exp = min(c.get('experience_years', 0) / 10.0, 1.0)
                conf = c.get('estimated_completion_confidence', 0.8)
                workload_norm = 1.0 / (1.0 + c.get('current_workload', 0))
                fairness = c.get('fairness_adjustment_score', 0)
                deadline_pen = c.get('deadline_urgency', 0)

                score = (
                    weights.get('skill_match', 0.35) * skill +
                    weights.get('experience', 0.25) * exp +
                    weights.get('completion_confidence', 0.2) * conf +
                    weights.get('workload', 0.1) * workload_norm +
                    weights.get('fairness', 0.1) * fairness -
                    weights.get('deadline_penalty', 0.15) * deadline_pen
                )
                scores.append((c, score))

            scores.sort(key=lambda x: x[1], reverse=True)
            top = scores[0][0] if scores else None
            alternatives = [{"user_id": int(c.get('id')), "score": float(s), "reason": "fallback score"} for c, s in scores[:3]]
            ai_decision = {
                "chosen_user_id": int(top.get('id')) if top else None,
                "confidence": round(float(scores[0][1]) if scores else 0.0, 3),
                "rationale": "Deterministic fallback used due to LLM timeout; scored by features.",
                "alternatives": alternatives,
                "reassignment_suggestions": [],
                "ethical_checks": {"wellbeing_risks": [], "bias_checks": []}
            }
            decision_source = 'fallback'

        # Map AI decision to response model
        chosen_id = ai_decision.get('chosen_user_id') or ai_decision.get('recommended_user_id')
        confidence = ai_decision.get('confidence') or ai_decision.get('confidence_score')
        rationale = ai_decision.get('rationale') or ai_decision.get('reasoning')
        alternatives = ai_decision.get('alternatives', [])

        # VALIDATION: Check if chosen candidate meets minimum skill thresholds
        if chosen_id:
            chosen_candidate = next((c for c in candidates if int(c.get('id')) == int(chosen_id)), None)
            task_difficulty = task.get('difficulty', 'LOW')
            
            if chosen_candidate:
                skill_match = chosen_candidate.get('skill_match_score', 0.0)
                
                # For HIGH difficulty: Must be >= 0.6, if not re-score
                if task_difficulty == 'HIGH' and skill_match < 0.6 and skill_match < 0.1:
                    logger.warning(f"VALIDATION FAIL: Candidate {chosen_id} assigned for HIGH task but skill_match={skill_match}. Re-scoring...")
                    # Force re-score to find better candidate
                    fallback_scores = []
                    for c in candidates:
                        skill = c.get('skill_match_score', 0.0)
                        if c.get('availability', True):  # Only consider available candidates
                            exp = min(c.get('experience_years', 0) / 5.0, 1.0)
                            conf = c.get('estimated_completion_confidence', 0.7)
                            # For HIGH tasks, heavily weight skill_match
                            score = (skill * 0.50) + (exp * 0.30) + (conf * 0.20)
                            fallback_scores.append((c, score))
                    
                    fallback_scores.sort(key=lambda x: x[1], reverse=True)
                    if fallback_scores and fallback_scores[0][1] > 0:
                        new_winner = fallback_scores[0][0]
                        chosen_id = int(new_winner.get('id'))
                        confidence = round(fallback_scores[0][1], 2)
                        rationale = f"Reassigned (skill validation): Selected {new_winner.get('name')} with skill_match={new_winner.get('skill_match_score', 0):.2f}. Original assignment had insufficient skill match."
                        logger.info(f"Validation override: Reassigned to user {chosen_id}")

        # MANDATORY FALLBACK: If still no assignment, use deterministic scoring
        if not chosen_id or chosen_id in (None, '', 0):
            logger.warning("No candidate chosen by LLM, applying mandatory fallback scoring")
            # Score all candidates using deterministic formula
            fallback_scores = []
            for c in candidates:
                skill = c.get('skill_match_score', 0.5)
                exp = min(c.get('experience_years', 0) / 5.0, 1.0)
                conf = c.get('estimated_completion_confidence', 0.7)
                fairness = c.get('fairness_adjustment_score', 1.0)
                workload_penalty = 0.15 if c.get('current_workload', 0) >= cfg.max_allowed_workload else 0.0
                
                # Calculate score
                score = (skill * 0.35) + (exp * 0.25) + (conf * 0.30) + (fairness * 0.10) - workload_penalty
                fallback_scores.append((c, score))
            
            fallback_scores.sort(key=lambda x: x[1], reverse=True)
            if fallback_scores:
                winner = fallback_scores[0][0]
                chosen_id = int(winner.get('id'))
                confidence = round(fallback_scores[0][1], 2)
                rationale = f"Mandatory assignment: Selected {winner.get('name')} (ID: {chosen_id}) with score {confidence:.2f}. Factors: skill_match={winner.get('skill_match_score', 0):.2f}, experience={winner.get('experience_years', 0)}yrs, confidence={winner.get('estimated_completion_confidence', 0):.2f}, workload={winner.get('current_workload', 0)}."
                decision_source = 'mandatory-fallback'
                logger.info(f"Mandatory fallback assigned task to user {chosen_id}")

        recommended_user = next((u for u in raw_users if int(u['id']) == int(chosen_id)), None) if chosen_id else None

        # Log decision for transparency (Use Case 5: Decision Logging)
        try:
            decision_id = decision_logger.log_task_assignment_decision(
                task_id=str(request.task_id),
                task_title=task.get('title', ''),
                assigned_user_id=str(chosen_id) if chosen_id else '',
                assigned_user_name=recommended_user['name'] if recommended_user else 'Unknown',
                confidence=float(confidence) if confidence is not None else 0.0,
                explanation=rationale or '',
                ethical_analysis=ai_decision.get('ethical_checks', ai_decision.get('ethical_analysis', {})),
                risk_assessment=ai_decision.get('risk_assessment', {}),
                performance_metrics=ai_decision.get('performance_metrics', {}),
                reasoning_trace=ai_decision.get('reasoning_trace', []) if isinstance(ai_decision.get('reasoning_trace', []), list) else [ai_decision.get('reasoning_trace', '')],
                priority_factors={
                    'task_priority': task.get('priority', 'Medium'),
                    'task_difficulty': task.get('difficulty', 'Medium'),
                    'required_skills': task.get('required_skills', []),
                    'decision_source': decision_source
                },
                alternative_options=alternatives if isinstance(alternatives, list) else [],
                action_items=ai_decision.get('reassignment_suggestions', [])
            )
            logger.info(f"Decision logged with ID: {decision_id}")
        except Exception as log_error:
            logger.error(f"Failed to log decision: {log_error}")

        return DecisionResponse(
            task_id=str(request.task_id),
            task_title=task.get('title') if task else "",
            assigned_user_id=str(chosen_id) if chosen_id else "",
            assigned_user_name=recommended_user['name'] if recommended_user else None,
            confidence=float(confidence) if confidence is not None else 0.0,
            explanation=rationale or "",
            detailed_reasoning=ai_decision.get('detailed_reasoning', ""),  # Include detailed reasoning
            ethical_analysis=ai_decision.get('ethical_checks', ai_decision.get('ethical_analysis', {})),
            risk_assessment=ai_decision.get('risk_assessment', {}),
            performance_metrics=ai_decision.get('performance_metrics', {}),
            reasoning_trace=ai_decision.get('reasoning_trace', []) if isinstance(ai_decision.get('reasoning_trace', []), list) else [ai_decision.get('reasoning_trace', '')],
            reassignment_suggestions=ai_decision.get('reassignment_suggestions', []),
            timestamp=datetime.utcnow()
        )

    except json.JSONDecodeError as e:
        logger.error(f"AI returned invalid JSON: {e}")
        raise HTTPException(status_code=500, detail="AI response parsing failed")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/v1/decisions/performance-review", response_model=PerformanceReviewResponse)
async def get_performance_review(request: PerformanceReviewRequest):
    """
    AI-powered performance review - supports both individual and team-wide reviews
    """
    try:
        # Fetch data
        async with httpx.AsyncClient() as client:
            users_response = await client.get(f"{settings.nestjs_backend_url}/users")
            tasks_response = await client.get(f"{settings.nestjs_backend_url}/tasks")
            users = users_response.json()
            tasks = tasks_response.json()
        
        # Determine if it's a team review or individual review
        if request.team_id:
            # TEAM-WIDE PERFORMANCE REVIEW
            logger.info(f"🤖 AI Team Performance Review for team_id: {request.team_id}")
            
            # Get team members
            team_members = [u for u in users if u.get('team_id') == request.team_id]
            if not team_members:
                raise ValueError(f"No team members found for team_id {request.team_id}")
            
            # Calculate detailed metrics for each team member
            member_performance = []
            for member in team_members:
                member_tasks = [t for t in tasks if t.get('assignee_id') == member['id']]
                completed_tasks = [t for t in member_tasks if t['status'] in ['DONE', 'COMPLETED']]
                in_progress = [t for t in member_tasks if t['status'] == 'IN_PROGRESS']
                completion_rate = len(completed_tasks) / len(member_tasks) if member_tasks else 0
                
                # Calculate quality metrics
                avg_quality = sum(t.get('quality_score', 85) for t in completed_tasks) / len(completed_tasks) if completed_tasks else 0
                total_story_points = sum(t.get('story_points', 3) for t in completed_tasks)
                avg_task_difficulty = sum(1 if t.get('difficulty') == 'LOW' else 2 if t.get('difficulty') == 'MEDIUM' else 3 for t in completed_tasks) / len(completed_tasks) if completed_tasks else 0
                
                # Get completed task titles for context
                completed_task_titles = [t.get('title', 'Unknown') for t in completed_tasks[:3]]  # Top 3 for brevity
                
                member_performance.append({
                    'id': member['id'],
                    'name': member['name'],
                    'role': member.get('role', 'Developer'),
                    'total_tasks': len(member_tasks),
                    'completed_tasks': len(completed_tasks),
                    'in_progress_tasks': len(in_progress),
                    'completion_rate': completion_rate,
                    'avg_quality_score': avg_quality,
                    'total_story_points': total_story_points,
                    'avg_difficulty': avg_task_difficulty,
                    'completed_task_titles': completed_task_titles,
                    'workload': member.get('workload', 0),
                    'skills': member.get('skills', [])
                })
            
            # Filter out members with 0 tasks for ranking (but keep them in the report)
            rankable_members = [m for m in member_performance if m['total_tasks'] > 0]
            
            # Create team-wide AI prompt
            llm = get_llm()
            
            # Detailed team summary with quality metrics
            team_summary = "\n".join([
                f"- {m['name']} ({m['role']}): {m['completed_tasks']}/{m['total_tasks']} tasks ({m['completion_rate']*100:.1f}%), "
                f"Quality: {m['avg_quality_score']:.1f}/100, Story Points: {m['total_story_points']}, "
                f"Avg Difficulty: {m['avg_difficulty']:.1f}/3.0"
                + (f", Recent work: {', '.join(m['completed_task_titles'][:2])}" if m['completed_task_titles'] else "")
                for m in member_performance
            ])
            
            prompt = f"""You are an AI Performance Review Manager conducting a comprehensive TEAM performance evaluation. Your goal is to provide actionable insights, recognize top performers, and guide management decisions.

TEAM ID: {request.team_id}
REVIEW PERIOD: {request.review_period}
TEAM SIZE: {len(team_members)} members
MEMBERS WITH ASSIGNED TASKS: {len(rankable_members)} members

DETAILED PERFORMANCE DATA:
{team_summary}

EVALUATION CRITERIA:
1. Completion Rate (tasks completed / total tasks assigned)
2. Quality Score (average quality across completed tasks, 0-100 scale)
3. Story Points Delivered (total complexity delivered)
4. Task Difficulty (average complexity of completed work, 1-3 scale)
5. Consistency (all completed tasks vs. some completed)

CRITICAL INSTRUCTIONS FOR TOP PERFORMERS:
- ONLY rank members who have completed at least 1 task
- DO NOT include members with 0/0 tasks or 0 completed tasks in top performers
- If a member has 0 total tasks, mention them separately as "Not evaluated - no tasks assigned this period"
- Use actual data from the performance metrics above
- Be specific with numbers and percentages

YOUR TASK:
Provide a structured performance review with clear bullet points and data-driven insights.

RETURN ONLY valid JSON (no other text):
{{
    "rating": <1.0_to_5.0_team_average>,
    "summary": "📊 Executive Summary: [2-3 sentences highlighting team's overall performance, mentioning top performer by name with their completion rate]",
    "recommendation": "<team_recognition|continue_momentum|needs_improvement>",
    "justification": "🔍 Performance Analysis:\\n\\n• TEAM OVERVIEW: [1 sentence about team's collective performance with average completion rate]\\n\\n• TOP PERFORMERS:\\n  - [Name]: Completed [X/Y] tasks ([Z]% completion), Quality: [score]/100, Delivered [N] story points. [1 sentence about their excellence]\\n  - [Name]: Completed [X/Y] tasks ([Z]% completion), Quality: [score]/100, Delivered [N] story points. [1 sentence about their contribution]\\n  - [Name]: Completed [X/Y] tasks ([Z]% completion), Quality: [score]/100, Delivered [N] story points. [1 sentence about their strengths]\\n\\n• IMPROVEMENT NEEDED: [1-2 sentences about team members who need support, with specific data]\\n\\n• RECOMMENDATIONS: [2 sentences about concrete actions for management]",
    "strengths": [
        "✅ [Specific strength with data, e.g., 'High completion rate: 3 team members achieved 80%+ completion']",
        "✅ [Another strength, e.g., 'Quality excellence: Average quality score of 92/100 across completed tasks']",
        "✅ [Third strength with example, e.g., 'Complexity handling: Team delivered 45 story points in high-difficulty tasks']"
    ],
    "areas_for_improvement": [
        "⚠️ [Specific area with data, e.g., 'Task completion variance: 2 members below 50% completion need support']",
        "⚠️ [Another area, e.g., 'Workload distribution: Consider reassigning blocked tasks to available members']"
    ],
    "growth_opportunities": [
        "🚀 [Opportunity, e.g., 'Mentorship program: Pair top performers with members needing guidance']",
        "🚀 [Another opportunity, e.g., 'Skill development: Focus on [specific skill] training for improved task completion']"
    ],
    "top_performers": [
        {{
            "name": "[ACTUAL team member name with >0 completed tasks]",
            "achievement": "Completed [X/Y] tasks ([completion]% rate), Quality: [score]/100, [N] story points delivered. [Specific accomplishment from their completed work]"
        }},
        {{
            "name": "[2nd performer with >0 completed tasks]",
            "achievement": "Completed [X/Y] tasks ([completion]% rate), Quality: [score]/100, [N] story points. [Why they're #2]"
        }},
        {{
            "name": "[3rd performer with >0 completed tasks]",
            "achievement": "Completed [X/Y] tasks ([completion]% rate), Quality: [score]/100, [N] story points. [Their key contribution]"
        }}
    ],
    "recognition_suggested": true,
    "recognition_details": "🏆 Recognition Recommendations:\\n• [Top performer name]: Recommend [specific recognition - bonus/promotion/award] for [specific achievement with percentage/number]\\n• [2nd performer name]: Acknowledge [specific contribution] in team meeting\\n• [3rd performer name]: Consider for [opportunity] based on [specific strength]",
    "fairness_check": "Evaluation based on objective metrics: completion rate, quality scores, story points, and task difficulty. All members evaluated using same criteria.",
    "ethical_considerations": "Balanced quantitative metrics (completion rates, quality scores) with qualitative factors (task complexity, blocked tasks). Members with no assigned tasks marked as 'not evaluated' rather than poor performers."
}}

REMEMBER: 
- DO NOT list members with 0 completed tasks as top performers
- Use EXACT data from the performance metrics provided
- Format justification with clear bullet points using \\n for line breaks
- Include specific numbers (percentages, scores, story points) in all descriptions"""
            
            try:
                response = await invoke_llm_with_timeout(llm, prompt)
                
                # Extract JSON from response
                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    content = content[start_idx:end_idx+1]
                
                logger.debug(f"Extracted JSON content: {content[:200]}...")
                ai_review = json.loads(content)
            except TimeoutError as e:
                logger.error("LLM timeout: %s", e)
                raise HTTPException(status_code=504, detail="LLM invocation timed out")
            
            # Log decision for transparency
            try:
                await decision_logger.log_decision(
                    decision_type="TEAM_PERFORMANCE_REVIEW",
                    decision_maker="AI System",
                    decision=f"Team {request.team_id} performance: {ai_review['recommendation']}",
                    reasoning=ai_review['justification'],
                    ethical_considerations=[ai_review['fairness_check'], ai_review['ethical_considerations']],
                    alternatives_considered=[],
                    confidence_score=ai_review['rating'] / 5.0,
                    metadata={
                        "team_id": request.team_id,
                        "team_size": len(team_members),
                        "review_period": request.review_period,
                        "top_performers": ai_review.get('top_performers', [])
                    }
                )
                logger.info(f"Team performance review logged")
            except Exception as log_error:
                logger.error(f"Failed to log performance review: {log_error}")
            
            # Return team-wide performance review
            return PerformanceReviewResponse(
                user_id="TEAM",
                user_name=f"Team {request.team_id} ({len(team_members)} members)",
                review_period=request.review_period,
                rating=ai_review['rating'],
                summary=ai_review['summary'],
                recommendation=ai_review['recommendation'],
                justification=ai_review['justification'],
                metrics={
                    "team_size": len(team_members),
                    "total_tasks": sum(m['total_tasks'] for m in member_performance),
                    "completed_tasks": sum(m['completed_tasks'] for m in member_performance),
                    "avg_completion_rate": sum(m['completion_rate'] for m in member_performance) / len(member_performance) if member_performance else 0,
                    "top_performers": ai_review.get('top_performers', [])
                },
                strengths=ai_review.get('strengths', []),
                areas_for_improvement=ai_review.get('areas_for_improvement', []),
                growth_opportunities=ai_review.get('growth_opportunities', []),
                recognition_suggested=ai_review.get('recognition_suggested', False),
                fairness_check=ai_review['fairness_check'],
                ethical_considerations=ai_review['ethical_considerations'],
                comparison_to_peers={"recognition_details": ai_review.get('recognition_details', 'N/A')},
                timestamp=datetime.utcnow()
            )
        
        else:
            # INDIVIDUAL USER REVIEW (original logic)
            logger.info(f"🤖 AI Performance Review for user_id: {request.user_id}")
            
            # Find user
            user = next((u for u in users if u['id'] == request.user_id), None)
            if not user:
                raise ValueError(f"User {request.user_id} not found")
            
            # Calculate metrics
            user_tasks = [t for t in tasks if t.get('assignee_id') == request.user_id]
            completed_tasks = [t for t in user_tasks if t['status'] == 'DONE']
            in_progress = [t for t in user_tasks if t['status'] == 'IN_PROGRESS']
            completion_rate = len(completed_tasks) / len(user_tasks) if user_tasks else 0
            
            # Create AI prompt
            llm = get_llm()
            prompt = f"""You are an AI performance review system. Analyze this employee's performance.

EMPLOYEE:
Name: {user['name']}
Role: {user.get('role', 'Developer')}
Experience: {user.get('experience_years', 1)} years
Skills: {', '.join(user.get('skills', ['General']))}
Review Period: {request.review_period}

PERFORMANCE METRICS:
- Total tasks assigned: {len(user_tasks)}
- Tasks completed: {len(completed_tasks)}
- Tasks in progress: {len(in_progress)}
- Completion rate: {completion_rate * 100:.1f}%
- Current workload: {user.get('workload', 0)} tasks

PROVIDE COMPREHENSIVE REVIEW:
1. Overall rating (1.0 to 5.0 based on performance)
2. Brief summary (2-3 sentences)
3. Detailed justification (3-4 sentences)
4. Strengths (3-5 specific points)
5. Areas for improvement (2-3 points)
6. Growth opportunities (2-3 points)
7. Whether recognition is suggested (based on performance)
8. How you ensured unbiased evaluation

RETURN ONLY valid JSON (no other text):
{{
    "rating": <1.0_to_5.0>,
    "summary": "<2-3 sentence summary>",
    "recommendation": "<recognition|continue|improvement_needed>",
    "justification": "<detailed 3-4 sentence explanation>",
    "strengths": ["<strength1>", "<strength2>", "<strength3>"],
    "areas_for_improvement": ["<area1>", "<area2>"],
    "growth_opportunities": ["<opportunity1>", "<opportunity2>"],
    "recognition_suggested": <true_or_false>,
    "fairness_check": "<how you ensured unbiased evaluation>",
    "ethical_considerations": "<objectivity and fairness measures>"
}}"""
            
            try:
                response = await invoke_llm_with_timeout(llm, prompt)
                
                # Extract JSON from response (handle cases where LLM adds text around JSON)
                content = response.content.strip()
                
                # Try to find JSON block markers
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Remove any leading/trailing text before first { and after last }
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    content = content[start_idx:end_idx+1]
                
                logger.debug(f"Extracted JSON content: {content[:200]}...")
                ai_review = json.loads(content)
            except TimeoutError as e:
                logger.error("LLM timeout: %s", e)
                raise HTTPException(status_code=504, detail="LLM invocation timed out")
            
            # Log decision for transparency (Use Case 5: Decision Logging)
            try:
                decision_id = decision_logger.log_performance_review(
                    user_id=str(request.user_id),
                    user_name=user["name"],
                    review_period=request.review_period,
                    rating=ai_review['rating'],
                    summary=ai_review['summary'],
                    recommendation=ai_review['recommendation'],
                    justification=ai_review['justification'],
                    metrics={
                        "completion_rate": completion_rate,
                        "total_tasks": len(user_tasks),
                        "completed_tasks": len(completed_tasks),
                        "in_progress_tasks": len(in_progress)
                    },
                    fairness_check=ai_review['fairness_check'],
                    ethical_considerations=ai_review['ethical_considerations']
                )
                logger.info(f"Performance review logged with ID: {decision_id}")
            except Exception as log_error:
                logger.error(f"Failed to log performance review: {log_error}")
            
            return PerformanceReviewResponse(
                user_id=str(request.user_id),
                user_name=user["name"],
                review_period=request.review_period,
                rating=ai_review['rating'],
                summary=ai_review['summary'],
                recommendation=ai_review['recommendation'],
                justification=ai_review['justification'],
                metrics={
                    "completion_rate": completion_rate,
                    "total_tasks": len(user_tasks),
                    "completed_tasks": len(completed_tasks),
                    "in_progress_tasks": len(in_progress)
                },
                strengths=ai_review['strengths'],
                areas_for_improvement=ai_review['areas_for_improvement'],
                growth_opportunities=ai_review['growth_opportunities'],
                recognition_suggested=ai_review['recognition_suggested'],
                fairness_check=ai_review['fairness_check'],
                ethical_considerations=ai_review['ethical_considerations'],
                comparison_to_peers=None,
                timestamp=datetime.utcnow()
            )
        
    except json.JSONDecodeError as e:
        logger.error(f"AI returned invalid JSON: {e}")
        raise HTTPException(status_code=500, detail="AI response parsing failed")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/decisions/risk-assessment", response_model=RiskAssessmentResponse)
async def assess_project_risks(request: RiskAssessmentRequest):
    """
    AI-powered risk assessment and conflict detection for projects
    Combines risk analysis with conflict detection for comprehensive project health check
    """
    try:
        logger.info(f"🤖 AI Risk Assessment for project_id: {request.project_id}")
        
        # Fetch project data
        async with httpx.AsyncClient() as client:
            tasks_response = await client.get(f"{settings.nestjs_backend_url}/tasks")
            users_response = await client.get(f"{settings.nestjs_backend_url}/users")
            tasks = tasks_response.json()
            users = users_response.json()
        
        # Filter by project and optionally by team
        project_tasks = [t for t in tasks if t.get('project_id') == request.project_id]
        if request.team_id:
            team_user_ids = [u['id'] for u in users if u.get('team_id') == request.team_id]
            project_tasks = [t for t in project_tasks if t.get('assignee_id') in team_user_ids or t.get('assignee_id') is None]
        
        # Analyze risks
        blocked_tasks = [t for t in project_tasks if t.get('status') == 'BLOCKED']
        critical_tasks = [t for t in project_tasks if t.get('priority') == 'CRITICAL']
        in_progress = [t for t in project_tasks if t.get('status') == 'IN_PROGRESS']
        
        # Calculate workload by user
        user_workloads = {}
        for task in project_tasks:
            if task.get('assignee_id'):
                user_id = task['assignee_id']
                user_workloads[user_id] = user_workloads.get(user_id, 0) + task.get('story_points', 3)
        
        overloaded_users = [
            {'user_id': uid, 'workload': workload, 'name': next((u['name'] for u in users if u['id'] == uid), 'Unknown')}
            for uid, workload in user_workloads.items() if workload > 10
        ]
        
        # Deadline analysis
        from datetime import datetime, timedelta
        today = datetime(2026, 1, 3)  # Current demo date
        deadline_risks = []
        for task in project_tasks:
            if task.get('deadline') and task.get('status') != 'COMPLETED':
                deadline_date = datetime.strptime(task['deadline'], '%Y-%m-%d')
                days_remaining = (deadline_date - today).days
                if days_remaining <= 3:  # Risk if deadline within 3 days
                    deadline_risks.append({
                        'task_id': task['id'],
                        'title': task['title'],
                        'days_remaining': days_remaining,
                        'progress': task.get('progress', 0),
                        'status': task['status']
                    })
        
        # Create comprehensive AI prompt
        llm = get_llm()
        
        # Get all valid task IDs for the AI to reference
        valid_task_ids = sorted([t['id'] for t in project_tasks])
        task_list = chr(10).join([f"  • Task #{t['id']}: {t['title']} ({t.get('status')}, {t.get('progress', 0)}% complete)" 
                                   for t in project_tasks[:20]])  # Show first 20 tasks
        
        risk_summary = f"""
PROJECT OVERVIEW:
- Total tasks: {len(project_tasks)}
- Valid Task IDs: {valid_task_ids}
- Blocked tasks: {len(blocked_tasks)} (IDs: {[t['id'] for t in blocked_tasks]})
- Critical tasks: {len(critical_tasks)}
- In progress: {len(in_progress)}
- Overloaded team members: {len(overloaded_users)} ({', '.join([u['name'] for u in overloaded_users])})
- Deadline risks: {len(deadline_risks)} tasks with deadlines within 3 days

ALL PROJECT TASKS:
{task_list}

CRITICAL BLOCKED TASKS:
{chr(10).join([f"- Task #{t['id']}: {t['title']} (Blocked by: {t.get('blocking_tasks', [])}, Priority: {t.get('priority')})" for t in blocked_tasks[:5]]) if blocked_tasks else "None"}

DEADLINE PRESSURE:
{chr(10).join([f"- Task #{r['task_id']}: {r['title']} - {r['days_remaining']} days remaining, {r['progress']}% complete" for r in deadline_risks[:5]]) if deadline_risks else "None"}

OVERLOADED TEAM MEMBERS:
{chr(10).join([f"- {u['name']}: {u['workload']} story points" for u in overloaded_users]) if overloaded_users else "None"}
"""
        
        prompt = f"""You are an AI Project Risk Assessment Manager. Analyze this project's health and identify critical risks and conflicts.

{risk_summary}

YOUR TASK:
Provide a comprehensive risk assessment with clear bullet points, specific data, and actionable recommendations.

ANALYZE:
1. Overall risk level (LOW/MEDIUM/HIGH/CRITICAL)
2. Critical risks that could derail the project
3. Conflicts detected (speed vs quality, resource conflicts, deadline pressures)
4. Specific mitigation strategies
5. Recommended actions with priorities
6. Stakeholder communication message

RETURN ONLY valid JSON (no other text):
{{
    "overall_risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
    "risk_score": <0.0_to_1.0>,
    "executive_summary": "📊 [2-3 sentences summarizing project health, key risks, and urgency level]",
    "detailed_analysis": "🔍 Risk Analysis:\\n\\n• PROJECT HEALTH: [Overall status with specific numbers]\\n\\n• CRITICAL RISKS:\\n  - [Risk 1 with impact]\\n  - [Risk 2 with data]\\n\\n• CONFLICTS DETECTED:\\n  - [Conflict type and description]\\n\\n• TIMELINE CONCERNS: [Deadline risks with specific tasks]\\n\\n• RESOURCE ISSUES: [Overload/underutilization]\\n\\n• IMPACT ASSESSMENT: [What happens if not addressed]",
    "critical_risks": [
        {{"type": "deadline", "severity": "high", "description": "[Specific risk with task IDs and timeline]", "impact": "Project delay of X days"}},
        {{"type": "resource", "severity": "medium", "description": "[Team member overload details]", "impact": "Burnout risk"}},
        {{"type": "blocker", "severity": "high", "description": "[Blocked tasks preventing progress]", "impact": "Cascading delays"}}
    ],
    "conflicts_detected": [
        {{"type": "speed_vs_quality", "tasks": [1, 2], "description": "[Why this conflict exists]", "severity": "high"}},
        {{"type": "deadline_vs_wellbeing", "description": "[Team overload situation]", "severity": "medium"}}
    ],
    "mitigation_strategies": [
        "✅ [Specific actionable strategy with expected outcome]",
        "✅ [Another strategy with timeline]",
        "✅ [Third strategy with responsible party]"
    ],
    "recommended_actions": [
        {{"action": "[Specific immediate action]", "priority": "CRITICAL", "owner": "[Role/person]", "timeline": "[When]"}},
        {{"action": "[Another action]", "priority": "HIGH", "owner": "[Role]", "timeline": "[When]"}},
        {{"action": "[Third action]", "priority": "MEDIUM", "owner": "[Role]", "timeline": "[When]"}}
    ],
    "stakeholder_message": "📢 Stakeholder Communication:\\n\\n[Professional 3-4 sentence message explaining the situation, actions being taken, and revised expectations. Be transparent but constructive.]",
    "confidence_score": <0.0_to_1.0_assessment_confidence>
}}

IMPORTANT: 
- ONLY reference task IDs that are in the Valid Task IDs list above
- DO NOT make up or hallucinate task IDs that don't exist
- Use actual data from the risk summary
- Be specific with task IDs, names, and numbers from the data provided"""
        
        try:
            response = await invoke_llm_with_timeout(llm, prompt, timeout=30.0)
            
            # Extract JSON from response
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            if start_idx != -1 and end_idx != -1:
                content = content[start_idx:end_idx+1]
            
            logger.debug(f"Extracted JSON content: {content[:200]}...")
            ai_assessment = json.loads(content)
        except TimeoutError as e:
            logger.error("LLM timeout: %s", e)
            raise HTTPException(status_code=504, detail="LLM invocation timed out")
        
        # Log decision
        try:
            await decision_logger.log_decision(
                decision_type="RISK_ASSESSMENT",
                decision_maker="AI System",
                decision=f"Project {request.project_id} risk level: {ai_assessment['overall_risk_level']}",
                reasoning=ai_assessment['detailed_analysis'],
                ethical_considerations=["Balanced urgency with team wellbeing", "Transparent risk communication"],
                alternatives_considered=[s for s in ai_assessment.get('mitigation_strategies', [])[:3]],
                confidence_score=ai_assessment.get('confidence_score', 0.8),
                metadata={
                    "project_id": request.project_id,
                    "blocked_tasks": len(blocked_tasks),
                    "deadline_risks": len(deadline_risks),
                    "overloaded_members": len(overloaded_users)
                }
            )
            logger.info(f"Risk assessment logged")
        except Exception as log_error:
            logger.error(f"Failed to log risk assessment: {log_error}")
        
        return RiskAssessmentResponse(
            project_id=request.project_id,
            overall_risk_level=ai_assessment['overall_risk_level'],
            risk_score=ai_assessment['risk_score'],
            executive_summary=ai_assessment['executive_summary'],
            detailed_analysis=ai_assessment['detailed_analysis'],
            critical_risks=ai_assessment.get('critical_risks', []),
            conflicts_detected=ai_assessment.get('conflicts_detected', []),
            blocked_tasks=[{'task_id': t['id'], 'title': t['title'], 'blocked_by': t.get('blocking_tasks', [])} for t in blocked_tasks],
            overloaded_members=overloaded_users,
            deadline_risks=deadline_risks,
            mitigation_strategies=ai_assessment.get('mitigation_strategies', []),
            recommended_actions=ai_assessment.get('recommended_actions', []),
            stakeholder_message=ai_assessment.get('stakeholder_message', ''),
            confidence_score=ai_assessment.get('confidence_score', 0.8),
            timestamp=datetime.utcnow()
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"AI returned invalid JSON: {e}")
        raise HTTPException(status_code=500, detail="AI response parsing failed")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/audit/decisions")
async def get_all_decisions(limit: int = 100, offset: int = 0, decision_type: Optional[str] = None):
    """Get all AI decisions"""
    try:
        decisions = decision_logger.get_all_decisions(limit=limit, offset=offset, decision_type=decision_type)
        return {"total": len(decisions), "limit": limit, "offset": offset, "decisions": decisions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting AI Backend")
    logger.info(f"📡 Provider: {settings.llm_provider}")
    logger.info(f"🤖 Model: {settings.llm_model}")
    uvicorn.run("main:app", host=settings.fastapi_host, port=settings.fastapi_port, reload=True)
