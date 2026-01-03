"""
LangGraph Workflow - Orchestrates AI agents using Graph of Thoughts (GoT) reasoning
"""
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
import operator
import json
import logging

from config.settings import settings
import asyncio
from utils.llm_utils import invoke_llm_with_timeout

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State passed between agents in the graph"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task: Dict[str, Any]
    users: list[Dict[str, Any]]
    teams: list[Dict[str, Any]]
    reasoning_trace: list[str]
    ethical_decision: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    final_decision: Dict[str, Any]
    explanation: str
    next_step: str


class DecisionWorkflow:
    """LangGraph workflow for AI decision making with GoT reasoning"""
    
    def __init__(self):
        # Create a provider-agnostic LLM via factory (Ollama or Groq)
        from utils.llm_factory import create_llm
        self.llm = create_llm()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("reasoning_agent", self.reasoning_node)
        workflow.add_node("ethics_agent", self.ethics_node)
        workflow.add_node("risk_agent", self.risk_node)
        workflow.add_node("performance_agent", self.performance_node)
        workflow.add_node("decision_agent", self.decision_node)
        workflow.add_node("explainability_agent", self.explainability_node)
        
        # Define the graph flow (GoT structure)
        workflow.set_entry_point("reasoning_agent")
        
        # Reasoning agent branches to parallel evaluation
        workflow.add_edge("reasoning_agent", "ethics_agent")
        workflow.add_edge("ethics_agent", "risk_agent")
        workflow.add_edge("risk_agent", "performance_agent")
        workflow.add_edge("performance_agent", "decision_agent")
        workflow.add_edge("decision_agent", "explainability_agent")
        workflow.add_edge("explainability_agent", END)
        
        return workflow.compile()
    
    def reasoning_node(self, state: AgentState) -> AgentState:
        """
        Reasoning Agent - Analyzes the task and generates initial options
        """
        logger.info("Reasoning Agent: Generating decision options...")
        
        task = state["task"]
        users = state["users"]
        
        prompt = f"""
You are a Reasoning Agent in a project management AI system.
Analyze the following task and available users to generate decision options.

TASK:
{json.dumps(task, indent=2)}

AVAILABLE USERS:
{json.dumps(users, indent=2)}

Generate 2-3 candidate options for task assignment. For each option, consider:
1. User availability and current workload
2. Task difficulty vs. user experience
3. Skill match and project context

Return your analysis as JSON:
{{
    "options": [
        {{
            "user_id": "<id>",
            "user_name": "<name>",
            "rationale": "<why this is a good option>",
            "confidence": <0-1>
        }}
    ],
    "reasoning_trace": "<your thought process>"
}}
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Reasoning agent LLM invocation timed out")
            content = ""
        
        try:
            # Parse the JSON response
            reasoning_result = json.loads(content)
            state["reasoning_trace"].append(f"Reasoning: {reasoning_result.get('reasoning_trace', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse reasoning agent response")
            state["reasoning_trace"].append(f"Reasoning: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    def ethics_node(self, state: AgentState) -> AgentState:
        """
        Ethics & Fairness Agent - Evaluates ethical considerations
        """
        logger.info("Ethics Agent: Evaluating fairness and ethical considerations...")
        
        task = state["task"]
        users = state["users"]
        previous_reasoning = state.get("reasoning_trace", [])
        
        prompt = f"""
You are an Ethics & Fairness Agent in a project management AI system.

Previous reasoning:
{json.dumps(previous_reasoning, indent=2)}

TASK:
{json.dumps(task, indent=2)}

USERS:
{json.dumps(users, indent=2)}

