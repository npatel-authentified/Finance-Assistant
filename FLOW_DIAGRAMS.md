# Interactive Flow Diagrams

## How to View These Diagrams

1. Copy any diagram below
2. Go to https://mermaid.live/
3. Paste the code
4. View the interactive diagram!

---

## Diagram 1: Complete System Flow

```mermaid
graph TD
    START([User Question]) --> FAST_ROUTER[Fast Router<br/>Pattern Matching]

    FAST_ROUTER -->|Confidence >= 0.9| AGENT_DIRECT[Agent Direct]
    FAST_ROUTER -->|Confidence < 0.9| SUPERVISOR[Supervisor<br/>LLM Analysis]

    SUPERVISOR -->|Single Agent| AGENT_SUPER[Agent]
    SUPERVISOR -->|Multi-Agent| AGENT1[Agent 1]

    AGENT_DIRECT --> END1([END])
    AGENT_SUPER --> END2([END])

    AGENT1 --> SEQ_ROUTER1{Sequence Router}
    SEQ_ROUTER1 -->|More Agents| AGENT2[Agent 2]
    AGENT2 --> SEQ_ROUTER2{Sequence Router}
    SEQ_ROUTER2 -->|More Agents| AGENT3[Agent 3]
    AGENT3 --> SEQ_ROUTER3{Sequence Router}
    SEQ_ROUTER3 -->|Queue Complete| SYNTHESIZER[Synthesizer<br/>Combine Results]

    SYNTHESIZER --> END3([END])

    style START fill:#e1f5ff
    style END1 fill:#c8e6c9
    style END2 fill:#c8e6c9
    style END3 fill:#c8e6c9
    style FAST_ROUTER fill:#fff9c4
    style SUPERVISOR fill:#ffe0b2
    style SYNTHESIZER fill:#f8bbd0
    style SEQ_ROUTER1 fill:#e0e0e0
    style SEQ_ROUTER2 fill:#e0e0e0
    style SEQ_ROUTER3 fill:#e0e0e0
```

---

## Diagram 2: Scenario - High Confidence Single Agent

**Example: "What is a 401k?"**

```mermaid
graph TD
    START([User: What is a 401k?]) --> FAST_ROUTER[Fast Router]

    FAST_ROUTER -->|Keywords: 401k, retirement<br/>Confidence: 0.95| EDU_AGENT[Education Agent<br/>RAG Query]

    EDU_AGENT -->|Response: A 401k is...| END([END<br/>2 nodes, ~2s])

    style START fill:#e1f5ff
    style FAST_ROUTER fill:#fff9c4
    style EDU_AGENT fill:#c5e1a5
    style END fill:#c8e6c9
```

---

## Diagram 3: Scenario - Low Confidence Single Agent

**Example: "I want to plan something for my future"**

```mermaid
graph TD
    START([User: Plan for future]) --> FAST_ROUTER[Fast Router]

    FAST_ROUTER -->|Ambiguous<br/>Confidence: 0.65| SUPERVISOR[Supervisor<br/>LLM Decides]

    SUPERVISOR -->|Primary: Goal Planning<br/>Mode: Single| GOAL_AGENT[Goal Planning Agent]

    GOAL_AGENT -->|Response: Let's create a plan...| END([END<br/>3 nodes, ~3-4s])

    style START fill:#e1f5ff
    style FAST_ROUTER fill:#fff9c4
    style SUPERVISOR fill:#ffe0b2
    style GOAL_AGENT fill:#c5e1a5
    style END fill:#c8e6c9
```

---

## Diagram 4: Scenario - Multi-Agent Sequential (3 Agents)

**Example: "Should I invest in Tesla? Consider my portfolio."**

