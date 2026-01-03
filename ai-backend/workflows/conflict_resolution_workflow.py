"""
Conflict Resolution Workflow - Handles priority conflicts using Graph of Thoughts reasoning
Use Case 2: Conflict Resolution Between Priorities
"""
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
import asyncio
from utils.llm_factory import create_llm
from utils.llm_utils import invoke_llm_with_timeout
import operator
import json
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class ConflictState(TypedDict):
    """State passed between agents in conflict resolution"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    conflict_type: str
    project: Dict[str, Any]
    tasks: list[Dict[str, Any]]
    team: Dict[str, Any]
    business_priorities: list[str]
    team_wellbeing_factors: Dict[str, Any]
    analysis: Dict[str, Any]
    trade_offs: Dict[str, Any]
    resolution: Dict[str, Any]
    ethical_justification: str
    reasoning_trace: list[str]


class ConflictResolutionWorkflow:
    """LangGraph workflow for resolving conflicts between priorities"""
    
    def __init__(self):
        # Use provider-agnostic LLM from factory (Groq or other configured provider)
        self.llm = create_llm()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the conflict resolution workflow"""
        workflow = StateGraph(ConflictState)
        
        # Add nodes
        workflow.add_node("conflict_analyzer", self.conflict_analyzer_node)
        workflow.add_node("stakeholder_perspective", self.stakeholder_perspective_node)
        workflow.add_node("ethics_evaluator", self.ethics_evaluator_node)
        workflow.add_node("tradeoff_calculator", self.tradeoff_calculator_node)
        workflow.add_node("resolution_generator", self.resolution_generator_node)
        
        # Define flow
        workflow.set_entry_point("conflict_analyzer")
        workflow.add_edge("conflict_analyzer", "stakeholder_perspective")
        workflow.add_edge("stakeholder_perspective", "ethics_evaluator")
        workflow.add_edge("ethics_evaluator", "tradeoff_calculator")
        workflow.add_edge("tradeoff_calculator", "resolution_generator")
        workflow.add_edge("resolution_generator", END)
        
        return workflow.compile()
    
    def conflict_analyzer_node(self, state: ConflictState) -> ConflictState:
        """
        Analyzes the conflict and identifies core issues
        """
        logger.info("Conflict Analyzer: Identifying conflict dimensions...")
        
        conflict_type = state["conflict_type"]
        project = state["project"]
        tasks = state["tasks"]
        
        prompt = f"""
You are a Conflict Analyzer in a project management AI system.
Identify and analyze the core conflict dimensions.

CONFLICT TYPE: {conflict_type}

PROJECT DETAILS:
{json.dumps(project, indent=2)}

TASKS INVOLVED:
{json.dumps(tasks, indent=2)}

Analyze:
1. What are the conflicting priorities?
2. What are the time pressures?
3. What are the quality requirements?
4. What are the resource constraints?
5. What are the stakeholder expectations?

Return your analysis as JSON:
{{
    "primary_conflict": "<description>",
    "secondary_conflicts": ["<list>"],
    "time_pressure": "<low|medium|high>",
    "quality_requirements": "<flexible|moderate|strict>",
    "resource_constraints": ["<list>"],
    "stakeholder_expectations": {{
        "business": ["<expectations>"],
        "technical": ["<expectations>"],
        "team": ["<expectations>"]
    }},
    "conflict_severity": "<low|medium|high|critical>",
    "reasoning": "<your analysis>"
}}
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Conflict analyzer LLM invocation timed out")
            content = ""
        
        try:
            analysis = json.loads(content)
            state["analysis"] = analysis
            state["reasoning_trace"].append(f"Conflict Analysis: {analysis.get('reasoning', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse conflict analyzer response")
            state["reasoning_trace"].append(f"Conflict Analysis: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    def stakeholder_perspective_node(self, state: ConflictState) -> ConflictState:
        """
        Evaluates conflict from multiple stakeholder perspectives
        """
        logger.info("Stakeholder Perspective: Analyzing different viewpoints...")
        
        analysis = state.get("analysis", {})
        business_priorities = state["business_priorities"]
        team_wellbeing = state["team_wellbeing_factors"]
        
        prompt = f"""
