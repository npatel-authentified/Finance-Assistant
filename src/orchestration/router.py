"""
Fast Router - Rule-based routing for common questions.

Routes approximately 80% of questions directly to agents without supervisor overhead.
Uses pattern matching and keyword scoring for fast, deterministic routing.
"""

import re
from typing import Optional, Dict, List, Tuple
from .types import RouterDecision, AgentType


# Confidence threshold for direct routing (0.85 = 85% confidence)
DIRECT_ROUTE_THRESHOLD = 0.85


# Exact pattern matching (highest confidence - 95%)
# These patterns are unambiguous and clearly indicate intent
EXACT_PATTERNS: Dict[AgentType, List[str]] = {
    AgentType.PORTFOLIO: [
        r"(?:how (?:is|did)|what's|analyze) my portfolio",
        r"my portfolio (?:performance|return|diversification|risk|value|allocation)",
        r"analyze my (?:holdings|investments|positions)",
        r"(?:am I|is my portfolio) (?:diversified|concentrated|balanced)",
        r"compare (?:my )?portfolio (?:to|vs|against) (?:S&P|benchmark|market)",
        r"rebalanc(?:e|ing) (?:my )?portfolio",
        r"my (?:stocks|shares|holdings|positions)",
    ],

    AgentType.GOAL_PLANNING: [
        r"(?:I want to|I need to|help me) save (?:for|up)",
        r"(?:create|set|make|plan|build) (?:a )?(?:financial )?goal",
        r"how much (?:do I need to|should I|must I) save",
        r"saving for (?:a )?(?:house|home|car|education|college|wedding|retirement|vacation)",
        r"retirement (?:goal|planning|savings|fund)",
        r"(?:am I|is my goal) on track",
        r"prioritize (?:my )?goals",
        r"update (?:my )?goal",
        r"(?:goal|savings) (?:progress|status|update)",
    ],

    AgentType.MARKET: [
        # Stock/ETF price and data queries (PRIORITY - check before education patterns)
        r"(?:what(?:'s| is)|what's the|get|show|tell me) (?:the )?(?:\w+(?:'s)?) (?:stock|ETF|etf)? ?(?:price|max|high|low|close|open|current)",
        r"(?:\w+) (?:stock|ETF|etf)? ?(?:price|max price|high|low|52.week)",

        # Performance and returns queries (CRITICAL - add before education patterns!)
        r"(?:what(?:'s| is)|what's the|show|get) (?:the )?(?:performance|returns?|gains?) (?:of|for|on)",
        r"(?:how|what) (?:has|have|is|are) .+? (?:performed|performing|returned|done)",
        r"performance (?:of|for) .+? (?:over|in|during|for) (?:\d+[ymd]|year|month|lifetime|YTD|ytd)",
        r"(?:1|5|10) (?:year|yr|y) (?:performance|return|gains?)",
        r"(?:lifetime|historical|past) (?:performance|returns?)",

        # Stock/ETF tickers (individual stocks and ETFs)
        r"(?:AAPL|TSLA|MSFT|GOOGL|AMZN|NVDA|META|NFLX|FB|GOOG|CRM|AMD|INTC|ORCL|IBM|BA|DIS|WMT|JPM|BAC|V|MA)\b",  # Stocks
        r"(?:VOO|VTI|SPY|QQQ|IVV|VEA|VWO|AGG|BND|VIG|VYM|SCHD|VUG|VTV|VO|VB)\b",  # Common ETFs
        r"(?:Apple|Tesla|Microsoft|Google|Amazon|Nvidia|Meta|Netflix|Facebook|Oracle|Intel|Boeing|Disney|Walmart|JPMorgan)\s+(?:stock|share)",
        r"(?:Vanguard|iShares|SPDR|Schwab|Fidelity) .+? (?:ETF|Fund)",

        # Market overview
        r"what's the market (?:doing|performance|status)",
        r"how (?:is|are) (?:the )?(?:S&P|Nasdaq|Dow|(?:stock )?market|indices)",
        r"(?:sector|industry) performance",

        # Technical analysis
        r"technical analysis (?:of|for) \w+",
        r"(?:RSI|moving average|MA|MACD|beta|volatility) (?:of|for) \w+",
        r"compare (?:the )?fundamentals (?:of|for|between)",
        r"(?:stock|market) technicals",

        # Earnings and sentiment
        r"earnings (?:calendar|report|announcement)",
        r"market (?:overview|sentiment|breadth|conditions)",
    ],

    AgentType.NEWS: [
        r"should I invest in \w+",
        r"(?:thinking about|considering|researching) investing (?:in)?",
        r"what are (?:the )?(?:investment )?risks? (?:of|for|in) \w+",
        r"investment (?:thesis|case|opportunity|analysis) (?:for|of|on)",
        r"is (?:now|this|it) (?:a )?good time to (?:invest|buy)",
        r"(?:bull|bear) case (?:for|of|on) \w+",
        r"compare .+ (?:for investment|to invest|as an? investment)",
        r"due diligence (?:on|for) \w+",
        r"(?:investment )?(?:timing|opportunity) (?:for|of)",
        r"watchlist (?:news|updates?)",
    ],

    AgentType.EDUCATION: [
        r"what (?:is|are|does) (?:a |an |the )?(?!my|the market)",  # "What is X?" but not "my"
        r"(?:explain|define|describe|clarify) (?:what |how |why )?(?!my|the market)",
        r"how (?:do|does) .+? work",
        r"(?:what's the |what is the )?difference between",
        r"(?:tell me about|teach me about|help me understand)",
        r"(?:learn|understand) (?:about |how |what )",
    ],
}


