"""
Supervisor Agent - LLM-based routing for ambiguous/complex questions.

Handles the remaining ~20% of questions that the fast router can't confidently route.
Uses an LLM to make intelligent routing decisions for multi-agent scenarios.
"""

import json
import re
from typing import Optional, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import get_openai_api_key, DEFAULT_LLM_MODEL
from src.prompts import get_prompt
from .types import SupervisorDecision, AgentType


def create_supervisor_agent():
    """
    Create supervisor LLM agent for intelligent routing.

    Uses a lightweight LLM call with low temperature for consistent routing.

    Returns:
        ChatOpenAI: Configured LLM for supervisor decisions
    """
    openai_api_key = get_openai_api_key()

    llm = ChatOpenAI(
        model=DEFAULT_LLM_MODEL,
        temperature=0.1,  # Low temperature for consistent, deterministic routing
        openai_api_key=openai_api_key
    )

    return llm


def supervisor_route(
    question: str,
    context: Optional[Dict] = None,
    hints: Optional[Dict] = None
) -> SupervisorDecision:
    """
    Use supervisor to make routing decision for ambiguous questions.

    This is called when the fast router lacks confidence (<85%).
    The supervisor analyzes the question and decides:
    - Which agent(s) to use
    - Whether to use multiple agents
    - Sequential vs parallel execution

    Args:
        question: User's question to route
        context: Optional conversation context (user profile, history, etc.)
        hints: Optional hints from fast router (keyword scores, etc.)

    Returns:
        SupervisorDecision with routing plan

    Example:
        >>> decision = supervisor_route(
        ...     "I want to save $1M for retirement, have $200k portfolio, on track?",
        ...     context={"user_context": {"has_portfolio": True}}
        ... )
        >>> print(decision.primary_agent)  # AgentType.GOAL_PLANNING
        >>> print(decision.secondary_agents)  # [AgentType.PORTFOLIO]
        >>> print(decision.execution_mode)  # "sequential"
    """
    llm = create_supervisor_agent()

    # Get supervisor prompt from centralized prompts
    supervisor_prompt = get_prompt("supervisor")

    # Build enhanced prompt with context
    full_prompt = _build_supervisor_prompt(
        supervisor_prompt, question, context, hints
    )

    # Get decision from LLM
    messages = [
        SystemMessage(content=supervisor_prompt),
        HumanMessage(content=full_prompt)
    ]

    response = llm.invoke(messages)

    # Parse response into structured decision
    decision = _parse_supervisor_response(response.content, question)

    return decision


def _build_supervisor_prompt(
    base_prompt: str,
    question: str,
    context: Optional[Dict],
    hints: Optional[Dict]
) -> str:
    """
    Build enhanced prompt for supervisor with question and context.

    Args:
        base_prompt: Base supervisor prompt
        question: User's question
        context: Conversation context
        hints: Fast router hints

    Returns:
        Complete prompt string
    """
    context_info = _format_context(context, hints)

    prompt = f"""
User Question: "{question}"

{context_info}

Analyze the question and provide your routing decision in JSON format.

Required JSON structure:
{{
  "primary_agent": "education|tax|goal_planning|portfolio|market|news",
  "secondary_agents": [],
  "execution_mode": "single|sequential|parallel",
  "reasoning": "explanation of routing decision"
}}

Your JSON response:
"""

    return prompt


def _format_context(context: Optional[Dict], hints: Optional[Dict]) -> str:
    """
    Format context and hints for supervisor prompt.

    Args:
        context: Conversation context
        hints: Fast router hints

    Returns:
        Formatted context string
    """
    parts = []

    # Add conversation context
    if context:
        parts.append("**Context:**")

        user_ctx = context.get("user_context", {})
        if user_ctx.get("has_portfolio"):
            parts.append("- User has an existing portfolio")
        if user_ctx.get("active_goals"):
            num_goals = len(user_ctx["active_goals"])
            parts.append(f"- User has {num_goals} active goal(s)")
        if user_ctx.get("risk_tolerance"):
            parts.append(f"- User risk tolerance: {user_ctx['risk_tolerance']}")
        if user_ctx.get("investment_stage"):
            stage = user_ctx["investment_stage"]
            if stage == "potential":
                parts.append("- User is researching potential investments (not yet invested)")
            elif stage == "current":
                parts.append("- User is a current investor")

        if context.get("last_agent"):
            parts.append(f"- Last agent used: {context['last_agent']}")

    # Add fast router hints
    if hints:
        parts.append("\n**Fast Router Analysis:**")

        if "keyword_scores" in hints:
            scores = hints["keyword_scores"]
            top_3 = list(scores.items())[:3]
            parts.append(f"- Top keyword matches: {top_3}")

        if "pattern_matched" in hints:
            parts.append(f"- Pattern matched: {hints['pattern_matched']}")

        if "winner_score" in hints and "margin" in hints:
            parts.append(
                f"- Score: {hints['winner_score']:.2f}, "
                f"Margin: {hints['margin']:.2f}"
            )

    if not parts:
        return "**Context:** No additional context available"

    return "\n".join(parts)