You are a Multi-Stakeholder Perspective Agent in a project management AI system.
Evaluate the conflict from different stakeholder viewpoints.

CONFLICT ANALYSIS:
{json.dumps(analysis, indent=2)}

BUSINESS PRIORITIES:
{json.dumps(business_priorities, indent=2)}

TEAM WELLBEING FACTORS:
{json.dumps(team_wellbeing, indent=2)}

Evaluate from these perspectives:
1. **Business Perspective**: Revenue, deadlines, customer satisfaction
2. **Technical Quality Perspective**: Code quality, testing, maintainability
3. **Team Wellbeing Perspective**: Burnout risk, work-life balance, morale
4. **Customer Perspective**: Value delivery, reliability, trust

For each perspective, identify:
- What they value most
- Their concerns about each resolution option
- Their acceptable trade-offs

Return as JSON:
{{
    "perspectives": {{
        "business": {{
            "priorities": ["<list>"],
            "concerns": ["<list>"],
            "acceptable_tradeoffs": ["<list>"]
        }},
        "technical_quality": {{
            "priorities": ["<list>"],
            "concerns": ["<list>"],
            "acceptable_tradeoffs": ["<list>"]
        }},
        "team_wellbeing": {{
            "priorities": ["<list>"],
            "concerns": ["<list>"],
            "acceptable_tradeoffs": ["<list>"]
        }},
        "customer": {{
            "priorities": ["<list>"],
            "concerns": ["<list>"],
            "acceptable_tradeoffs": ["<list>"]
        }}
    }},
    "common_ground": ["<shared priorities across stakeholders>"],
    "major_tensions": ["<irreconcilable differences>"],
    "reasoning": "<your analysis>"
}}
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Stakeholder perspective LLM invocation timed out")
            content = ""
        
        try:
            perspectives = json.loads(content)
            state["analysis"]["stakeholder_perspectives"] = perspectives
            state["reasoning_trace"].append(f"Stakeholder Analysis: {perspectives.get('reasoning', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse stakeholder perspective response")
            state["reasoning_trace"].append(f"Stakeholder Analysis: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    def ethics_evaluator_node(self, state: ConflictState) -> ConflictState:
        """
        Evaluates ethical implications of different resolution paths
        """
        logger.info("Ethics Evaluator: Assessing ethical implications...")
        
        analysis = state.get("analysis", {})
        
        prompt = f"""
You are an Ethics Evaluator in a project management AI system.
Assess the ethical implications of different resolution approaches.

CONFLICT ANALYSIS:
{json.dumps(analysis, indent=2)}

Evaluate ethical considerations:
1. **Fairness**: Does the resolution fairly balance stakeholder needs?
2. **Human Wellbeing**: Does it prioritize team health and sustainability?
3. **Long-term Impact**: What are the long-term consequences?
4. **Trust**: Does it maintain stakeholder trust?
5. **Responsibility**: Does it demonstrate ethical leadership?

Consider these resolution scenarios:
A) Prioritize speed (meet deadline, sacrifice quality/testing)
B) Prioritize quality (delay deadline, maintain standards)
C) Balanced approach (extend deadline slightly, moderate quality standards)

Return ethical evaluation as JSON:
{{
    "scenario_evaluations": {{
        "prioritize_speed": {{
            "fairness_score": <0-1>,
            "wellbeing_score": <0-1>,
            "longterm_score": <0-1>,
            "trust_score": <0-1>,
            "ethical_concerns": ["<list>"],
            "justification": "<explanation>"
        }},
        "prioritize_quality": {{
            "fairness_score": <0-1>,
            "wellbeing_score": <0-1>,
            "longterm_score": <0-1>,
            "trust_score": <0-1>,
            "ethical_concerns": ["<list>"],
            "justification": "<explanation>"
        }},
        "balanced_approach": {{
            "fairness_score": <0-1>,
            "wellbeing_score": <0-1>,
            "longterm_score": <0-1>,
            "trust_score": <0-1>,
            "ethical_concerns": ["<list>"],
            "justification": "<explanation>"
        }}
    }},
    "recommended_approach": "<prioritize_speed|prioritize_quality|balanced_approach>",
    "ethical_principles_applied": ["<list>"],
    "reasoning": "<your ethical analysis>"
}}
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Ethics evaluator LLM invocation timed out")
            content = ""
        
        try:
            ethics_eval = json.loads(content)
            state["analysis"]["ethical_evaluation"] = ethics_eval
            state["reasoning_trace"].append(f"Ethics Evaluation: {ethics_eval.get('reasoning', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse ethics evaluator response")
            state["reasoning_trace"].append(f"Ethics Evaluation: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    def tradeoff_calculator_node(self, state: ConflictState) -> ConflictState:
        """
        Calculates precise trade-offs for each resolution option
        """
        logger.info("Tradeoff Calculator: Computing impact metrics...")
        
        analysis = state.get("analysis", {})
        tasks = state["tasks"]
        
        prompt = f"""
You are a Trade-off Calculator in a project management AI system.
Calculate precise trade-offs for each resolution option.

CONFLICT ANALYSIS:
{json.dumps(analysis, indent=2)}

TASKS INVOLVED:
{json.dumps(tasks, indent=2)}

Calculate trade-offs on these dimensions (use -3 to +3 scale):
- Speed (time to delivery)
- Quality (code quality, testing coverage)
- Cost (resources, budget)
- Team Wellbeing (stress, burnout risk)
- Customer Satisfaction (value, reliability)
- Technical Debt (future maintenance burden)

For each scenario:
A) Prioritize Speed: Rush to meet deadline
B) Prioritize Quality: Delay to maintain standards
C) Balanced: Moderate extension with adjusted scope