# Keyword weights for scoring (when patterns don't match)
# Format: {keyword: weight} where higher weight = stronger signal
KEYWORD_WEIGHTS: Dict[AgentType, Dict[str, int]] = {
    AgentType.PORTFOLIO: {
        # Strong signals (weight: 3)
        "portfolio": 3, "holdings": 3, "positions": 3, "my stocks": 3,
        "diversification": 3, "concentration": 3, "allocation": 3,
        "rebalance": 3, "my shares": 3,

        # Medium signals (weight: 2)
        "invested": 2, "sharpe": 2, "beta": 2, "volatility": 2,
        "risk": 2, "performance": 2, "return": 2, "benchmark": 2,

        # Weak signals (weight: 1)
        "value": 1, "stocks": 1, "shares": 1,
    },

    AgentType.GOAL_PLANNING: {
        # Strong signals
        "goal": 3, "save": 3, "saving": 3, "target": 3,
        "retirement": 3, "emergency fund": 3, "down payment": 3,

        # Medium signals
        "plan": 2, "need": 2, "afford": 2, "years": 2,
        "monthly": 2, "annual": 2, "priority": 2,

        # Weak signals
        "money": 1, "future": 1, "fund": 1, "budget": 1,
    },

    AgentType.MARKET: {
        # Strong signals - Stock/ETF ticker symbols
        "AAPL": 4, "TSLA": 4, "MSFT": 4, "GOOGL": 4, "AMZN": 4, "NVDA": 4, "META": 4,
        "VOO": 4, "VTI": 4, "SPY": 4, "QQQ": 4, "IVV": 4,  # Common ETFs

        # Strong signals - Performance and price queries
        "performance": 4, "returns": 4, "return": 4, "gains": 4,
        "stock price": 4, "max price": 4, "stock high": 4, "stock low": 4,
        "52-week": 4, "52 week": 4, "all-time high": 4,
        "1 year": 4, "5 year": 4, "10 year": 4, "lifetime": 4, "YTD": 4,
        "performed": 4, "performing": 4,

        # Strong signals - Market data
        "market": 3, "sector": 3, "index": 3, "indices": 3,
        "S&P": 3, "Nasdaq": 3, "Dow": 3, "technical": 3,
        "fundamentals": 3, "earnings": 3, "ETF": 3, "Vanguard": 3,

        # Medium signals
        "RSI": 2, "moving average": 2, "P/E": 2, "PE ratio": 2,
        "revenue": 2, "MACD": 2, "momentum": 2,
        "Apple": 2, "Tesla": 2, "Microsoft": 2, "Google": 2, "Amazon": 2,

        # Weak signals
        "price": 1, "stock": 1, "trading": 1, "volume": 1, "high": 1, "low": 1,
    },

    AgentType.NEWS: {
        # Strong signals
        "should I invest": 3, "investment": 3, "risks": 3,
        "opportunity": 3, "timing": 3, "thesis": 3,
        "bull case": 3, "bear case": 3, "due diligence": 3,

        # Medium signals
        "news": 2, "recent": 2, "developments": 2,
        "considering": 2, "thinking about": 2, "researching": 2,
        "watchlist": 2,

        # Weak signals
        "buy": 1, "research": 1, "looking at": 1, "interested": 1,
    },

    AgentType.EDUCATION: {
        # Strong signals
        "what is": 3, "explain": 3, "how does": 3,
        "difference between": 3, "teach me": 3, "define": 3,

        # Medium signals
        "learn": 2, "understand": 2, "concept": 2, "work": 2,

        # Weak signals
        "help": 1, "question": 1, "about": 1,
    },
}


