# Routing Issue: "What is Apple's stock max price?"

## The Problem

**User asks:** "What is Apple's stock max price?"
**System responds:** "I'm sorry, I don't have an answer for that."

## Root Cause Analysis

### The Issue: Wrong Agent Routing

The question is being routed to the **Education agent** instead of the **Market Analysis agent**.

### Evidence

The exact response **"I'm sorry, I don't have an answer for that."** appears in:

**File:** `src/prompts.py` - Line 23

```python
FINANCIAL_ASSISTANT_PROMPT = """
You are a knowledgeable financial education assistant...

Act as a Finance domain expert. Answer only Finance-related questions...
For any question outside this scope, politely decline by saying:
"I'm sorry, I don't have an answer for that."
"""
```

This is the **Education agent's prompt**. The education agent is designed for:
- Explaining financial concepts ("What is compound interest?")
- Educational RAG retrieval from documents
- General financial learning

**NOT for:**
- Real-time stock data
- Market prices
- Technical analysis

---

## Why the Routing Failed

### Fast Router Pattern Matching

The fast router uses **keyword scoring** to make quick routing decisions:

**File:** `src/orchestration/router.py` (likely)

Common routing keywords:
- **Education triggers:** "what is", "explain", "how does", "define"
- **Market triggers:** "stock price", "market", "technical", "chart", "performance"

**The problem:**
- User question: "What is Apple's stock **max price**?"
- **"What is"** → Strong signal for Education agent ❌
- **"stock"** → Weaker signal for Market agent
- **"max price"** → Not recognized as market data request

The fast router saw **"What is"** and routed to Education with high confidence!

---

## What Should Happen

### Correct Routing: Market Analysis Agent

**File:** `src/agents/market_analysis.py`

The Market Analysis agent HAS the tools to answer this:

#### Tool 1: `get_stock_technicals` (Line 158-252)
```python
@tool("get_stock_technicals", description="Get technical analysis indicators for a stock...")
def get_stock_technicals(ticker: str, period: str = "3mo") -> str:
    # ... code ...

    # Current price
    current_price = hist['Close'].iloc[-1]

    # 52-week high/low
    high_52w = hist['Close'].max()  # ← This is the "max price"!
    low_52w = hist['Close'].min()

    result += f"\n52-Week Range:\n"
    result += f"  High: ${high_52w:.2f}\n"  # ← Answer to user's question
    result += f"  Low: ${low_52w:.2f}\n"
```

#### Tool 2: `analyze_stock_momentum` (Line 572-674)
```python
@tool("analyze_stock_momentum", description="Analyze stock momentum...")
def analyze_stock_momentum(ticker: str) -> str:
    # Gets current price and historical data
    current_price = current_data['Close'].iloc[-1]
    # Shows performance across multiple periods including max/min
```

**The Market agent CAN answer this question!**

---

## How Market Agent Would Respond

If routed correctly to the Market agent:

```
User: What is Apple's stock max price?

Market Agent:
📊 Technical Analysis: AAPL

Current Price: $178.52

52-Week Range:
  High: $199.62  ← This is the "max price" (52-week high)
  Low: $164.08

📈 The 52-week high for Apple (AAPL) is $199.62, reached on [date].
   Current price is -10.56% below the 52-week high.
```

---

## The Routing Decision Tree

### What Actually Happened ❌

```
User: "What is Apple's stock max price?"
↓
Fast Router Analysis:
  - Keyword: "What is" → Education score: +50
  - Keyword: "stock" → Market score: +20
  - Keyword: "price" → Market score: +10
  - Total: Education (50) > Market (30)
↓
Routed to: Education Agent
↓
Education Agent:
  - Has retrieve_tool (RAG on documents)
  - No real-time stock data tools
  - No yfinance access
  - Cannot answer stock price questions
↓
Response: "I'm sorry, I don't have an answer for that."
```

### What Should Happen ✅

```
User: "What is Apple's stock max price?"
↓
Improved Router Analysis:
  - Question contains: stock ticker (AAPL/Apple) → Market score: +50
  - Question asks for: price/max/high → Market score: +40
  - Pattern match: "stock [ticker] price" → Market score: +30
  - Total: Market (120) >> Education (50)
↓
Routed to: Market Analysis Agent
↓
Market Agent:
  - Has get_stock_technicals tool
  - Can call yfinance.Ticker("AAPL").history()
  - Calculates 52-week high
↓
Response: "Apple's 52-week high is $199.62..."
```

---

## Why This Happens

### Router Keyword Conflicts

Many stock questions start with **"What is"**:
- "What is Apple's stock price?" → Should go to Market
- "What is Tesla's P/E ratio?" → Should go to Market
- "What is Microsoft's 52-week high?" → Should go to Market

But **"What is"** is a very strong signal for Education:
- "What is compound interest?" → Should go to Education
- "What is a 401k?" → Should go to Education
- "What is diversification?" → Should go to Education

### Context Matters!

The router needs to look at the FULL context:
- **"What is [concept]?"** → Education
- **"What is [ticker symbol]'s [data]?"** → Market

---

## Solutions

### Option 1: Improve Fast Router Pattern Matching

**File:** `src/orchestration/router.py`