```mermaid
graph TD
    START([User: Should I invest<br/>in Tesla? Consider<br/>my portfolio]) --> FAST_ROUTER[Fast Router]

    FAST_ROUTER -->|Complex Query<br/>Confidence: 0.45| SUPERVISOR[Supervisor]

    SUPERVISOR -->|Plan: Portfolio → Market → Goal<br/>Mode: Sequential| PORT_AGENT[Portfolio Agent<br/>Analyze current holdings]

    PORT_AGENT -->|Results: 60% tech stocks...| SEQ1{Sequence Router}

    SEQ1 -->|Index: 0→1<br/>Next: Market| MARKET_AGENT[Market Agent<br/>Analyze Tesla stock]

    MARKET_AGENT -->|Results: Tesla at $250...| SEQ2{Sequence Router}

    SEQ2 -->|Index: 1→2<br/>Next: Goal Planning| GOAL_AGENT[Goal Planning Agent<br/>Make recommendation]

    GOAL_AGENT -->|Results: Based on analysis...| SEQ3{Sequence Router}

    SEQ3 -->|Index: 2→3<br/>Queue Complete| SYNTH[Synthesizer<br/>Combine 3 Results]

    SYNTH -->|Final: PORTFOLIO + MARKET + GOAL| END([END<br/>10 nodes, ~8-12s])

    style START fill:#e1f5ff
    style FAST_ROUTER fill:#fff9c4
    style SUPERVISOR fill:#ffe0b2
    style PORT_AGENT fill:#c5e1a5
    style MARKET_AGENT fill:#c5e1a5
    style GOAL_AGENT fill:#c5e1a5
    style SEQ1 fill:#e0e0e0
    style SEQ2 fill:#e0e0e0
    style SEQ3 fill:#e0e0e0
    style SYNTH fill:#f8bbd0
    style END fill:#c8e6c9
```

---

## Diagram 5: State Transitions

```mermaid
stateDiagram-v2
    [*] --> FastRouter: messages: [user_msg]

    FastRouter --> DirectAgent: confidence >= 0.9<br/>router_decision set
    FastRouter --> Supervisor: confidence < 0.9<br/>router_decision set

    DirectAgent --> [*]: final_response set

    Supervisor --> SingleAgent: execution_mode=single<br/>supervisor_decision set
    Supervisor --> MultiAgent1: execution_mode=sequential<br/>execution_plan created

    SingleAgent --> [*]: final_response set

    MultiAgent1 --> SequenceRouter1: agent_results updated<br/>current_index++
    SequenceRouter1 --> MultiAgent2: Check queue:<br/>more agents
    MultiAgent2 --> SequenceRouter2: agent_results updated<br/>current_index++
    SequenceRouter2 --> Synthesizer: Queue complete

    Synthesizer --> [*]: final_response set
```

---

## Diagram 6: Decision Points

```mermaid
flowchart TD
    Q1{Fast Router<br/>Confidence?}
    Q1 -->|>= 0.9| A1[Direct to Agent]
    Q1 -->|< 0.9| A2[Send to Supervisor]

    A2 --> Q2{Supervisor<br/>Execution Mode?}
    Q2 -->|single| A3[One Agent]
    Q2 -->|sequential| A4[Create Execution Plan]

    A4 --> Q3{After Agent:<br/>Execution Plan<br/>Exists?}
    Q3 -->|Yes| A5[Sequence Router]
    Q3 -->|No| A6[END]

    A5 --> Q4{Sequence Router:<br/>More Agents<br/>in Queue?}
    Q4 -->|Yes| A7[Next Agent]
    Q4 -->|No| A8[Synthesizer]

    A7 --> Q3

    style Q1 fill:#fff9c4
    style Q2 fill:#ffe0b2
    style Q3 fill:#e0e0e0
    style Q4 fill:#e0e0e0
    style A8 fill:#f8bbd0
```

---

## Diagram 7: Edge Cases Flow

```mermaid
graph TD
    START([Input]) --> CHECK1{Messages<br/>Empty?}

    CHECK1 -->|Yes| DEFAULT[Default to<br/>Education Agent]
    CHECK1 -->|No| NORMAL[Normal Flow]

    NORMAL --> AGENT[Agent Execution]

    AGENT --> CHECK2{Agent<br/>Error?}

    CHECK2 -->|Yes| ERROR[Return Error Message<br/>Clear execution_plan]
    CHECK2 -->|No| SUCCESS[Return Response]

    ERROR --> END1([END])
    SUCCESS --> CHECK3{Multi-Agent<br/>Plan?}

    CHECK3 -->|Yes| CONTINUE[Continue to<br/>Next Agent]
    CHECK3 -->|No| END2([END])

    CONTINUE --> AGENT
    DEFAULT --> END3([END])

    style CHECK1 fill:#ffecb3
    style CHECK2 fill:#ffecb3
    style CHECK3 fill:#ffecb3
    style ERROR fill:#ffcdd2
    style SUCCESS fill:#c8e6c9
```