def fast_route(
    question: str,
    context: Optional[Dict] = None
) -> RouterDecision:
    """
    Fast routing using pattern matching and keyword scoring.

    This is the first pass at routing - handles ~80% of questions quickly
    without requiring an LLM call.

    Args:
        question: User's question to route
        context: Optional conversation context (user profile, history, etc.)

    Returns:
        RouterDecision with routing recommendation (direct or supervisor)

    Example:
        >>> decision = fast_route("How is my portfolio performing?")
        >>> print(decision.route)  # "direct"
        >>> print(decision.agent)  # AgentType.PORTFOLIO
        >>> print(decision.confidence)  # 0.95
    """
    question_lower = question.lower()

    # Step 1: Try exact pattern matching (highest confidence: 95%)
    pattern_decision = _try_pattern_matching(question_lower, context)
    if pattern_decision:
        return pattern_decision

    # Step 2: Keyword scoring (medium confidence: varies)
    keyword_decision = _try_keyword_scoring(question_lower, context)
    if keyword_decision:
        return keyword_decision

    # Step 3: No confident match - send to supervisor
    return _fallback_to_supervisor(
        "No confident pattern or keyword match found"
    )


def _try_pattern_matching(
    question_lower: str,
    context: Optional[Dict]
) -> Optional[RouterDecision]:
    """
    Try to match question against exact patterns.

    Returns RouterDecision if confident match found, None otherwise.
    """
    for agent_type, patterns in EXACT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, question_lower):
                confidence = 0.95  # Very high confidence for exact patterns

                # Apply context adjustments
                if context:
                    confidence = _adjust_confidence_for_context(
                        confidence, agent_type, context
                    )

                if confidence >= DIRECT_ROUTE_THRESHOLD:
                    return RouterDecision(
                        route="direct",
                        agent=agent_type,
                        confidence=confidence,
                        reasoning=f"Exact pattern match: '{pattern}'",
                        context_hints={"pattern_matched": pattern}
                    )

    return None


def _try_keyword_scoring(
    question_lower: str,
    context: Optional[Dict]
) -> Optional[RouterDecision]:
    """
    Score question against keyword weights for each agent.

    Returns RouterDecision if confidence threshold met, None otherwise.
    """
    # Calculate scores for all agents
    scores: Dict[AgentType, float] = {}
    for agent_type, keywords in KEYWORD_WEIGHTS.items():
        score = _calculate_keyword_score(question_lower, keywords)
        scores[agent_type] = score

    if not scores:
        return None

    # Find winner and runner-up
    sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winner, winner_score = sorted_agents[0]
    runner_up_score = sorted_agents[1][1] if len(sorted_agents) > 1 else 0

    # Calculate confidence based on score and margin
    confidence = _calculate_confidence(
        winner_score, runner_up_score, context, winner
    )

    # Only route directly if confidence is high enough
    if confidence >= DIRECT_ROUTE_THRESHOLD:
        return RouterDecision(
            route="direct",
            agent=winner,
            confidence=confidence,
            reasoning=f"Keyword score: {winner_score:.2f} (margin: {winner_score - runner_up_score:.2f})",
            context_hints={
                "keyword_scores": {k.value: v for k, v in sorted_agents[:3]},
                "winner_score": winner_score,
                "margin": winner_score - runner_up_score
            }
        )

    # Close competition or low scores - use supervisor
    return None


def _calculate_keyword_score(question: str, keywords: Dict[str, int]) -> float:
    """
    Calculate weighted keyword score for a question.

    Args:
        question: Question text (lowercase)
        keywords: Dict of {keyword: weight}

    Returns:
        Normalized score (0.0-10.0)
    """
    total_score = 0

    for keyword, weight in keywords.items():
        if keyword in question:
            total_score += weight

    # Normalize by question length to avoid bias toward long questions
    word_count = len(question.split())
    normalized_score = (total_score / max(word_count, 5)) * 10

    return min(normalized_score, 10.0)  # Cap at 10


