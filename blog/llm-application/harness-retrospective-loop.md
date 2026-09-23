# A Repository Harness That Learns From Its Traces

A user asks a coding agent to add reservation cancellation. The patch passes
the available tests. The user then replies: “I can cancel someone else's
reservation.” The test result and the user's experience disagree. To improve
the next task, we need both signals: the conversation identifies the missing
behavior, while the execution trace may show why the agent missed it.

A coding harness helps an agent solve the task in front of it. It supplies the
model, tools, skills, instructions, and execution environment. As the agent
works, the harness produces a trace: what it saw, which tools it used, where
it struggled, and what it delivered. The user's subsequent messages provide
another signal: whether the result helped, needed correction, or led to a new
request.

Together, the trace and user feedback can do more than help debug one task. A
second, slower loop can study many tasks, identify a recurring cost, and propose
a change to the harness itself. This is a practical starting point for the [harness RSI](/blog/llm-application/harness-rsi)
idea: begin with a working harness, then let evidence from repository work guide
its evolution.

The design has two loops. The **foreground loop** serves the user's current
request. The **background retrospective loop** improves the system that will
serve later requests. The retrospective is itself a repository-owned skill and
set of tools, so it can eventually be improved through the same process.

```text
FOREGROUND                          BACKGROUND
user task                            trigger
   |                                    |
   v                                    v
current harness + model          select traces + feedback
   |                                    |
   v                                    v
result + trace + user reply      diagnose recurring friction
   |                                    |
   +---------- evidence -------------->+
                                        |
                                        v
                                 propose candidate commit
                                        |
                                        v
                                 compare with current commit
                                   /              \
                              adopt            reject
                                |                 |
                                v                 v
                         next foreground     retain evidence;
                         runs use it         keep current version
```

The background loop does not need to interrupt the foreground task. It can run
when a human requests a review, enough comparable tasks have accumulated,
conversation feedback reveals a recurring problem, or a new model or tool makes
an old procedure worth reconsidering.

## Start With a Versioned Harness

