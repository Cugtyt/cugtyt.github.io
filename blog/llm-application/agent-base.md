# AgentBase: Designing a Full-Agent Lifecycle with Factory, Runtime, and Observer

Agent systems become easier to reason about when we break them into clean, reusable stages. Building on the ideas from “LLM Generates Tokens, Agent Generates Messages, AgentLauncher Generates Agents,” this post introduces **AgentBase**: a three-stage design pattern that stretches from agent creation to performance evaluation and back again.


## Why AgentBase?

Modern AI projects cycle continually through ideation, deployment, and refinement. AgentBase formalizes that loop so teams can:

- Swap in new components without rewriting the entire stack.
- Capture consistent telemetry for evaluation and iteration.
- Push changes confidently because every stage exposes stable interfaces.

The key insight is to treat every agent as the product of three collaborating roles:

1. **AgentFactory** – constructs a runnable agent workflow from specs.
2. **AgentRuntime** – executes the workflow on a concrete task input.
3. **AgentObserver** – scores the outcome and feeds improvements back into the factory.


## Key Artifacts

Before drilling into each stage, we anchor the conversation around three core artifacts.

### Agent Workflow Spec (Factory Output)

The factory produces a structured blueprint that downstream stages can execute without guessing. At minimum it should capture:

- **System prompts** – Behavioral guardrails, persona, policy statements, and input contracts.
- **Tool list** – Names, descriptions, schemas, and budgets for every callable tool.
- **Runtime config** – Static settings such as max steps, trace verbosity, memory strategy, and required measurement hooks.

The spec itself should be serialized as YAML or JSON so runtimes can consume it directly without bespoke parsers.

### Runtime Execution Record (Runtime Output)

While running a task, the runtime packages everything the observer (and future humans) need to understand what happened:

- **Task input** – The exact payload.
- **Conversation trace** – Ordered system/user/assistant messages, plus tool call and result messages.
- **Final output** – The answer delivered back to the caller, including confidence or reasoning fields if produced.
- **Telemetry** – Token counts, timing breakdowns, budget usage, and any custom metrics requested by the measurement plan.

This record becomes the observer’s raw material and feeds future rounds back in the factory.

### Observer Report (Observer Output)

The observer evaluates the runtime record using the agreed measurement plan and emits:

- **Task input** – Echoed from the runtime record for alignment.
- **Task output** – The final answer (or answers) under review.
- **Measurement report** – Scores, pass/fail verdicts, and narrative feedback derived from the measurement plan.

This report becomes both the artifact presented to stakeholders and the feedback payload that the factory can ingest for iterative improvement.


## Flow of Inputs and Artifacts

With those artifacts defined, the AgentBase contract expects the following baseline inputs:

- **Task description** – What the agent must accomplish and any operating constraints.
- **Test task inputs** – Concrete sample prompts, datasets, or API requests to try.
- **Optional test outputs** – Ground-truth responses, if you have them.
- **Measurement plan** – Qualitative or quantitative criteria to judge success.

Every stage adds to or transforms this information:

| Stage            | Consumes                                                | Produces                                   |
| ---------------- | ------------------------------------------------------- | ------------------------------------------ |
| AgentFactory     | task description, test inputs, optional outputs, measurements, optional previous report | Agent spec (workflow + configuration)     |
| AgentRuntime     | agent spec, real task input                             | Task output plus execution trace           |
| AgentObserver    | agent spec, task description, task input, task output, measurement plan | Performance report with improvement hints |

When improvements are needed, the observer’s report travels back to the factory as an extra input, and the loop iterates.


## Stage 1: AgentFactory

An AgentFactory instance starts life with its own system prompt that states the factory’s charter: absorb the task brief, resist overfitting to narrow examples, and emit a reusable agent workflow spec. With that context in place, the factory executes a predictable loop:

1. **Ingest** the task description, representative inputs, optional outputs, measurement criteria, and any prior observer report.
2. **Synthesize** an agent system prompt that encodes task goals, safety and policy constraints, and the expected shape of raw string inputs and structured outputs.
3. **Assemble** the tooling roster and runtime configuration needed to execute the prompt reliably.