Return trade-off calculations as JSON:
{{
    "tradeoffs": {{
        "prioritize_speed": {{
            "speed": <-3 to +3>,
            "quality": <-3 to +3>,
            "cost": <-3 to +3>,
            "team_wellbeing": <-3 to +3>,
            "customer_satisfaction": <-3 to +3>,
            "technical_debt": <-3 to +3>,
            "overall_score": <sum of above>,
            "explanation": "<detailed explanation>"
        }},
        "prioritize_quality": {{
            "speed": <-3 to +3>,
            "quality": <-3 to +3>,
            "cost": <-3 to +3>,
            "team_wellbeing": <-3 to +3>,
            "customer_satisfaction": <-3 to +3>,
            "technical_debt": <-3 to +3>,
            "overall_score": <sum of above>,
            "explanation": "<detailed explanation>"
        }},
        "balanced_approach": {{
            "speed": <-3 to +3>,
            "quality": <-3 to +3>,
            "cost": <-3 to +3>,
            "team_wellbeing": <-3 to +3>,
            "customer_satisfaction": <-3 to +3>,
            "technical_debt": <-3 to +3>,
            "overall_score": <sum of above>,
            "explanation": "<detailed explanation>"
        }}
    }},
    "recommended_scenario": "<prioritize_speed|prioritize_quality|balanced_approach>",
    "reasoning": "<why this is optimal>"
}}
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Tradeoff calculator LLM invocation timed out")
            content = ""
        
        try:
            tradeoffs = json.loads(content)
            state["trade_offs"] = tradeoffs
            state["reasoning_trace"].append(f"Trade-off Analysis: {tradeoffs.get('reasoning', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse tradeoff calculator response")
            state["reasoning_trace"].append(f"Trade-off Analysis: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    def resolution_generator_node(self, state: ConflictState) -> ConflictState:
        """
        Generates final resolution with actionable recommendations
        """
        logger.info("Resolution Generator: Creating final resolution...")
        
        analysis = state.get("analysis", {})
        trade_offs = state.get("trade_offs", {})
        
        prompt = f"""
You are a Resolution Generator in a project management AI system.
Create a final, actionable resolution for the conflict.

CONFLICT ANALYSIS:
{json.dumps(analysis, indent=2)}

TRADE-OFFS:
{json.dumps(trade_offs, indent=2)}

Generate a comprehensive resolution that:
1. States the decision clearly
2. Explains the reasoning
3. Addresses all stakeholder concerns
4. Provides actionable next steps
5. Includes ethical justification

Format for project manager communication:
- Executive summary (2-3 sentences)
- Detailed reasoning (4-5 paragraphs)
- Action items (bulleted list)
- Stakeholder messaging (how to communicate to team, business, customers)

Return as JSON:
{{
    "decision": "<the chosen resolution approach>",
    "timeline_adjustment": "<e.g., extend by 2 days, no change, etc>",
    "scope_adjustment": "<any scope changes>",
    "resource_adjustment": "<any resource changes>",
    "executive_summary": "<2-3 sentence summary>",
    "detailed_reasoning": "<4-5 paragraph explanation>",
    "ethical_justification": "<why this is the ethically right choice>",
    "action_items": [
        {{
            "action": "<specific action>",
            "owner": "<who should do it>",
            "timeline": "<when>"
        }}
    ],
    "stakeholder_messaging": {{
        "team": "<how to communicate to team>",
        "business": "<how to communicate to business stakeholders>",
        "customer": "<how to communicate to customers>"
    }},
    "success_metrics": ["<how to measure if this resolution worked>"],
    "contingency_plan": "<backup plan if issues arise>",
    "reasoning": "<summary of decision logic>"
}}

Example output:
"Accelerating delivery may impact testing quality. A one-day delay ensures quality compliance and reduces team stress."
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Resolution generator LLM invocation timed out")
            content = ""
        
        try:
            resolution = json.loads(content)
            state["resolution"] = resolution
            state["ethical_justification"] = resolution.get("ethical_justification", "")
            state["reasoning_trace"].append(f"Resolution: {resolution.get('reasoning', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse resolution generator response")
            state["reasoning_trace"].append(f"Resolution: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    async def run(
        self,
        conflict_type: str,
        project: Dict[str, Any],
        tasks: list,
        team: Dict[str, Any],
        business_priorities: list[str],
        team_wellbeing_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run the complete conflict resolution workflow
        
        Args:
            conflict_type: Type of conflict (speed_vs_quality, deadline_vs_wellbeing, etc.)
            project: Project details
            tasks: List of tasks involved in conflict
            team: Team details
            business_priorities: List of business priorities
            team_wellbeing_factors: Team wellbeing indicators
            
        Returns:
            Complete resolution with analysis and recommendations
        """
        logger.info(f"Starting conflict resolution workflow for: {conflict_type}")
        
        # Initialize state
        initial_state: ConflictState = {
            "messages": [HumanMessage(content=f"Resolve conflict: {conflict_type}")],
            "conflict_type": conflict_type,
            "project": project,
            "tasks": tasks,
            "team": team,
            "business_priorities": business_priorities,
            "team_wellbeing_factors": team_wellbeing_factors,
            "analysis": {},
            "trade_offs": {},
            "resolution": {},
            "ethical_justification": "",
            "reasoning_trace": []
        }
        
        # Run the workflow
        result = self.workflow.invoke(initial_state)
        
        # Extract and return results
        return {
            "conflict_type": result["conflict_type"],
            "analysis": result["analysis"],
            "trade_offs": result["trade_offs"],
            "resolution": result["resolution"],
            "ethical_justification": result["ethical_justification"],
            "reasoning_trace": result["reasoning_trace"]
        }


# Create singleton instance
conflict_resolution_workflow = ConflictResolutionWorkflow()
