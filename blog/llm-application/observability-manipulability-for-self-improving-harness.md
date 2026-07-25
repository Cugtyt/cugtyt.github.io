# Observability and Manipulability: The Eyes and Hands of Self-Improving Harnesses

> **The core work of designing a self-improving harness is defining its
> observation and manipulation interfaces.** Observability lets the improvement
> mechanism find the right target. Manipulability gives it an action space in
> which to make a bounded change.

## A Personal Case: A Retrospective Skill for Codex

One self-improvement system I use is a retrospective skill for my Codex
experience. It reviews recent Codex threads and investigates repeated
behaviors, errors, and patterns. Its purpose is not merely to summarize past
work. It uses those records to improve the next period of work.

The loop is:

```text
        ┌──────────────────────────────────────────────┐
        │                                              │
        v                                              │
recent Codex threads
        |
        v
find repeated behaviors, errors, and friction
        |
        v
identify a concrete improvement target
        |
        v
build or refine a skill, script, or tool
        |
        v
use it in the next period of Codex work
        |
        v
collect new threads for the next retrospective
        |
        └──────────────────────────────────────────────┘
```

The retrospective skill is itself an improvement mechanism—a policy operating
at a slower time scale than the individual Codex agent. The working agent
handles today's task. The retrospective agent studies a period of experience
and changes the system that will handle tomorrow's tasks.

This case makes the role of observability clear. The retrospective needs access
to the data record: not only final answers, but enough of the thread history,
tool interactions, errors, corrections, and user feedback to recognize a
pattern. Without that access, it lacks the context needed to locate the
improvement target. It can only guess from isolated outcomes.

It also makes manipulability concrete. After finding a repeated pattern, the
retrospective needs a defined scope in which it can act. It may turn a repeated
manual procedure into a script, package a successful workflow as a skill, add a
tool that exposes missing information, or refine an instruction that repeatedly
caused confusion. This scope tells the retrospective what kinds of improvements
are possible.

Without observability, the retrospective does not know **what should be
improved**. Without manipulability, it does not know **how improvement can be
expressed**.

The most valuable output is therefore not a general comment such as “Codex
should be more careful.” It is a grounded and actionable transformation:

```text
observed recurring pattern
        +
identified causal mechanism
        +
editable harness surface
        =
concrete improvement target
```

For example, if multiple threads show the same lengthy manual inspection
sequence, the target may be a reusable script. If they show repeated loss of a
repository-specific constraint, the target may be a skill or persistent
instruction. If failures repeatedly lack diagnostic evidence, the first target
may be a new observation tool rather than a behavioral rule.

This last case is important: sometimes the system's first improvement is to
improve its own observability. Better traces create better future improvement
targets.

## From a Personal Workflow to a Harness Principle