def _calculate_confidence(
    winner_score: float,
    runner_up_score: float,
    context: Optional[Dict],
    winner: AgentType
) -> float:
    """
    Calculate routing confidence based on score, margin, and context.

    Args:
        winner_score: Top agent's keyword score
        runner_up_score: Second place agent's score
        context: Conversation context
        winner: Winning agent type

    Returns:
        Confidence score (0.0-1.0)
    """
    if winner_score == 0:
        return 0.0

    # Base confidence from absolute score (0-10 scale)
    base_confidence = min(winner_score / 10.0, 0.9)

    # Boost confidence if there's a clear margin over second place
    margin = winner_score - runner_up_score
    if margin > 3.0:
        base_confidence += 0.1  # Clear winner
    elif margin > 2.0:
        base_confidence += 0.05  # Moderate margin
    elif margin < 1.0:
        base_confidence -= 0.15  # Too close to call

    # Apply context adjustments
    if context:
        base_confidence = _adjust_confidence_for_context(
            base_confidence, winner, context
        )

    return max(0.0, min(1.0, base_confidence))


def _adjust_confidence_for_context(
    confidence: float,
    agent_type: AgentType,
    context: Dict
) -> float:
    """
    Adjust confidence based on conversation context and user profile.

    Args:
        confidence: Current confidence score
        agent_type: Agent being routed to
        context: Context dict with user_context, last_agent, etc.

    Returns:
        Adjusted confidence score
    """
    # Boost if same agent was just used (topic continuity)
    if context.get("last_agent") == agent_type.value:
        confidence += 0.05

    # Adjust based on user profile
    user_context = context.get("user_context", {})

    # Portfolio agent: reduce confidence if user doesn't have portfolio
    if agent_type == AgentType.PORTFOLIO:
        if not user_context.get("has_portfolio", True):  # Default True if unknown
            confidence -= 0.2

    # Goal planning: boost if user has active goals
    if agent_type == AgentType.GOAL_PLANNING:
        if user_context.get("active_goals"):
            confidence += 0.05

    # News synthesizer: boost if user is in research phase
    if agent_type == AgentType.NEWS:
        if user_context.get("investment_stage") == "potential":
            confidence += 0.05

    return max(0.0, min(1.0, confidence))


def _fallback_to_supervisor(
    reason: str,
    context_hints: Optional[Dict] = None
) -> RouterDecision:
    """
    Create a RouterDecision that routes to supervisor.

    Args:
        reason: Why supervisor is needed
        context_hints: Optional hints to pass to supervisor

    Returns:
        RouterDecision with route="supervisor"
    """
    return RouterDecision(
        route="supervisor",
        agent=None,
        confidence=0.0,
        reasoning=reason,
        context_hints=context_hints or {}
    )


# Utility function for testing/debugging
def analyze_routing(question: str, context: Optional[Dict] = None) -> Dict:
    """
    Analyze routing decision with detailed breakdown.

    Useful for debugging and understanding why questions route to certain agents.

    Args:
        question: Question to analyze
        context: Optional context

    Returns:
        Dict with detailed routing analysis

    Example:
        >>> analysis = analyze_routing("How is my portfolio doing?")
        >>> print(analysis)
        {
            'decision': RouterDecision(...),
            'pattern_matches': ['portfolio performance'],
            'keyword_scores': {'portfolio': 8.5, 'market': 2.1, ...},
            'context_adjustments': 'No context provided'
        }
    """
    question_lower = question.lower()

    # Find all pattern matches
    pattern_matches = {}
    for agent_type, patterns in EXACT_PATTERNS.items():
        matches = [p for p in patterns if re.search(p, question_lower)]
        if matches:
            pattern_matches[agent_type.value] = matches

    # Calculate keyword scores for all agents
    keyword_scores = {}
    for agent_type, keywords in KEYWORD_WEIGHTS.items():
        score = _calculate_keyword_score(question_lower, keywords)
        keyword_scores[agent_type.value] = score

    # Get actual routing decision
    decision = fast_route(question, context)

    return {
        'decision': decision.model_dump(),
        'pattern_matches': pattern_matches,
        'keyword_scores': keyword_scores,
        'context': context or 'No context provided',
    }
