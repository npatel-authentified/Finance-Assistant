# AI Finance Assistant

An intelligent multi-agent financial assistant powered by LangGraph that provides personalized financial guidance through specialized agents for education, portfolio analysis, market insights, goal planning, and investment research.

## Overview

The AI Finance Assistant uses a **multi-agent architecture** with intelligent routing to handle diverse financial queries. It features:

- **5 Specialized Agents**: Each expert in their domain (education, portfolio, market, news, goal planning)
- **Smart Routing**: Fast router for direct agent selection, supervisor for complex multi-agent workflows
- **LangGraph Orchestration**: Declarative state graph for transparent, maintainable agent coordination
- **Web Interface**: Clean Gradio-based chat UI with real-time execution progress
- **Conversation Memory**: Persistent conversation history using LangGraph checkpointing
- **RAG-Powered**: Financial education agent uses retrieval augmented generation with Pinecone

## Features

### Multi-Agent System
- **📚 Education Agent** - Explains financial concepts using RAG over curated financial documents
- **🎯 Goal Planning Agent** - Helps set and track financial goals with personalized recommendations
- **💼 Portfolio Analysis Agent** - Analyzes investment portfolios and provides optimization suggestions
- **📈 Market Analysis Agent** - Provides real-time market data and stock analysis using yfinance
- **📰 News Synthesizer Agent** - Research and synthesize investment news for potential investors

### Intelligent Routing
- **Fast Router**: Direct routing to appropriate agent with confidence scoring (90%+ confidence → direct route)
- **Supervisor**: Multi-agent orchestration for complex queries requiring multiple specialized agents
- **Sequential Execution**: Clean sequential agent workflow for multi-step analysis

### User Experience
- **Web UI**: Modern chat interface with Gradio
- **Real-time Progress**: See which agents are executing and routing decisions
- **Conversation Memory**: Context-aware responses using conversation history
- **Thread Management**: Multiple conversation threads with persistence

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Question                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Fast Router   │  (Confidence-based routing)
         └────────┬───────┘
                  │
        ┌─────────┴──────────┐
        │                    │
   High Confidence      Low Confidence
        │                    │
        ▼                    ▼
  ┌──────────┐         ┌─────────────┐
  │  Agent   │         │ Supervisor  │  (Multi-agent orchestration)
  └──────────┘         └─────┬───────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                Sequential        Parallel
                    │                 │
                    ▼                 ▼
           ┌─────────────────┐  ┌─────────────────┐
           │ Agent → Agent   │  │ Agent + Agent   │
           └─────────────────┘  └─────────────────┘
                    │                 │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  Synthesizer    │  (Combine results)
                    └─────────────────┘
```

## Project Structure

```
ai_finance_assistant/
├── README.md                          # This file
├── LANGGRAPH_IMPLEMENTATION.md        # LangGraph architecture details
├── WEB_UI_GUIDE.md                    # Web UI documentation
├── main_langgraph.py                  # CLI entry point
├── run_webapp.py                      # Web UI launcher
├── pyproject.toml                     # Project dependencies
├── pytest.ini                         # Test configuration
├── financial_assistant_graph.png      # Graph visualization
├── src/
│   ├── config.py                      # Centralized configuration
│   ├── prompts.py                     # Agent system prompts
│   ├── agents/                        # Agent implementations
│   │   ├── ques_ans.py               # Education agent (RAG)
│   │   ├── goal_planning.py          # Goal planning agent
│   │   ├── portfolio_analysis.py     # Portfolio analysis agent
│   │   ├── market_analysis.py        # Market data agent
│   │   └── news_synthesizer.py       # News research agent
│   ├── orchestration/                 # LangGraph orchestration
│   │   ├── graph.py                  # State graph definition
│   │   ├── router.py                 # Fast router logic
│   │   ├── supervisor.py             # Supervisor agent
│   │   ├── nodes.py                  # Graph nodes
│   │   └── types.py                  # State types
│   ├── rag/                          # RAG system
│   │   ├── ingestion.py              # Document embedding
│   │   └── retrieval_and_generation.py
│   ├── core/
│   │   └── tools/                    # Agent tools
│   └── utils/
├── tests/                             # Test suite
│   ├── test_langgraph.py
│   ├── test_simplified_graph.py
│   └── ...
└── web_app/                           # Gradio web UI
    ├── app.py                        # Main web application
    ├── test_ui.py                    # UI test (no dependencies)
    └── README.md                     # Web UI quick start
```

## Installation

### Prerequisites

- Python 3.12.7 or higher
- pip or uv package manager (uv recommended)

### Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Using pip
pip install -e .
```

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required API Keys:**
- `OPENAI_API_KEY` - OpenAI API key for LLM
- `PINECONE_API_KEY` - Pinecone API key for RAG (education agent)

**Optional Configuration:**
- `PINECONE_INDEX_NAME` - Pinecone index name (default: "finance-education-index")
- `LLM_MODEL` - LLM model (default: "gpt-4o-mini")
- `EMBEDDING_MODEL` - Embedding model (default: "text-embedding-3-small")
- `CHUNK_SIZE` - Document chunk size (default: 300)
- `CHUNK_OVERLAP` - Chunk overlap (default: 100)
- `RETRIEVAL_K` - Documents to retrieve (default: 5)

### Test Configuration

```bash
python -m src.config
```

## Usage

### Option 1: Web UI (Recommended)

Launch the Gradio web interface:

```bash
# Using the launcher script
python run_webapp.py

# Or directly
python web_app/app.py

# With uv
uv run python web_app/app.py
```

The web UI will open at `http://localhost:7860` with:
- Real-time agent execution progress
- Conversation memory within each thread
- Clear chat and new thread management
- Example questions to get started

**Test the UI (without full dependencies):**
```bash
python web_app/test_ui.py
```

### Option 2: Command Line

Run the LangGraph CLI:

```bash
# Interactive mode
python main_langgraph.py

# Ask a specific question
python main_langgraph.py "How is my portfolio performing?"

# With uv
uv run python main_langgraph.py "What is compound interest?"
```

**Example Questions:**

```bash
# Education agent
python main_langgraph.py "What is a 401k and how does it work?"

# Goal planning agent
python main_langgraph.py "Help me plan for retirement in 20 years"

# Portfolio analysis agent
python main_langgraph.py "How is my portfolio performing?"

# Market analysis agent
python main_langgraph.py "Should I invest in Tesla stock?"

# News synthesizer agent
python main_langgraph.py "What's the latest news on AI stocks?"
```

### RAG Setup (Education Agent)

The education agent requires financial documents to be indexed:

```bash
# Index documents (one-time setup)
python -m src.rag.ingestion

# With custom document directory
python -m src.rag.ingestion /path/to/financial/docs

# Force re-indexing if documents changed
python -m src.rag.ingestion --force-reindex
```

Or programmatically:

```python
from src.rag import setup_finance_rag

# One-time setup
vectorstore = setup_finance_rag("./financial_docs")

# Force re-indexing
vectorstore = setup_finance_rag("./financial_docs", force_reindex=True)
```

## How It Works

### 1. Fast Router (First Decision)

When you ask a question, the **Fast Router** analyzes it and:
- Classifies the question type (education, portfolio, market, etc.)
- Assigns a confidence score (0.0 - 1.0)
- Routes accordingly:
  - **High confidence (≥0.9)**: Direct to specific agent
  - **Low confidence (<0.9)**: Send to Supervisor

### 2. Agent Execution

**Single Agent (Fast Route):**
```
Question → Fast Router → Education Agent → Response
```

**Multi-Agent (Supervisor Route):**
```
Question → Fast Router → Supervisor → [Agent 1, Agent 2] → Synthesizer → Response
```

### 3. Conversation Memory

Each conversation thread maintains context:
- User messages and agent responses stored in LangGraph state
- Thread-based persistence using checkpointer
- Context available to agents for follow-up questions

## API Reference

### Orchestration

```python
from src.orchestration import create_app_with_memory

# Create the LangGraph application
app = create_app_with_memory()

# Run with streaming
config = {"configurable": {"thread_id": "session_123"}}
for chunk in app.stream(
    {"messages": [{"role": "user", "content": "What is a Roth IRA?"}]},
    config,
    stream_mode="updates"
):
    print(chunk)

# Get final state
final_state = app.get_state(config)
print(final_state.values["final_response"])
```

### Individual Agents

```python
from src.agents import (
    create_education_agent,
    create_goal_planning_agent,
    create_portfolio_agent,
    create_market_agent,
    create_news_agent,
)

# Use individual agents directly
education_agent = create_education_agent()
response = education_agent.invoke({"messages": [{"role": "user", "content": "What is diversification?"}]})
```

### Configuration

```python
from src.config import (
    get_openai_api_key,
    get_pinecone_api_key,
    validate_config,
    INDEX_NAME,
    DEFAULT_LLM_MODEL,
)

# Validate configuration
validate_config()
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_langgraph.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Visualize Graph

Generate graph visualization:

```python
from src.orchestration import create_app_with_memory

app = create_app_with_memory()
png_bytes = app.get_graph().draw_mermaid_png()

with open("financial_assistant_graph.png", "wb") as f:
    f.write(png_bytes)
```

### Adding New Agents

1. Create agent in `src/agents/my_agent.py`
2. Add agent type to `src/orchestration/types.py`
3. Register agent node in `src/orchestration/graph.py`
4. Update router to recognize agent in `src/orchestration/router.py`
5. Add system prompt to `src/prompts.py`

See `LANGGRAPH_IMPLEMENTATION.md` for detailed architecture guide.

## Troubleshooting

### API Key Errors

Ensure `.env` file exists with valid API keys:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Module Import Errors

Install the package in development mode:
```bash
uv sync  # or pip install -e .
```

### Web UI Issues

Test the UI without dependencies:
```bash
python web_app/test_ui.py
```

For Gradio 6.x specific issues, see `WEB_UI_GUIDE.md`.

### Memory Not Working

The web UI automatically handles conversation memory. Each thread maintains its own context. Click "Clear Chat" to start a new conversation thread.

## Documentation

- **LANGGRAPH_IMPLEMENTATION.md** - Detailed architecture and graph flow
- **WEB_UI_GUIDE.md** - Web interface usage and features
- **web_app/README.md** - Web UI quick start guide

## Roadmap

- [ ] User authentication and profile persistence
- [ ] PostgreSQL checkpointer for production
- [ ] Additional financial agents (retirement, tax planning)
- [ ] Enhanced portfolio tools (optimization, rebalancing)
- [ ] Real-time market alerts
- [ ] Export conversation history

## Contributing

1. Follow DRY principles - use `src/config.py` and `src/prompts.py`
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation
5. Follow the existing agent patterns

## License

MIT License

## Support

For issues and questions, please open an issue on the project repository.