def _parse_supervisor_response(response: str, question: str) -> SupervisorDecision:
    """
    Parse supervisor LLM response into structured SupervisorDecision.

    Handles various response formats and provides fallback if parsing fails.

    Args:
        response: LLM response (should contain JSON)
        question: Original question (for fallback reasoning)

    Returns:
        SupervisorDecision with routing plan
    """
    # Try to extract JSON from response
    json_match = re.search(r'\{.*\}', response, re.DOTALL)

    if json_match:
        try:
            data = json.loads(json_match.group())

            # Extract and validate primary agent
            primary_agent_str = data.get("primary_agent", "education")
            try:
                primary_agent = AgentType(primary_agent_str)
            except ValueError:
                # Invalid agent name - default to education
                primary_agent = AgentType.EDUCATION

            # Extract secondary agents
            secondary_agents = []
            for agent_str in data.get("secondary_agents", []):
                try:
                    secondary_agents.append(AgentType(agent_str))
                except ValueError:
                    continue  # Skip invalid agent names

            # Extract execution mode
            execution_mode = data.get("execution_mode", "single")
            if execution_mode not in ["single", "sequential", "parallel"]:
                execution_mode = "single"

            # Extract reasoning
            reasoning = data.get("reasoning", "Supervisor routing decision")

            # Build workflow steps if sequential
            workflow_steps = []
            if execution_mode == "sequential" and secondary_agents:
                agents = [primary_agent] + secondary_agents
                workflow_steps = [
                    f"{i+1}. Call {agent.value} agent"
                    for i, agent in enumerate(agents)
                ]
                workflow_steps.append(f"{len(agents)+1}. Synthesize results")

            return SupervisorDecision(
                primary_agent=primary_agent,
                secondary_agents=secondary_agents,
                execution_mode=execution_mode,
                reasoning=reasoning,
                workflow_steps=workflow_steps
            )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # JSON parsing failed - use intelligent fallback
            return _fallback_decision(question, f"Parsing error: {e}")

    # No JSON found - use intelligent fallback
    return _fallback_decision(question, "No JSON in response")


def _fallback_decision(question: str, error_msg: str) -> SupervisorDecision:
    """
    Create intelligent fallback decision when supervisor parsing fails.

    Uses simple heuristics to make a reasonable routing choice.

    Args:
        question: Original question
        error_msg: Why fallback was triggered

    Returns:
        SupervisorDecision with fallback routing
    """
    question_lower = question.lower()

    # Simple heuristics for fallback
    if any(word in question_lower for word in ["portfolio", "holdings", "my stocks"]):
        agent = AgentType.PORTFOLIO
    elif any(word in question_lower for word in ["save", "goal", "retirement plan"]):
        agent = AgentType.GOAL_PLANNING
    elif any(word in question_lower for word in ["market", "sector", "index"]):
        agent = AgentType.MARKET
    elif any(word in question_lower for word in ["invest", "should i", "risks"]):
        agent = AgentType.NEWS
    elif any(word in question_lower for word in ["tax", "deduction", "ira", "401k"]):
        agent = AgentType.TAX
    else:
        # Default to education for general questions
        agent = AgentType.EDUCATION

    return SupervisorDecision(
        primary_agent=agent,
        secondary_agents=[],
        execution_mode="single",
        reasoning=f"Fallback routing ({error_msg}): Heuristic matched '{agent.value}'",
        workflow_steps=[]
    )


def analyze_supervisor_decision(
    question: str,
    context: Optional[Dict] = None,
    hints: Optional[Dict] = None
) -> Dict:
    """
    Analyze supervisor decision with full transparency.

    Useful for debugging and understanding supervisor routing.

    Args:
        question: Question to analyze
        context: Optional context
        hints: Optional hints from fast router

    Returns:
        Dict with decision and full analysis

    Example:
        >>> analysis = analyze_supervisor_decision(
        ...     "I want to save $1M, have $200k in stocks, on track?"
        ... )
        >>> print(analysis['decision'])
        >>> print(analysis['prompt_sent'])
        >>> print(analysis['raw_response'])
    """
    llm = create_supervisor_agent()
    supervisor_prompt = get_prompt("supervisor")
    full_prompt = _build_supervisor_prompt(
        supervisor_prompt, question, context, hints
    )

    messages = [
        SystemMessage(content=supervisor_prompt),
        HumanMessage(content=full_prompt)
    ]

    response = llm.invoke(messages)
    decision = _parse_supervisor_response(response.content, question)

    return {
        'decision': decision.dict(),
        'prompt_sent': full_prompt,
        'raw_response': response.content,
        'context': context,
        'hints': hints,
    }