Recent discussions of [Heuristic Learning](https://trinkle23897.github.io/learning-beyond-gradients/)
and [harness engineering for self-improvement](https://lilianweng.github.io/posts/2026-07-04-harness/)
describe an important shift in how AI systems can improve. The object being
updated no longer has to be model weights. An agent can improve the software
around a model: prompts, tools, workflows, context management, memory,
permissions, evaluators, tests, and scripts.

This creates a practical path to self-improvement. A capable model can inspect
the behavior of an agent system, identify a recurring weakness, modify the
harness, and evaluate the next version. But the model's intelligence is only
one part of this loop. A system cannot improve what it cannot observe, and it
cannot act on what it is not able to manipulate.

The central idea of this post is:

> **The core work of a self-improvement harness is defining the observation and
> manipulation interfaces. The observation interface determines whether the
> improvement mechanism can discover a target. The manipulation interface
> determines whether it has an action space for changing that target.**

These are the eyes and hands of a self-improving harness.

## A Control-Loop View of Harness Improvement

The self-improvement loop resembles reinforcement learning, but the mapping
needs to be made carefully:

| Control-loop concept | Harness self-improvement |
| --- | --- |
| Environment | Tasks, users, repositories, tools, runtime, and their evolving state |
| Observation | Threads, traces, logs, test results, artifacts, feedback, and summaries exposed to the improver |
| Policy | The model and improvement procedure that decide what should change |
| Action space | The harness surfaces the improver is permitted and equipped to modify |
| Action | A particular edit to a prompt, skill, script, tool, workflow, memory rule, or evaluator |
| Feedback | Evaluation of the changed harness on later tasks and regressions |

Observability is not the environment itself. It is the interface through which
the policy sees the environment. Manipulability is not one action. It defines
the available action space.

We can express one iteration as:

```text
        ┌──────────────────────────┐
        │                          │
        v                          │
experience records
        |
        v
observation interface
        |
        v
improvement policy
        |
        v
bounded manipulation
        |
        v
new harness version
        |
        v
evaluation and new experience
        |
        └──────────────────────────┘
```

If the harness at time `t` is `H_t`, the observation interface produces a
representation `o_t` from its experience records. The improvement policy uses
that representation to select an action `a_t` from the allowed action space.
Applying the action produces `H_(t+1)`, which is then evaluated:

```text
o_t       = Observe(records(H_t))
a_t       = Improve(o_t, H_t), where a_t belongs to AllowedActions(H_t)
H_(t+1)   = Apply(H_t, a_t)
feedback  = Evaluate(H_(t+1), H_t)
```

This formulation separates four questions that are often mixed together:

1. What happened?
2. Why did it happen repeatedly?
3. What part of the harness could address it?
4. Did the proposed change actually improve future behavior?

The first two depend on observability. The third depends on manipulability. The
fourth depends on evaluation.

## Observability: Finding the Improvement Target

A final success or failure signal is rarely enough for improvement. Suppose an
agent times out on several coding tasks. The timeout tells us the outcome, but
not the mechanism. The agent may have searched the wrong directory, repeatedly
opened the same files, waited on a blocked command, lost the task constraints
after context compaction, or simply attempted a task that exceeded its budget.
These cases share a terminal symptom but require different improvements.

Useful observability therefore exposes more than outcomes. It should help the
improvement mechanism reconstruct the causal path:

- What task and constraints did the agent receive?
- What context was available at each decision?
- Which tools did it call, with what results?
- Where did it retry, backtrack, or stall?
- Which assumptions were correct or incorrect?
- What feedback did the user provide?
- Does the same behavior occur across multiple threads?

The goal is not to collect the largest possible log. A huge unstructured
transcript can be technically accessible but practically unobservable. The
improver also needs ways to search, group, summarize, compare, and trace the
records. Good observability turns raw history into evidence from which a stable
improvement target can be identified.

This is especially important because one failure does not necessarily justify
a harness change. It may be a rare task, a temporary external error, or an
appropriate tradeoff. Repeated behavior across multiple experiences is a
stronger signal. Historical records let the improvement policy distinguish a
systematic weakness from a one-off event.

## Manipulability: Defining the Action Space

Once the improver finds a target, it needs to know what it can change.
Manipulability is the explicit surface through which the harness can be
modified.

For a coding agent, that surface might include:

- system instructions and repository guidance;
- reusable skills and standard operating procedures;
- scripts for repeated deterministic work;
- tool definitions and tool-selection rules;
- context retrieval, summarization, and memory policies;
- workflow control, retry logic, and stopping conditions;
- evaluation cases, regression tests, and acceptance checks.

Making a surface manipulable involves more than granting write permission. The
surface needs a legible structure, a defined scope, and a way to validate the
result. A monolithic prompt that mixes policy, workflow, domain knowledge, and
tool documentation is technically editable, but its action space is poorly
structured. A narrow skill file with a clear trigger, procedure, and validation
contract is much easier to improve safely.

Manipulability should also be bounded. An improvement mechanism does not need
unrestricted permission to rewrite its runtime, delete its records, weaken its
evaluator, and change its success criteria at the same time. A useful action
space identifies:

- which artifacts may be changed;
- which interfaces and safety constraints must remain fixed;
- how large a change may be;
- what evidence is required before accepting it;
- how to compare with the previous version;
- how to roll back a harmful change.

Permissions are therefore not only a security mechanism. They are part of the
learning design: they define the action space of self-improvement.

## The Observability–Manipulability Matrix

The two interfaces form a simple design matrix:

| | Low manipulability | High manipulability |
| --- | --- | --- |
| **Low observability** | The system is opaque and frozen | The system can change, but changes are guesses |
| **High observability** | Problems can be diagnosed but not repaired | The system can identify and act on improvement targets |

A system with neither interface cannot meaningfully self-improve. A highly
observable but non-manipulable system becomes a monitoring system: it produces
good diagnoses but depends on someone else to act. A manipulable but
unobservable system is dangerous because it can make broad changes without
understanding their causes.

Only the upper-right condition supports grounded self-improvement, and even
there the loop still needs an evaluator. Eyes and hands make learning possible;
evaluation decides whether a movement was useful.

## Evaluation Prevents Change from Masquerading as Improvement

Observability and manipulability can produce a new harness, but “different” is
not the same as “better.” Every modification should face an acceptance
mechanism: regression tests, benchmark tasks, replayed threads, human review,
operational metrics, or some combination of them.

The evaluator should be harder to manipulate than the implementation. If the
same update can weaken the success criterion whenever it fails, the system can
improve its score without improving its behavior. This is why bounded
manipulation matters. The improver may edit a skill or script while golden
cases, safety constraints, and acceptance rules remain protected.

For a retrospective system, evaluation can compare periods:

- Did the repeated error occur less often?
- Did the new script reduce steps or retries?
- Did the skill generalize beyond the threads that motivated it?
- Were old successful behaviors preserved?
- Did the change introduce new friction?

These signals become the observations for the next retrospective, closing the
loop across periods.

## Design Harnesses for Improvement

Most harnesses are designed only to execute today's task. A self-improvable
harness must also support tomorrow's diagnosis and modification.

That leads to several practical design principles:

1. **Preserve experience as inspectable records.** Important context should not
   disappear when a thread ends.
2. **Capture causal traces, not only final metrics.** The improver needs to
   distinguish symptoms from mechanisms.
3. **Make records queryable and comparable.** Search, summaries, clustering,
   and stable identifiers are part of observability.
4. **Expose explicit editable surfaces.** Skills, tools, scripts, and workflows
   should have clear ownership and contracts.
5. **Keep the action space bounded.** Permissions, protected invariants, small
   diffs, and rollback make self-improvement controllable.
6. **Evaluate across both new and old cases.** Improvement should fix the
   target without silently erasing previous capabilities.
7. **Let the system improve its interfaces.** A retrospective may discover
   that the missing capability is a better log, replay, tool, or edit surface.

The long-term quality of a self-improving system may depend less on how
frequently it changes and more on how clearly it can connect experience to a
bounded change.

## Conclusion

Harness self-improvement is often described as an optimizer, coding agent, or
evolutionary loop rewriting the system around a model. But the loop only works
when the improvement mechanism has an effective relationship with that system.

Observability provides the evidence needed to discover an improvement target.
Manipulability provides the action space needed to express a solution.
Evaluation determines whether the solution should survive.

The retrospective skill illustrates this at a practical scale. Give the
improvement mechanism access to meaningful experience records, let it identify
repeated patterns, and expose a bounded set of skills, scripts, and tools it can
change. The result is a system that does more than remember its mistakes. It
can turn those mistakes into infrastructure for its next period of work.

> A self-improving harness needs eyes to find the target, hands to make the
> change, and a test to decide whether the change deserves to remain.
