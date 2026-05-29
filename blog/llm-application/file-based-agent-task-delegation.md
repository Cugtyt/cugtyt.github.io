# File-Based Orchestration for AI Agent Delegation

When delegating work from one AI agent to another, the hard part is often not
the task itself. The hard part is coordination.

The delegating agent needs to describe the task clearly.
The delegated agent needs to understand the boundary.
Progress needs to be visible.
The final result needs to be auditable.
And the delegating agent still needs to verify the result before trusting it.

A useful pattern for this is file-based orchestration.

Instead of treating delegation as a transient prompt exchange, represent each
delegated task as a single Markdown task file.

## The Problem With Prompt-Only Delegation

A prompt-only delegation flow is easy to start, but harder to audit.

The delegating agent sends instructions to another agent, waits for a
response, and then tries to decide whether the response is useful.

This works for simple cases, but it has several weaknesses:

- the original task may be hard to recover later
- progress is not naturally visible
- constraints may be buried in a long prompt
- the final answer may be disconnected from the original requirements
- retries and verification become harder to reason about

This becomes more important when the delegated agent is weaker or more
execution-focused. Such agents benefit from a smaller, more explicit
protocol.

## The Core Pattern

Use one file per delegated task.

The file is both the input and the output:

```markdown
---
status: created
cwd: /path/to/workdir
---

# Task

Describe the bounded task.

# Constraints

Describe exactly what the delegated agent may inspect or modify.

# Expected Result

Describe the required result format.

# Validation

Describe how the delegating agent will verify the result.

# Execution Report

- created: task prepared by the delegating agent.

# Final Result

pending
```

The delegated agent reads this file, performs the task, updates progress in
the same file, and writes the final result back into it.

There is no separate task JSON, no separate progress log, and no separate
result file.

The task file is the contract.

## Why One File Works Well

A single task file gives both agents one shared source of truth.

It contains:

- what to do
- where to work
- what is allowed
- what output is expected
- how the result will be verified
- what happened during execution
- what the final result was

This reduces coordination overhead. The delegated agent does not need to
remember multiple artifact paths or synchronize state across files. It only
needs to update the task file.

That matters because delegation protocols should be simpler than the task
being delegated.

## The Task File as an Audit Trail

The task file also becomes a lightweight audit trail.

During execution, the delegated agent appends progress:

# Execution Report

- created: task prepared by the delegating agent.
- running: inspected the allowed files.
- complete: wrote final result.

At the end, it writes a compact result:

# Final Result

Verdict: The implementation matches the documented behavior.

Evidence:
- file_a.go:42 shows the boundary check.
- file_b.go:88 handles the error path.

Notes For Validation:
- Spot-check the cited lines.
- Inspect the diff before accepting the result.

[delegated-task-done]

This makes the result easier to review because the original task, execution
notes, and final answer live together.

## Constraints Are the Boundary

The most important section is Constraints.

The delegating agent should make boundaries explicit.

For read-only work:

# Constraints

- Do not modify any files other than this task file.
- Read only the files listed in the task.
- Do not inspect secrets, credentials, private keys, tokens, or environment
files.

For edit work:

# Constraints

- You may modify only:
  - this task file
  - the explicitly named target file
- Do not modify any other files.
- Apply only the listed edit steps.
- Do not refactor unrelated code.

This avoids relying on implicit modes like “inspect” or “edit”. The file
itself defines what is allowed.

## Keep the Launcher Simple

A launcher can be used to start the delegated agent from a task file, but it
should stay boring.

Its responsibilities should be limited to:

1. locate or receive the task file
2. read the working directory from the frontmatter
3. start the delegated agent in that directory
4. inject the task-file protocol into the prompt

The launcher should not decide whether the task succeeded.
It should not validate the result.
It should not manage complex lifecycle state.

Validation belongs to the delegating agent.

## Validation Remains Mandatory

Delegation does not remove responsibility from the delegating agent.

After the delegated agent finishes, the delegating agent must verify the
result before using it.

Depending on the task, validation may include:

- reading the final result
- checking cited files and line numbers
- inspecting the diff
- confirming only allowed files changed
- running focused tests
- checking command output
- deciding whether the answer is specific enough to trust

The delegated agent can collect evidence, but the delegating agent must judge
it.

## Clean Up After Verification

Once the result has been verified and summarized, the task file can be
deleted.

Task files are useful during orchestration and audit. They do not need to
become permanent records unless there is a specific reason to keep them.

This keeps the task directory clean and ensures outstanding files represent
active or unverified work.

## The Practice

The full practice looks like this:

1. The delegating agent writes one Markdown task file.
2. The delegated agent reads the task file.
3. The delegated agent updates progress in the same file.
4. The delegated agent writes the final result in the same file.
5. The delegating agent validates the result.
6. The delegating agent deletes the task file after verification.

The result is an async delegation workflow with very little machinery.

The key idea is simple: use the filesystem as the coordination layer, and
make the task file the contract.