---

## Diagram 8: Execution Plan Structure

```mermaid
graph LR
    subgraph "Execution Plan State"
        EP[execution_plan]
        EP --> AQ[agents_queue:<br/>PORTFOLIO, MARKET, GOAL]
        EP --> CI[current_index: 0]
        EP --> NS[needs_synthesis: true]
    end

    subgraph "Agent 1 Executes"
        A1[Portfolio Agent] --> UPD1[current_index: 0 → 1]
    end

    subgraph "Agent 2 Executes"
        A2[Market Agent] --> UPD2[current_index: 1 → 2]
    end

    subgraph "Agent 3 Executes"
        A3[Goal Agent] --> UPD3[current_index: 2 → 3]
    end

    subgraph "Check Complete"
        CHK[current_index == len<br/>agents_queue?] --> SYNTH[Synthesizer]
    end

    EP --> A1
    UPD1 --> A2
    UPD2 --> A3
    UPD3 --> CHK

    style EP fill:#e1f5ff
    style AQ fill:#fff9c4
    style CI fill:#ffe0b2
    style NS fill:#c5e1a5
    style SYNTH fill:#f8bbd0
```

---

## Diagram 9: Agent Results Accumulation

```mermaid
graph TD
    START([Start Multi-Agent]) --> INIT[agent_results: empty]

    INIT --> A1[Portfolio Agent]
    A1 --> R1[agent_results:<br/>portfolio: Response 1]

    R1 --> A2[Market Agent]
    A2 --> R2[agent_results:<br/>portfolio: Response 1<br/>market: Response 2]

    R2 --> A3[Goal Agent]
    A3 --> R3[agent_results:<br/>portfolio: Response 1<br/>market: Response 2<br/>goal: Response 3]

    R3 --> SYNTH[Synthesizer<br/>Combines all 3]
    SYNTH --> FINAL[final_response:<br/>PORTFOLIO ANALYSIS<br/>MARKET ANALYSIS<br/>GOAL ANALYSIS<br/>COMPREHENSIVE]

    style INIT fill:#e1f5ff
    style R1 fill:#c5e1a5
    style R2 fill:#a5d6a7
    style R3 fill:#81c784
    style SYNTH fill:#f8bbd0
    style FINAL fill:#c8e6c9
```

---

## Diagram 10: Conversation Memory Flow

```mermaid
sequenceDiagram
    participant User
    participant WebUI
    participant LangGraph
    participant Checkpointer
    participant Agent

    User->>WebUI: Question 1: "I have a portfolio"
    WebUI->>LangGraph: invoke({messages: [Q1]}, thread_id="abc")
    LangGraph->>Checkpointer: Load state for thread "abc"
    Checkpointer-->>LangGraph: Empty (new thread)
    LangGraph->>Agent: Execute with [Q1]
    Agent-->>LangGraph: Response 1
    LangGraph->>Checkpointer: Save state: [Q1, R1]
    LangGraph-->>WebUI: Return R1
    WebUI-->>User: Display R1

    Note over User,Checkpointer: Later in conversation...

    User->>WebUI: Question 2: "How is it performing?"
    WebUI->>LangGraph: invoke({messages: [Q2]}, thread_id="abc")
    LangGraph->>Checkpointer: Load state for thread "abc"
    Checkpointer-->>LangGraph: [Q1, R1] (context!)
    LangGraph->>Agent: Execute with [Q1, R1, Q2]
    Note over Agent: Agent sees Q1+R1 context<br/>understands "it" = portfolio
    Agent-->>LangGraph: Response 2 (contextual)
    LangGraph->>Checkpointer: Save state: [Q1, R1, Q2, R2]
    LangGraph-->>WebUI: Return R2
    WebUI-->>User: Display R2
```

---

## How to Use These Diagrams

### View Online
1. Visit https://mermaid.live/
2. Copy any diagram code above
3. Paste and view interactively
4. Can export as PNG/SVG

### View in VS Code
1. Install "Markdown Preview Mermaid Support" extension
2. Open this file
3. Use "Markdown: Open Preview" command
4. Diagrams render inline

### View in GitHub
- Mermaid diagrams render automatically in GitHub markdown

---

**Created:** 2026-01-17
**Tool:** Mermaid.js
**Total Diagrams:** 10