The resulting specification typically bundles:

- **System prompt(s)** controlling high-level behavior, including explicit input and output expectations so runtime parsing stays consistent.
- **Tooling manifest** detailing allowed tools, schemas, budgets, and auth requirements.
- **Routing logic** that chooses between sub-agents or modes.
- **Runtime configuration** such as max steps, retry policies, temperature, and streaming preferences.

Inputs can include the observer’s last report. If a previous iteration flagged slow tool calls or low accuracy, the factory bakes new heuristics or alternative tool selections into the next spec.

> *Think of the factory as a compiler: it ingests requirements and diagnostics, then outputs an optimized agent blueprint.*


## Stage 2: AgentRuntime

AgentRuntime owns execution. It consumes the factory artifacts wholesale—system prompts, tool manifests, runtime configuration—and spins up a real agent ready to process any task input. Unlike the factory’s sample-based view, the runtime must accept the **entire** task payload, performing any required pre-processing before handing it to the agent loop. A typical cycle looks like:

1. **Instantiate** the agent per the spec, wiring in prompts, tools, and runtime configuration.
2. **Feed** the full task input into the conversation (optionally in parallel when multiple inputs arrive), initializing system/user messages accordingly.
3. **Execute** the iterative loop, orchestrating LLM calls and tool invocations as defined.
4. **Capture** the conversation trace, final output, and real-time metrics (token usage, latency, cost), packaging them into the runtime execution record.

Runtime does not judge quality—that’s the observer’s job. Its responsibility is fidelity: the trace must capture enough detail to reproduce decisions later and support parallel task handling when needed.

## Stage 3: AgentObserver

AgentObserver closes the loop. It ingests the agent spec, task description, and the full runtime execution record (task input, conversation trace, outputs, telemetry) alongside the user-provided measurement plan, then analyzes every detail strictly along the dimensions that plan specifies—nothing more, nothing less.

Observer deliverables:

- **Performance report** – A structured artifact summarizing metrics, verdicts, and notable events (e.g., “Tool X failed twice before succeeding”).
- **Improvement hints** – Prioritized suggestions: swap tools, adjust prompts, tighten guardrails, expand memory, etc.
- **Scorecards** – Optional aggregated dashboards for cross-agent comparisons.

The report flows back to the factory. Depending on its feedback, the next iteration could refine prompts, add fallback strategies, or even escalate to a human review step.


## The AgentBase Feedback Loop

```
task description + measurement plan
            ↓
       AgentFactory
            ↓ (agent spec)
       AgentRuntime
            ↓ (outputs + trace)
       AgentObserver
            ↓ (performance report)
        ┌──────────────┐
        │  Improve?     │
        │   Yes → back  │
        │   No  → ship  │
        └──────────────┘
```

Key properties:

- **Iterative** – Each pass tightens the agent’s behavior.
- **Composable** – Swap factories, runtimes, or observers without rewriting others.
- **Transparent** – Observer trace makes debugging and audits straightforward.

## Practical Tips

- **Version everything** – Keep specs, prompts, and measurement plans under version control so each report references the exact artifacts used.
- **Start narrow** – Pilot the Observer with a single measurement dimension before expanding to multi-faceted evaluation plans.
- **Automate the loop** – Pair AgentBase with CI jobs that rerun the Factory Runtime Observer pipeline nightly using fresh test inputs.
- **Expose a CLI** – Offer `agentbase factory`, `agentbase run`, and `agentbase observe` commands so developers can iterate locally.


## Wrapping Up

AgentBase reframes “build an agent” as “design a loop.” By separating **creation**, **execution**, and **evaluation**, you gain:

- Faster iteration cycles with clarity on failure modes.
- Modular components that can be upgraded independently.
- Auditable performance reports that support compliance and tuning.

Whether you’re orchestrating a single assistant or a fleet of specialized agents, this pattern keeps every improvement grounded in data and structured feedback. Ready for the next turn? Feed the observer’s report back into the factory and keep the loop spinning.