Suppose we use DeepSeek Harness (DSH) as the runtime. Its [plugin architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
lets a profile compose tools and other capabilities from bundles. DSH can also
[load skills from the repository](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md).
The repository would own its intended profile configuration, skills, tool
plugins, retrospective procedure, and evaluation cases. The DSH version and
plugin dependencies would be pinned so a Git commit identifies the harness we
intended to run.

The first version can be basic. It needs to complete ordinary repository tasks,
record a useful trace, and run the project's existing checks. It does not need
an optimizer or a plugin for every possible failure. The retrospective should
earn each addition by finding a concrete need.

Git gives each candidate a precise identity. A change to a skill, plugin, or
profile is a new harness commit. A rejected candidate remains an experiment;
the previous commit remains active. An accepted candidate becomes the version
used for subsequent work. This also makes removal a normal improvement: a
later commit can delete an instruction or plugin that no longer helps.

An experiment records two Git identities. The **task starting commit** fixes
the application's state before the user task. The **harness commit** fixes the
skills, plugins, and configuration used to do that task. For example:

```text
Task: add reservation cancellation
Application starting commit: A

Run 1: application A + current harness H1   -> result and user feedback
Run 2: application A + candidate harness H2 -> result and user feedback
```

Both agents must start with the same application files at `A`; the model and
evaluation criteria should also stay fixed. If the harness lives inside the
application repository, `H2` can be a commit that changes only harness files.
The application files in the `H1` and `H2` checkouts must still match `A`.
Otherwise, an apparent improvement might come from code changed between runs
rather than from the harness candidate.

## Keep Traces Outside the Versioned Repo

DSH's [session log](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/session.md)
is an append-only record of model-visible history, tool calls and results, and
turn and step events. Its [persistence backend](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-persistence-jsonl/README.md)
can store each session under a configured root directory. Those logs may be
large and may contain prompts, file contents, and command output. They are
evidence for the retrospective, but they need not be committed with the harness
code. The trace store should survive checkouts, candidate experiments, and
rollback.

Every foreground run needs a small record connecting its execution to its
result:

```text
run ID and task ID
task starting commit and harness commit
DSH version, model, and relevant configuration
session ID or trace location
follow-up message IDs and their relationship to the result
checks performed and their results
explicit acceptance, rejection, correction, or unresolved outcome
```

The session log tells us what the agent did. The user's messages help explain
whether that work met their intent and how much correction it required. Neither
should stand in for the other. A passing command does not establish that the
user got the right result; a negative comment alone does not explain which
part of the harness contributed to the problem.

The retrospective can start from compact run records and open full traces only
for promising or contradictory cases. It should retain links to the original
evidence so a diagnosis remains reviewable. It also needs a consistent policy
for retention and access because raw traces can contain sensitive material.

## Read the Conversation as Feedback

User feedback is a primary input to the retrospective, not an annotation added
after technical metrics. A user might say “this is wrong,” point out a missing
requirement, ask for a substantial rework, accept the result, or continue with a
related request. The background loop should connect those messages to the
result they address, even when they arrive after the original DSH session or in
a different conversation. A task or run ID provides that link.

The interpretation needs care. “You missed the cancellation case” is strong
evidence of a gap in that result. “Now add cancellation” may introduce new
scope rather than reveal a failure. Continued conversation by itself is
ambiguous; silence does not establish acceptance. Praise can indicate value,
but it does not prove that every contract was met. Store the message reference,
the inferred signal, and the reason for that inference so a reviewer can
correct it. Leave uncertain outcomes marked as uncertain.

This creates two complementary views of a run:

| Evidence | What it can reveal |
| --- | --- |
| User messages and corrections | Whether the result served the user's intent, what was missing, and how much rework followed |
| Execution trace and checks | Which actions, tools, instructions, or missing information may explain that outcome |

The retrospective should look for a connection between the two. A repeated
tool failure may be cheap and harmless; a single misunderstood requirement may
cost the user substantial time. Conversely, repeated wasted searches can be a
good improvement target even when users accept the final result. Neither signal
should be discarded because the other looks good.

## Give the Background Loop Two Phases

The structure resembles background memory generation: experience from earlier
interactions is processed after the immediate work and made useful later. Here
the output goes a step further. The retrospective can propose a new version of
the system that handles future work.

**Phase 1: extract experience.** Join traces to subsequent user messages and
outcomes, distinguish corrections from new requests, group comparable tasks,
and look for repeated costs: missed constraints, redundant searches, ineffective
checks, excessive tool use, or instructions that a newer model no longer needs.
Successful tasks and positive feedback also matter. They can reveal a reusable
method or show that an existing intervention has become unnecessary.

The output of this phase is a small set of evidence-backed hypotheses, not a
list of complaints. For each hypothesis, the retrospective should identify the
runs that support it, the likely mechanism, its frequency and impact, and cases
that might contradict it. The highest-value target is the one with a plausible
intervention whose expected benefit justifies building and maintaining it.

**Phase 2: propose and test one change.** Choose an editable surface: a skill,
tool, plugin, configuration, check, or part of the retrospective itself. State
what should improve and what must not regress. Make the candidate on its own
Git commit and compare it with the current harness on fresh executions from
comparable task starting states. Record the results whether the candidate wins
or loses.

A background runner can trigger the retrospective skill and provide tools for
selecting runs, reading traces, creating an isolated candidate, and running the
comparison. The skill defines the method; the runner controls when it executes.
A failed candidate ends that experiment. Its evidence can inform a later cycle
without repeatedly applying the same unsuccessful fix.

## A Repository Example

Return to the cancellation task. The user's correction identifies an ownership
rule the result violated. Other tasks show similar corrections after changes
to booking endpoints. The traces show that agents read the endpoint code and
ran its local tests, but did not open the authorization spec in another
directory. The conversation tells the retrospective what mattered to users;
the traces narrow the possible explanation.

The retrospective first tests its diagnosis. Is the authorization spec absent,
difficult to find, or available but ignored? If discovery is the problem, it
may propose a plugin that links changed booking code to relevant specs and
validation commands. If the spec was already in the agent's context, another
retrieval tool may only add cost; a review procedure change may be the better
experiment.

Run the current and candidate harnesses on comparable tasks, including cases
outside the examples that inspired the plugin. Check whether they find known
violations, complete ordinary tasks, and reduce human correction. Also compare
time and token cost. If the plugin makes reviews faster but causes agents to
treat an incomplete link map as exhaustive, reject it. Keep the trace and
result of that failed experiment so the next retrospective can refine the
diagnosis.

If it succeeds, adopt the plugin commit. Later, a model upgrade or better
repository search may make the plugin redundant. The retrospective can compare
the harness with and without it under the new model and propose a deletion.
An evolving harness needs this ability to get smaller as well as larger.

## Keep Acceptance Independent

The improver should not decide that its own proposal worked simply because it
can explain the proposal convincingly. Fix the comparison criteria before the
candidate run. Use checks and task outcomes that do not depend on the candidate
plugin's own report. Review changes to evaluation criteria separately from the
change they would evaluate.

The background loop should leave a record of its own decisions: which runs it
selected, why it chose the target, the candidate and baseline commits, the
comparison results, and the adopt or reject decision. Its proposals can be
judged over time. If it repeatedly chooses low-value targets or expensive
experiments, its selection skill or evaluation tools become improvement targets.

This is the recursive part of the design. Foreground traces help improve the
working harness. Background traces help improve the mechanism that proposes
those changes. Git commits and retained experiment evidence let both loops
advance without losing the ability to explain or reverse a decision.

## Begin With One Complete Cycle

The smallest useful implementation is a working DSH profile, a durable session
store, a way to link later user feedback to each run, a repository-owned
retrospective skill, and a way to compare one candidate commit with the current
harness. A scheduled service, automated promotion, and a large plugin catalog
can wait until the first cycle demonstrates value.

The first milestone is not a harness that changes itself without supervision.
It is a harness that can observe its work, identify one worthwhile change,
test that change against its current version, and keep or discard it based on
evidence. Repeating that cycle turns repository experience into a continuously
reconsidered working system.
