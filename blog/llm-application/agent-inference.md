# Agent Inference: The Shift from Model to Agent Optimization

## Contact me

* Blog -> <https://cugtyt.github.io/blog/index>
* Email -> <cugtyt@qq.com>
* GitHub -> [Cugtyt@GitHub](https://github.com/Cugtyt)

---

When we talk about AI inference today, we mostly mean **model inference**—the infrastructure for making LLMs fast and efficient. We discuss GPUs, KV cache optimization, transformer layers, batch processing, and frameworks like vLLM and SGLang. These are critical concerns for serving models at scale, and naturally, this is where the industry focus currently lies.

But as agents become the basic unit of AI applications—with standardized lifecycles and building practices—**the focus will shift to a higher abstraction layer**: **Agent Inference**.

Just as model inference sits above hardware and optimizes token generation, agent inference sits above model inference and optimizes agent behavior. This is the infrastructure layer that makes agents production-ready, reliable, and scalable. As the agent technology matures, this layer will become the primary engineering concern.

---

## Two Layers, One System

The AI inference stack has two distinct layers:

```
┌─────────────────────────────────────────────┐
│         Production Requirements              │
│    (What "working correctly" means)          │
├─────────────────────────────────────────────┤
│         AGENT INFERENCE LAYER                │
│  • Agent Role & System Prompts               │
│  • Skill Discovery & SOPs                    │
│  • Tool Discovery & Routing                  │
│  • Memory Management                         │
│  • Lifecycle Orchestration                   │
│  • Sub-Agent Delegation                      │
├─────────────────────────────────────────────┤
│         MODEL INFERENCE LAYER                │
│  • Token Generation                          │
│  • KV Cache Management                       │
│  • Batch Processing                          │
│  • Hardware Optimization (GPU/TPU)           │
│  • Request Scheduling                        │
└─────────────────────────────────────────────┘
```

**Model inference** focuses on making models fast:
- Throughput (tokens/second)
- Latency (time to first token, time per token)
- Hardware utilization (GPU memory, compute)
- Batch efficiency

**Agent inference** focuses on making agents work:
- Correctness (tasks completed successfully)
- Reliability (predictable behavior)
- Maintainability (SOPs as versioned artifacts)
- Observability (traceable decisions)

Both layers are essential. Fast token generation is useless if the agent can't complete tasks. Perfect task completion is impractical if it takes too long.

---

## Agents as Stateless Job Units

When agent inference becomes standardized, **agents transform into template-based, stateless job units**—similar to how containers standardized application deployment.

### The Standardized Agent Pattern

A standardized agent is:

1. **Template-based**: Generic agent spec that can handle a class of tasks
   - Agent role defining identity
   - System prompt defining behavior
   - Skill/SOP for domain expertise
   - Tool set for capabilities
   - Memory configuration
   - Success criteria

2. **Stateless**: Each invocation is independent
   - Task sent → Agent loop executes → Response returned
   - No persistent state between invocations (unless explicitly designed)
   - Clean lifecycle: start → process → complete

3. **On-demand**: Ready to trigger as long as a task is sent
   - Skills auto-discovered and loaded based on task context
   - Spins up, processes, returns result
   - Scales horizontally like serverless functions

4. **Uniform handling**: Standardized interface for all tasks
   - Input: Task description + context
   - Process: Agent loop (LLM call → tool call → continue/break)
   - Output: Result + execution trace

### Example: Code Review Agent as Job Unit

```yaml
agent_spec:
  name: "code-review-agent"
  type: "template"
  
  role: "code_reviewer"
  
  system_prompt: |
    You are a code review agent. For each code change:
    1. Check for syntax errors
    2. Verify test coverage
    3. Assess security issues
    4. Provide improvement suggestions
  
  skills:
    - name: "code-review-sop"
      version: "2.3"
      source: "mcp://skills/code-review"
    - name: "security-audit-sop"
      version: "1.5"
      source: "mcp://skills/security-audit"
  
  tools:
    - run_linter
    - run_tests
    - check_coverage
    - security_scan
  
  memory:
    type: "summary_based"
    context_window: 32000
  
  lifecycle:
    max_iterations: 10
    break_condition: "all_checks_complete"
```

**Usage**:
```python
# Agent is just a job unit waiting for tasks
result = agent_inference_runtime.invoke(
    agent="code-review-agent",
    task={
        "files": ["src/auth.py", "src/db.py"],
        "diff": "git diff HEAD~1"
    }
)

# Agent inference runtime handles:
# 1. Auto-discovers and loads relevant skills (code-review-sop, security-audit-sop)
# 2. Constructs dynamic context from skills + system prompt
# 3. Runs standardized agent loop:
#    - LLM reads diff with skill-enhanced context
#    - Calls run_linter tool
#    - Calls run_tests tool
#    - Calls check_coverage tool
#    - Calls security_scan tool
#    - LLM synthesizes results using skill guidelines
# 4. Returns review + trace

print(result.review)
print(result.execution_trace)
print(result.skills_used)  # Which skills were loaded
```

The agent has no memory of previous reviews. It's invoked, executes, returns results. **Stateless. Uniform. Ready.**

### Benefits of Standardization

When agents become standardized job units:

- **Scalability**: Deploy N instances, route tasks uniformly
- **Testability**: Same input always produces same behavior
- **Composability**: Chain agents like function calls
- **Observability**: Standard execution traces
- **Versioning**: Upgrade agent specs independently
- **Cost control**: Pay only for execution time
- **Skill reusability**: Share SOPs across different agents and teams
- **Dynamic adaptation**: Auto-discover and load relevant skills based on task context
- **Unified orchestration**: Main agents and sub-agents use the same infrastructure—no special cases

This is the **promise of agent inference as infrastructure**: agents become first-class job units in production systems, not ad-hoc scripts wrapped around model calls. The key differentiator is skill auto-discovery and dynamic context construction—agents adapt their expertise on-demand.

---

## The Core Components of Agent Inference

Agent inference requires infrastructure for six key areas:

### 1. Agent Role & Prompt Management

**Agent identity comes from the system prompt**. The prompt defines what the agent is ("You are a code review agent", "You are a data analyst") and how it behaves. Skills and tools provide capabilities, but the core identity is in the prompt. System prompts are configuration, not code. Agent inference engines must support:

- **Role definition**: Declarative agent identity
- **Runtime injection**: Load prompts from external sources (MCP-style)
- **Template rendering**: Construct prompts from task context
- **Factory generation**: Dynamically create prompts from requirements
- **Version control**: Track prompt changes, roll back

Example:
```python
# Agent inference engine resolves role and prompts at runtime
agent_runtime.load_agent_spec(
    agent_id="code-review-agent",
    role="code_reviewer",
    prompt_source="mcp://prompts/code-review/v2.3"
)
```

### 2. Tool Infrastructure & Distribution

Tools are the "hands" of agents. Tools will become standard distributable packages—this is a core area of agent inference.

**Tool registry and execution**:
- **Schema registration**: Declare available tools with types
- **Discovery**: Agents query tool registry
- **Routing**: Parse tool calls from LLM output
- **Execution**: Invoke tools and return results
- **Validation**: Ensure tool calls match schemas

From [agent-gen.md](agent-gen.md), the tool interface:
```python
Tool = {
    "name": str,
    "description": str,
    "parameters": Dict[str, Type],
    "execute": Callable
}
```

**Package-like distribution model**:

Just like npm packages, Python wheels, or Docker images, tools will become installable, versioned packages. Agent specs would reference tool packages:
```yaml
agent_spec:
  tools:
    - from: toolset://linters@3.2.1
      select: [run_pylint, run_prettier]  # Use subset
    - from: toolset://test-runners@latest
    - custom_tool  # Local tool
```

This enables dependency resolution, version management, and distribution through public registries, private repos, or enterprise marketplaces. Agent inference engines would handle the entire tool lifecycle—from package installation to execution.

### 3. Memory Orchestration

Agents need state management across invocations. Agent inference provides:

- **Conversation state**: Working memory for current task
- **Persistent memory**: Long-term storage (e.g., Git-based as in [git-context-memory.md](git-context-memory.md))
- **Context window management**: Stay within token limits
- **Memory isolation**: Sub-agents have independent context

**Example: Automatic summarization when threshold reached**
```python
# Agent inference runtime monitors conversation length
agent_config = {
    "memory": {
        "type": "conversation",
        "max_tokens": 30000,
        "summarize_threshold": 25000,  # Trigger summarization at 80% capacity
        "strategy": "auto_summarize"
    }
}

# During agent loop:
# Iteration 1-10: conversation = 15,000 tokens (normal operation)
# Iteration 11: conversation = 26,000 tokens (threshold exceeded)
#   → Runtime automatically calls summarize_messages tool
#   → Compresses messages 1-8 into single summary
#   → New conversation = 18,000 tokens (continues processing)
# Iteration 12-15: conversation stays under threshold
```

The agent inference layer **automatically manages memory**. Developers configure policies; runtime enforces them.

### 4. Lifecycle Orchestration

The **agent loop** is standardized infrastructure:

```
┌─────────────────────────────────────┐
│ 1. Receive Task                     │
├─────────────────────────────────────┤
│ 2. Load Agent Spec                   │
│    • Discover & inject skills        │
│    • Load system prompt + role       │
│    • Register tools                  │
├─────────────────────────────────────┤
│ 3. LLM Call (with role + prompt +   │
│    skills + conversation + tools)    │
├─────────────────────────────────────┤
│ 4. Parse Response                    │
│    • Text message? → Return          │
│    • Tool call? → Execute (goto 5)   │
├─────────────────────────────────────┤
│ 5. Execute Tool Call                 │
│    • Invoke tool function            │
│    • Capture result                  │
├─────────────────────────────────────┤
│ 6. Add Tool Result to Conversation   │
│    → Loop back to step 3             │
├─────────────────────────────────────┤
│ 7. Break Condition                   │
│    • No more tool calls              │
│    • Max iterations reached          │
│    • Success criteria met            │
├─────────────────────────────────────┤
│ 8. Return Result + Trace             │
└─────────────────────────────────────┘
```

From [agent-gen.md](agent-gen.md):
> The agent continues its loop if there's a tool call in the LLM response, and stops if there isn't.

Agent inference engines implement this loop as **first-class infrastructure**, not application code.

### 5. Sub-Agent Delegation

Complex tasks require task decomposition. **Sub-agents are just agents invoked through the same agent inference infrastructure**—there's no special "sub-agent" type. Agent inference provides:

- **Dynamic launching**: Main agent spawns other agents for subtasks using the same runtime
- **Context isolation**: Each agent (main or sub) has independent conversation
- **Result aggregation**: Sub-agent output becomes single message in main agent's conversation
- **Resource management**: Limit concurrent agents, set max iterations
- **Recursive composition**: Sub-agents can spawn their own sub-agents—all using the same infrastructure

From [context-offload-via-subagent.md](context-offload-via-subagent.md):
> Main agent dynamically generates task instructions → Sub-agent runs complete isolated lifecycle → Full sub-agent conversation compresses to single result message

**Key insight**: A "sub-agent" is simply another agent invocation. **They all share the same infrastructure, but can be configured differently**:

```python
# Main agent configuration
main_agent = {
    "role": "project_manager",
    "skills": ["task_decomposition@2.0"],
    "tools": ["create_subagent", "aggregate_results"],
    "memory": {"type": "persistent", "backend": "git"}
}

# Sub-agent 1: Code reviewer (different skills, tools, memory)
code_reviewer = {
    "role": "code_reviewer",
    "skills": ["code_review_sop@2.3", "security_audit@1.5"],
    "tools": ["run_linter", "run_tests", "check_coverage"],
    "memory": {"type": "stateless"}  # Different memory config
}

# Sub-agent 2: Test engineer (different configuration again)
test_engineer = {
    "role": "test_engineer",
    "skills": ["test_coverage_analysis@3.0"],
    "tools": ["pytest", "coverage_report", "mutation_testing"],
    "memory": {"type": "conversation", "max_tokens": 20000}
}
```

**Shared infrastructure** across all agents:
- Lifecycle orchestration (same agent loop)
- Tool registry (all tools available, agents select subset)
- Memory management primitives (different policies, same implementation)
- Skill discovery (same registry, different selections)
- Observability infrastructure (unified tracing)

**Different configurations** per agent:
- Role and system prompts (defines behavior)
- Skill sets (domain expertise)
- Tool sets (available actions)
- Memory policies (stateless vs. persistent, different thresholds)
- Resource limits (iterations, timeout, cost)

This unified-yet-configurable approach makes agent inference scalable—from one agent to hundreds of specialized sub-agents.

### 6. Skill Discovery & Distribution

**Skills** are containers for **SOPs (Standard Operating Procedures)**—the "programs" for agents. A skill packages domain expertise (instructions, workflows, tools, and success criteria) that agents load on-demand. Skills follow the same package distribution model as tools—this is a core area of agent inference.

Agent inference engines provide:

- **Skill registry**: Store SOPs as versioned artifacts
- **Runtime loading**: Inject skills based on task requirements (e.g., "code review skill", "data analysis skill")
- **Selection logic**: Choose appropriate SOP for current task
- **Composition**: Combine multiple skills for complex tasks
- **Skill marketplace**: Discover and install community-contributed skills

From [agent-intelligence-sop.md](agent-intelligence-sop.md):
> SOPs are first-class artifacts: Tools + Workflow + Instructions + Success Criteria

**Package distribution for skills**:

Skills would follow the same package distribution model as tools (see section 2), be installable and versioned, declare dependencies on other skills and toolsets, and be referenced in agent specs:

```yaml
agent_spec:
  skills:
    - code-review@2.3.0      # From registry
    - security-audit@1.5.0   # From registry
    - ./custom-sop.md        # Local skill
```

**Examples of skill systems**:
- Claude MCP: Skills injected at runtime based on context
- GitHub Copilot: SKILL.md files loaded per workspace for specialized workflows
- Cursor: .cursorrules as project-specific SOPs

---

## Agent Inference: Optimization and Production Concerns

Just as model inference optimizes token generation, agent inference optimizes task completion. But agent optimization is more complex—it must balance efficiency, reliability, observability, and cost.

### Parallel Concerns with Model Inference

| Model Inference | Agent Inference |
|----------------|----------------|
| **Batching**: Process multiple requests together | **Parallel tool execution**: Run independent tools concurrently |
| **Model routing**: Send requests to appropriate model | **Sub-agent routing**: Delegate subtasks to specialized agents |

### Efficiency: Agent-Specific Optimizations

**Model inference efficiency**: Tokens/second, GPU utilization  
**Agent inference efficiency**: Tasks/hour, context utilization, success rate

1. **Conversation Management**
   - Edit/delete messages to stay within context limits
   - Summarize long conversations (as shown in Memory Orchestration example)
   - From [conversation-manage.md](conversation-manage.md): edit_message, delete_message, summarize_messages

2. **Tool Call Efficiency**
   - Batch independent tool calls
   - Cache tool results for identical calls
   - Parallel execution where possible

3. **Context Compression**
   - Sub-agent offloading to isolate context
   - Git snapshots for long-term state
   - Selective message retention

4. **Validation Loops**
   - Factory → Runtime → Observer pattern from [agent-base.md](agent-base.md)
   - Iterative improvement based on success criteria
   - Process supervision: Design discussion → Implementation

### Observability: Tracing Agent Decisions

**Model inference traces**: Token generation, latency, throughput  
**Agent inference traces**: Decision rationale, tool calls, conversation flow, skill loading

Requirements:
- Conversation replay (inspect full message history)
- Decision trees (why did agent choose this tool? which skill influenced the decision?)
- Tool call logs (parameters, results, timing)
- Memory state inspection (what context was available?)
- Skill injection tracking (which SOPs were loaded and when?)

**Example trace output**:
```json
{
  "agent_id": "code-review-agent",
  "task_id": "review-123",
  "skills_loaded": ["code-review-sop:v2.3", "security-audit-sop:v1.5"],
  "iterations": 5,
  "tool_calls": [
    {"tool": "run_linter", "duration_ms": 340, "result": "3 issues"},
    {"tool": "run_tests", "duration_ms": 2100, "result": "all passed"},
    {"tool": "check_coverage", "duration_ms": 180, "result": "87%"}
  ],
  "memory_events": [{"type": "summarize", "iteration": 3, "tokens_saved": 8000}],
  "completion_status": "success",
  "total_duration_ms": 4500
}
```

### Reliability: Predictable Agent Behavior

**Model inference reliability**: Model availability, response consistency  
**Agent inference reliability**: Task success rate, predictable behavior, graceful degradation

Requirements:
- SOPs as tested artifacts (version controlled, regression tested)
- Success criteria validation (did agent actually complete task?)
- Error handling and retry logic (what happens when tool fails?)
- Graceful degradation (fallback strategies when skills unavailable)
- Skill version pinning (ensure consistent behavior across deployments)

### Cost Model: Multi-Dimensional Pricing

**Model inference costs**: Input tokens + output tokens  
**Agent inference costs**: (Multiple LLM calls × tokens) + tool execution + memory storage + sub-agent overhead + skill loading

Requirements:
- Budget constraints per task
- Cost tracking per agent invocation
- Tool execution pricing
- Sub-agent spawn limits
- Skill caching to reduce reload costs

---

## Agent Inference as Production Standard

As agent technology matures, **agent inference will become the primary engineering concern**—just as model inference is today for serving LLMs.

### The Evolution

**Phase 1 (Current)**: Ad-hoc agent implementations
- Every team writes their own agent loop
- Prompts hardcoded in application
- Tools tightly coupled to business logic
- No standard observability

**Phase 2 (Emerging)**: Standardized agent patterns
- Libraries like LangChain, AutoGen provide abstractions
- SOPs emerge as shareable artifacts (MCP, SKILL.md)
- Tool interfaces standardize
- Observability through logging

**Phase 3 (Future)**: Agent inference as infrastructure
- Agent inference engines (like vLLM for agents)
- Declarative agent specs (like Kubernetes manifests)
- Agents as stateless job units
- Production-grade observability, reliability, scalability

### Key Observations

As agent inference becomes production standard, several critical patterns emerge:

#### 1. Package Distribution as Core Infrastructure

As described in sections 2 and 6, the package distribution model for tools and skills is **the defining characteristic** of mature agent inference. This creates network effects: as more skills are packaged and shared, every agent becomes more capable. The ecosystem compounds—much like npm transformed JavaScript development, agent inference will create a marketplace of reusable capabilities where domain experts package their expertise for millions of agents.

#### 2. Unified Infrastructure with Configurable Specialization

**All agents share the same infrastructure, but configure it differently**. This is the key to scalable agent orchestration:

- **Shared**: Lifecycle engine, tool registry, memory primitives, skill discovery, observability
- **Configured**: Role, skill sets, tool sets, memory policies, resource limits

A project manager agent and a code reviewer agent run on the same runtime—they just load different configurations. Sub-agents aren't special; they're just agent invocations with different specs. This unified-yet-configurable model is what makes agent inference scalable from 1 agent to 1000+ concurrent agents.

### Why This Matters

As agent inference standardizes:

1. **Infrastructure commoditization**: Agent loops, tool routing, and conversation management become standard—developers focus on SOPs and task design
2. **Ecosystem acceleration**: Skill marketplaces emerge, enabling capability sharing at scale
3. **Production simplification**: Deploy agent specs like Kubernetes manifests—scale horizontally, monitor uniformly

---

## Conclusion

As agents become the basic unit of AI applications—standardized, stateless, ready-to-trigger job units—infrastructure will evolve to treat agent inference as a first-class concern:

- **Agent roles** as declarative identity
- **System prompts** as configuration
- **Skills (SOPs)** as loadable domain expertise
- **Tools** as registered capabilities
- **Memory** as managed state
- **Lifecycles** as orchestrated processes
- **Sub-agents** as delegated tasks

The infrastructure exists in pieces across different frameworks today. As the agent ecosystem matures, we'll see **convergence and unification**: agent inference engines that provide production-grade runtime for agents, just as vLLM and SGLang provide for models. This is the same transformation that containers brought to application deployment—**agent inference will be the Kubernetes moment for AI agents**.

**The focus will naturally shift from model inference to agent inference**—not because model inference isn't important, but because it becomes commoditized infrastructure while agent inference becomes the differentiator. Model inference makes models fast. Agent inference makes agents work. Both are essential, but as agent technology matures, optimizing agent behavior becomes the primary engineering concern.

The intelligence is in the model, the capability is in the agent, and the production readiness is in the agent inference layer.

---

## References

From this blog series:

- [agent-intelligence-sop.md](agent-intelligence-sop.md): Intelligence Engineering and SOPs as first-class artifacts
- [agent-gen.md](agent-gen.md): Standardized agent lifecycle (message types, tool interface, agent loop)
- [agent-base.md](agent-base.md): Factory → Runtime → Observer pattern
- [context-management.md](context-management.md): Three-tier memory strategy
- [git-context-memory.md](git-context-memory.md): Git as persistent memory backend
- [context-offload-via-subagent.md](context-offload-via-subagent.md): Sub-agent delegation for context isolation
- [conversation-manage.md](conversation-manage.md): Real-time conversation optimization tools
- [agent-three-stage.md](agent-three-stage.md): Agent evolution stages
