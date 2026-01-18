# From Prompts to SOPs: The Rise of Intelligence Engineering

## Contact Me

- Blog: <https://cugtyt.github.io/blog/llm-application/index>
- Email: <cugtyt@qq.com>
- GitHub: [Cugtyt@GitHub](https://github.com/Cugtyt)

---

We've seen the evolution of how we work with large language models. First came **Prompt Engineering**—the art of crafting inputs to elicit better outputs. Then **Context Engineering** emerged—managing what information the model sees, when it sees it, and how it's structured. Now we're entering a new phase: **Intelligence Engineering**—the discipline of architecting agent systems that transform raw model reasoning into structured, repeatable, production-grade workflows.

As base models become increasingly powerful and commoditized, the differentiation shifts to the agent layer—how you structure intelligence for your specific use case.

The key insight is this: a model's intelligence is necessary but not sufficient for production deployment. A coding model can generate code. But to actually fix a bug in your codebase, following your team's conventions, respecting your security constraints, and validating against your test suite—that requires more than raw intelligence. It requires an **SOP (Standard Operating Procedure)**—a structured guide that tells the agent *how* to approach the task, what steps to follow, what constraints to respect, and how to know when it's done.

Intelligence Engineering is about designing these SOPs. It's the practice of encoding procedural knowledge into agent systems so that generic model capabilities become scenario-specific solutions. Different products implement SOPs differently—Claude calls them Skills, GitHub Copilot uses SKILL.md and agent.md files, Cursor has its own config formats—but they all serve the same purpose: guiding intelligence toward production-ready outcomes.

---

## Two Layers of Intelligence

When we talk about "AI intelligence" in production systems, we're really talking about two distinct layers:

### Model Layer: The Thinking Capability

The model layer is where raw intelligence lives. This is what the LLM provides:

- **Token generation**: Producing coherent text, code, or structured output
- **Reasoning**: Following logical chains, analyzing problems, considering alternatives
- **Knowledge retrieval**: Drawing on training data to inform responses
- **Pattern recognition**: Understanding context, intent, and domain-specific patterns

This layer is powerful but generic. A coding model trained on millions of repositories can write Python, debug JavaScript, and explain algorithms. But it writes "public knowledge" code—solutions that work in general but may not fit your specific situation.

### Agent Layer: The Doing Capability

The agent layer is where intelligence becomes actionable. This is what transforms a model into a production system:

- **Memory**: Maintaining context across interactions and sessions
- **Tools**: Accessing external systems—file systems, APIs, databases, terminals
- **Lifecycle management**: Knowing when to act, when to wait, when to ask for input
- **SOPs**: Following structured procedures to achieve specific outcomes

The agent layer doesn't add more "thinking"—it adds **structure** to thinking. It defines *how* the model's intelligence gets applied to real problems.

**The key distinction**: A model can write code. An agent with SOPs knows *how* to fix your specific bug in your specific codebase following your specific workflow.

---

## SOPs: The Core of Intelligence Engineering

An **SOP (Standard Operating Procedure)** is what tells an agent how to achieve a task. It's not separate pieces (tools, configs, instructions)—it's one cohesive procedure that combines all of them into actionable guidance.

Different products implement SOPs in different formats, but they all contain the same core components:

### Components of an SOP

| Component | What It Defines | Example |
|-----------|-----------------|----------|
| **Tool Definitions** | What actions are available | `read_file`, `edit_file`, `run_terminal`, `search_code` |
| **Workflow Logic** | How to sequence actions | "Read file → identify issue → propose fix → validate → apply" |
| **Instructions** | Domain guidance and constraints | Procedural steps, constraints, best practices |
| **Success Criteria** | How to know when done | "Tests pass, no new errors introduced, follows style guide" |

### Example: A "Bug Fix" SOP

```yaml
name: bug-fix
description: Fix a reported bug in the codebase

tools:
  - read_file      # Examine source code
  - grep_search    # Find related code and usages
  - get_errors     # Check current errors/warnings
  - edit_file      # Apply fixes
  - run_terminal   # Run tests and validation

instructions: |
  When fixing a bug:
  1. First understand the bug - read the error message, reproduce if possible
  2. Locate the source - search for related code, understand the context
  3. Identify root cause - don't just fix symptoms, find the actual problem
  4. Consider impact - check what else uses this code (list_code_usages)
  5. Propose minimal fix - change as little as necessary
  6. Validate - run tests, check for new errors
  7. If tests fail, iterate - don't stop until validation passes

constraints:
  - Never modify test files to make tests pass
  - Preserve existing code style and patterns
  - If fix requires architectural changes, stop and report

success_criteria:
  - Original error no longer occurs
  - All existing tests pass
  - No new errors introduced
```

This SOP encodes *how* to fix bugs—not just "write code that fixes it" but the complete procedure a skilled developer would follow.

---

## Intelligence Engineering in Practice

The clearest evidence for Intelligence Engineering is this: **the same base model behaves completely differently across different agent products**. Why? Because each product wraps the model in different SOPs.

GitHub Copilot uses SKILL.md and agent.md files. Claude Code has its Skills system with MCP (Model Context Protocol) for runtime injection—meaning new SOPs can be added on the fly without rebuilding the agent. Cursor uses .cursorrules for project-level guidance. Custom agents might use YAML or JSON workflow configs.

The implementation varies, but they're all doing the same thing: encoding procedural knowledge that tells the agent *how* to apply its intelligence to specific scenarios. A coding model is a coding model. What makes these products feel different isn't the model—it's the SOPs wrapped around it.

---

## From Generic Output to Production Solution

When you ask a model to "fix this bug," it draws on public knowledge—common patterns, general best practices, typical solutions. This produces *reasonable* output, but not necessarily *your* output. It might use a different style, miss your validation requirements, or skip your required review steps.

SOPs bridge this gap by encoding three critical elements:

**Constraints** (what NOT to do): Never commit directly to main, never bypass type checking, never include credentials in code.

**Procedures** (what MUST be done): Always run linter before proposing changes, always check for existing tests, always verify backward compatibility.

**Evaluation** (how to know when DONE): All tests pass, no new lint errors, type checking succeeds.

With SOPs, the agent doesn't just produce output that "works"—it produces output that follows your procedures, respects your constraints, and meets your evaluation criteria. Intelligence Engineering is about ensuring the agent works *your way*.

---

## The Intelligence Engineering Stack

Here's how all the pieces fit together:

```
┌─────────────────────────────────────────────────────────────┐
│           Scenario Requirements & Evaluation                 │
│     (What "success" means for this specific use case)       │
├─────────────────────────────────────────────────────────────┤
│              SOPs (Skills, agent.md, configs)                │
│     Tools + Instructions + Workflow + Success Criteria       │
│  (The complete procedure for achieving specific outcomes)   │
├─────────────────────────────────────────────────────────────┤
│                   Agent Runtime                              │
│           Lifecycle management, memory, tool execution       │
│     (The execution engine that runs SOPs)                   │
├─────────────────────────────────────────────────────────────┤
│                    Model Layer                               │
│         Token generation, reasoning, knowledge               │
│     (The raw intelligence that powers everything)           │
└─────────────────────────────────────────────────────────────┘
```

Each layer amplifies the one below:

- **Model Layer** provides reasoning capability
- **Agent Runtime** structures that reasoning into executable workflows—following a [standardized agent lifecycle](agent-gen) (conversation → LLM call → tool call → loop until done) that makes SOPs portable across implementations
- **SOPs** constrain and guide those workflows toward specific outcomes
- **Scenario Requirements** define what success looks like

Because the Agent Runtime follows a uniform pattern, SOPs can be written once and work across different agent products. The standardization at the runtime layer is what makes Intelligence Engineering scalable.

The gap between "impressive demo" and "production deployment" lives in the upper layers. Intelligence Engineering is the discipline of designing those layers.

---

## The Discipline of Intelligence Engineering

Intelligence Engineering treats SOPs as first-class engineering artifacts—regardless of whether they're implemented as Skills, agent.md files, or custom configs:

### Design

- Define clear SOPs for each task type
- Specify tools, instructions, workflows, and success criteria
- Consider edge cases and failure modes
- Choose the right implementation format for your platform

### Version Control

- SOPs should be versioned like code
- Changes to procedures should be reviewed
- Rollback capability when SOPs degrade performance

### Testing

- Test SOPs against representative scenarios
- Measure success rates, efficiency, quality
- Regression testing when SOPs or models change

### Iteration

- Observe agent behavior in production
- Identify where SOPs fail or underperform
- Refine procedures based on real-world feedback

---

## Conclusion

The evolution is clear:

| Paradigm | Core Question | Focus |
|----------|---------------|-------|
| **Prompt Engineering** | "What should I say to the model?" | Crafting inputs |
| **Context Engineering** | "What should the model know?" | Managing information |
| **Intelligence Engineering** | "How should the system behave?" | Designing SOPs |

We have powerful models. They can think, reason, and generate. But thinking isn't doing. The agent layer—through SOPs—bridges that gap.

Intelligence Engineering is the discipline of encoding procedural knowledge into agent systems. Whether you call them Skills, agent.md, .cursorrules, or something else—they're all SOPs. They're all ways of telling an agent *how* to apply intelligence to get real work done.

The model brings reasoning. The SOP brings the structure. Together, they solve production problems.