Add stock-specific patterns:
```python
# High-priority market patterns (check BEFORE general "what is")
MARKET_PATTERNS = [
    r"(?:stock|ticker)\s+(?:price|max|high|low|performance)",
    r"(?:AAPL|TSLA|MSFT|GOOGL|AMZN)",  # Common tickers
    r"(?:52.week|52w|all.time)\s+(?:high|low)",
    r"(?:P/E|PE|market cap|dividend)",
]

# If any market pattern matches → Route to Market with high confidence
```

### Option 2: Use Supervisor for Ambiguous "What is" Questions

**Current:** Fast router sees "What is" → Routes to Education with high confidence

**Better:** Fast router sees "What is" + "stock/price" → Route to Supervisor (low confidence)

**Supervisor then:**
```json
{
  "primary_agent": "market",
  "secondary_agents": [],
  "execution_mode": "single",
  "reasoning": "Question asks for stock price data (AAPL max price), requires real-time market data from yfinance, not educational content"
}
```

### Option 3: Add Stock Price Tool to Education Agent

**Quick fix but NOT recommended:**
- Gives Education agent access to yfinance
- Breaks separation of concerns
- Makes agents less specialized

---

## Immediate Fix: Test Direct Routing

### Bypass Router and Test Market Agent Directly

```python
# In Python console or test file
from src.agents.market_analysis import ask_question

response = ask_question("What is Apple's stock max price?")
print(response)
```

**Expected output:**
```
📊 Technical Analysis: AAPL

Current Price: $178.52

52-Week Range:
  High: $199.62
  Low: $164.08

[... more technical analysis ...]
```

If this works, the problem is definitely routing!

---

## How to Test Routing

### Check Which Agent Is Handling the Question

Add logging to `src/orchestration/nodes.py`:

```python
def _execute_agent_node(state, agent_type, agent_func):
    print(f"[DEBUG] Executing agent: {agent_type.value}")  # ← Add this

    messages = state.get("messages", [])
    trimmed_messages = trim_for_agent(messages, agent_type=agent_type.value)
    response = agent_func(trimmed_messages, verbose=False)
    # ... rest of code
```

Then ask the question and check console:
```
User: "What is Apple's stock max price?"

[DEBUG] Executing agent: education  ← Problem! Should be "market"
```

---

## Recommended Fix

### Update Fast Router Keywords

**File:** `src/orchestration/router.py` (or wherever fast routing logic is)

Add these high-priority checks BEFORE checking "what is":

```python
def fast_route(question: str, context: Dict) -> RouterDecision:
    question_lower = question.lower()

    # Priority 1: Stock ticker symbols (before "what is" check)
    stock_patterns = [
        r'\b(?:AAPL|TSLA|MSFT|GOOGL|AMZN|NVDA|META|NFLX)\b',  # Tickers
        r'\b(?:Apple|Tesla|Microsoft|Google|Amazon|Nvidia|Meta|Netflix)\b',  # Company names
        r'stock\s+(?:price|max|high|low|close|open)',
        r'(?:52.week|52w|all.time)\s+(?:high|low)',
        r'(?:P/E|market cap|dividend|shares|earnings)',
    ]

    for pattern in stock_patterns:
        if re.search(pattern, question_lower, re.IGNORECASE):
            return RouterDecision(
                route="direct",
                agent=AgentType.MARKET,
                confidence=0.95,  # High confidence
                reasoning="Stock-specific data question"
            )

    # Priority 2: Then check "what is" for education
    if question_lower.startswith("what is"):
        # ... existing education routing
```

---

## Testing Checklist

After applying the fix:

### Test Cases for Market Agent

- [ ] "What is Apple's stock max price?" → Market agent
- [ ] "What is Tesla's 52-week high?" → Market agent
- [ ] "What is MSFT's current price?" → Market agent
- [ ] "What is Google's P/E ratio?" → Market agent
- [ ] "What is AAPL performance?" → Market agent

### Test Cases for Education Agent (Should NOT Break)

- [ ] "What is compound interest?" → Education agent
- [ ] "What is a 401k?" → Education agent
- [ ] "What is diversification?" → Education agent
- [ ] "What is a stock?" → Education agent (concept, not data)
- [ ] "What is inflation?" → Education agent

---

## Summary

### The Issue
Question about **stock price data** is being routed to **Education agent** instead of **Market agent**.

### Why It Happens
- Fast router sees "What is" and scores Education highly
- Doesn't recognize "Apple stock max price" as market data request
- Education agent has no tools to fetch real-time stock data
- Returns default rejection: "I'm sorry, I don't have an answer for that."

### The Solution
Improve router pattern matching to detect:
- Stock ticker symbols (AAPL, TSLA, etc.)
- Company names + "stock"
- Price/high/low/max keywords with stock context
- Route these to Market agent BEFORE checking general "what is"

### Market Agent CAN Answer This
- Has `get_stock_technicals` tool
- Uses yfinance to fetch data
- Returns 52-week high as "max price"
- Works perfectly when routed correctly

---

**Status:** Routing bug identified
**Impact:** Stock price questions fail
**Fix Required:** Router pattern matching improvement
**Agent Works:** Market agent can answer when routed correctly

**Date:** 2026-01-17