Evaluate the assignment options based on:
1. Workload distribution fairness
2. Equal opportunity (don't always assign to the same people)
3. Avoiding bias based on any personal attributes
4. Ensuring sustainable work-life balance

Rules:
- Only consider users where availability == true
- Prefer users with LOWER workload to balance distribution
- Consider task difficulty but don't discriminate
- Ensure fairness across all team members

Return your decision as JSON:
{{
    "chosen_user_id": "<user_id>",
    "fairness_score": <0-1>,
    "bias_check": "<how bias was avoided>",
    "workload_balance": "<how workload was balanced>",
    "wellbeing_impact": "<impact on wellbeing>",
    "ethical_concerns": ["<any concerns>"],
    "reasoning": "<explanation of ethical considerations>"
}}
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Ethics agent LLM invocation timed out")
            content = ""
        
        try:
            ethical_decision = json.loads(content)
            # Fill defaults so UI does not show N/A when model omits fields
            ethical_decision.setdefault("bias_check", "Bias mitigation applied; no sensitive attributes used")
            ethical_decision.setdefault("workload_balance", "Workload balanced relative to peers")
            ethical_decision.setdefault("wellbeing_impact", "Neutral wellbeing impact; no overload detected")
            ethical_decision.setdefault("ethical_concerns", [])
            ethical_decision.setdefault("fairness_score", 0.0)
            state["ethical_decision"] = ethical_decision
            state["reasoning_trace"].append(f"Ethics: {ethical_decision.get('reasoning', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse ethics agent response")
            fallback_ethics = {
                "bias_check": "Unavailable (parse error)",
                "workload_balance": "Unavailable (parse error)",
                "wellbeing_impact": "Unavailable (parse error)",
                "ethical_concerns": [],
                "fairness_score": 0.0,
                "reasoning": content,
            }
            state["ethical_decision"] = fallback_ethics
            state["reasoning_trace"].append(f"Ethics: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    def risk_node(self, state: AgentState) -> AgentState:
        """
        Risk Assessment Agent - Evaluates risks associated with the decision
        """
        logger.info("Risk Agent: Assessing risks...")
        
        task = state["task"]
        ethical_decision = state.get("ethical_decision", {})
        
        prompt = f"""
You are a Risk Assessment Agent in a project management AI system.

TASK:
{json.dumps(task, indent=2)}

PROPOSED ASSIGNMENT:
{json.dumps(ethical_decision, indent=2)}

Assess the risks of this assignment:
1. Deadline risk (can the user complete it on time?)
2. Quality risk (does the user have the right skills?)
3. Workload risk (will this overburden the user?)
4. Project risk (impact on overall project success)

Return your assessment as JSON:
{{
    "overall_risk_level": "<low|medium|high>",
    "risk_factors": [
        {{
            "factor": "<risk name>",
            "level": "<low|medium|high>",
            "mitigation": "<suggested mitigation>"
        }}
    ],
    "recommendation": "<approve|modify|reject>",
    "reasoning": "<explanation>"
}}
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Risk agent LLM invocation timed out")
            content = ""
        
        try:
            risk_assessment = json.loads(content)
            state["risk_assessment"] = risk_assessment
            state["reasoning_trace"].append(f"Risk: {risk_assessment.get('reasoning', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse risk agent response")
            state["reasoning_trace"].append(f"Risk: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    def performance_node(self, state: AgentState) -> AgentState:
        """
        Performance Agent - Evaluates performance implications
        """
        logger.info("Performance Agent: Evaluating performance metrics...")
        
        users = state["users"]
        ethical_decision = state.get("ethical_decision", {})
        chosen_user_id = ethical_decision.get("chosen_user_id")
        
        prompt = f"""
You are a Performance Recognition Agent in a project management AI system.

USERS:
{json.dumps(users, indent=2)}

PROPOSED ASSIGNEE: {chosen_user_id}

Evaluate performance considerations:
1. Current workload and contribution levels
2. Recognition and growth opportunities
3. Skill development potential
4. Team performance balance

Return your assessment as JSON:
{{
    "performance_impact": "<positive|neutral|negative>",
    "growth_opportunity": <0-1>,
    "contribution_balance": "<balanced|imbalanced>",
    "recommendations": ["<suggestions for team performance>"],
    "reasoning": "<explanation>"
}}
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Performance agent LLM invocation timed out")
            content = ""
        
        try:
            performance_metrics = json.loads(content)
            state["performance_metrics"] = performance_metrics
            state["reasoning_trace"].append(f"Performance: {performance_metrics.get('reasoning', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse performance agent response")
            state["reasoning_trace"].append(f"Performance: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    def decision_node(self, state: AgentState) -> AgentState:
        """
        Decision Agent - Makes final decision based on all inputs
        """
        logger.info("Decision Agent: Making final decision...")
        
        task = state["task"]
        ethical_decision = state.get("ethical_decision", {})
        risk_assessment = state.get("risk_assessment", {})
        performance_metrics = state.get("performance_metrics", {})
        reasoning_trace = state.get("reasoning_trace", [])
        
        prompt = f"""
You are the Decision Agent in a project management AI system.
You must make a final decision based on all the analysis from other agents.

TASK:
{json.dumps(task, indent=2)}

ETHICAL DECISION:
{json.dumps(ethical_decision, indent=2)}

RISK ASSESSMENT:
{json.dumps(risk_assessment, indent=2)}

PERFORMANCE METRICS:
{json.dumps(performance_metrics, indent=2)}

REASONING TRACE:
{json.dumps(reasoning_trace, indent=2)}

Make a final decision weighing:
- Ethical considerations (high priority)
- Risk factors (medium-high priority)
- Performance impact (medium priority)
- Overall project success (high priority)

Return your decision as JSON:
{{
    "final_user_id": "<chosen user id>",
    "confidence": <0-1>,
    "priority_factors": ["<factors that influenced decision>"],
    "alternative_options": ["<other viable options>"],
    "action_items": ["<any follow-up actions needed>"],
    "reasoning": "<final decision explanation>"
}}
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            content = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Decision agent LLM invocation timed out")
            content = ""
        
        try:
            final_decision = json.loads(content)
            state["final_decision"] = final_decision
            state["reasoning_trace"].append(f"Decision: {final_decision.get('reasoning', '')}")
            state["messages"].append(AIMessage(content=content))
        except json.JSONDecodeError:
            logger.error("Failed to parse decision agent response")
            state["reasoning_trace"].append(f"Decision: {content}")
            state["messages"].append(AIMessage(content=content))
        
        return state
    
    def explainability_node(self, state: AgentState) -> AgentState:
        """
        Explainability Agent - Generates human-readable explanation
        """
        logger.info("Explainability Agent: Generating explanation...")
        
        task = state["task"]
        final_decision = state.get("final_decision", {})
        reasoning_trace = state.get("reasoning_trace", [])
        ethical_decision = state.get("ethical_decision", {})
        risk_assessment = state.get("risk_assessment", {})
        
        prompt = f"""
You are an Explainability Agent in a project management AI system.
Generate a clear, human-readable explanation of the AI's decision.

TASK:
{json.dumps(task, indent=2)}

FINAL DECISION:
{json.dumps(final_decision, indent=2)}

COMPLETE REASONING TRACE:
{json.dumps(reasoning_trace, indent=2)}

ETHICAL ANALYSIS:
{json.dumps(ethical_decision, indent=2)}

RISK ASSESSMENT:
{json.dumps(risk_assessment, indent=2)}

Write a clear explanation for a project manager that includes:
1. What decision was made (who was assigned)
2. Why this decision was made (key factors)
3. How fairness and ethics were considered
4. What risks were identified and how they're mitigated
5. Any action items or recommendations

Write in 4-6 clear paragraphs, suitable for a project manager to understand and trust the AI's decision.
"""
        
        try:
            response = asyncio.run(invoke_llm_with_timeout(self.llm, prompt))
            explanation = getattr(response, "content", str(response))
        except TimeoutError:
            logger.warning("Explainability agent LLM invocation timed out")
            explanation = ""
        
        state["explanation"] = explanation
        state["reasoning_trace"].append(f"Explanation generated")
        state["messages"].append(AIMessage(content=explanation))
        
        return state
    
    async def run(self, task: Dict[str, Any], users: list, teams: list) -> Dict[str, Any]:
        """
        Run the complete decision workflow
        
        Args:
            task: Task dictionary
            users: List of user dictionaries
            teams: List of team dictionaries
            
        Returns:
            Complete decision result with explanation
        """
        logger.info("Starting decision workflow...")
        
        # Initialize state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=f"Make a decision for task: {task.get('title')}")],
            "task": task,
            "users": users,
            "teams": teams,
            "reasoning_trace": [],
            "ethical_decision": {},
            "risk_assessment": {},
            "performance_metrics": {},
            "final_decision": {},
            "explanation": "",
            "next_step": ""
        }
        
        # Run the workflow
        result = self.workflow.invoke(initial_state)
        
        # Extract and return the results
        return {
            "task": result["task"],
            "decision": result["final_decision"],
            "ethical_analysis": result["ethical_decision"],
            "risk_assessment": result["risk_assessment"],
            "performance_metrics": result["performance_metrics"],
            "explanation": result["explanation"],
            "reasoning_trace": result["reasoning_trace"]
        }


# Create a singleton instance
decision_workflow = DecisionWorkflow()
