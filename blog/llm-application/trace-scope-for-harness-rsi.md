# Trace Scope: Connecting Observability to Manipulability

An agent receives a requirement, loads a skill, calls a model, invokes a tool,
and reads an external service's response. A trace may record every step. But a
retrospective that wants to improve the agent's harness needs two more kinds
of information. Which parts of that history must be preserved, which are
outside the harness's control, and which can it improve? How well did the work
serve its purpose, across the outcomes that matter to this application?

This is the connection between the [observation and manipulation interfaces](/blog/llm-application/observability-manipulability-for-self-improving-harness).
Observation shows what happened. Manipulation defines the action space. A
**trace with item-level scope and evaluation events** connects them: scope
records which observed parts may change, while evaluation events record what
went well or badly. Later processes can build compact views of that history,
diagnose a recurring problem, and produce a bounded improvement specification
without treating every observed thing as editable.

The [harness RSI](/blog/llm-application/harness-rsi) problem makes this useful.
Models, tools, and workloads keep changing, so a harness must adapt. Yet a
model upgrade is not itself a harness edit, and a user requirement must not
become negotiable because the agent failed to satisfy it. We need a shared
language for those differences before automating the feedback loop.

Consider a model upgrade. A repository review still satisfies the user's
requirement, but the agent now performs several searches that an older skill
insists on even though the newer model has already found the relevant spec.
The requirement is a constraint; the model is a changing dependency; the
skill is a possible edit target. The review can satisfy the requirement while
still wasting time on searches. One final success score misses that cost. A
scope label alone identifies an edit surface but does not say whether changing
it would help. The retrospective needs both the trace and multidimensional
feedback.

## The Trace Item Is the Unit of Scope

A run does not have one improvement scope. Neither does a turn. Even one model
call may combine an external model, a harness-owned prompt, and instructions
from the user. One label for the whole call would hide the boundary we need.

This convention attaches scope to the **smallest independently
attributable observed action or input**. Such an item may be a timed operation,
an event within an operation, or a separately recorded input. If it combines
influences with different scopes, the producer emits distinguishable child
items when it can identify them reliably. A broad mixed parent can remain
unlabeled when its children carry precise labels; the parent itself is not an
edit candidate.

```text
agent turn                         mixed; no single scope
├── user requirement               out
├── repository skill               in
├── model invocation               out
│   └── harness prompt             in
├── tool implementation            in
└── remote service response        out
```

Here *scope* answers one question: **may this harness improvement loop propose
changing this item?** It does not claim that a model or requirement can never
change in another process. A different team may improve the model; harness
RSI observes its version as a dependency and adapts its own components around
it. A constraint may be revised by its owner in another cycle.

## Scope Is One Part of the Trace Contract

The scope vocabulary has two values:

| Improvement scope | Meaning |
| --- | --- |
| `in` | This loop may propose changing the item. The implementation adapter still checks authorization. |
| `out` | This loop may use the item as context or a constraint but may not propose editing it. |

No label is different from `out`. It is expected on a mixed parent whose
children carry scope and on an evaluation event that reports a score rather
than an improvement subject. On an independently attributable action or input,
a missing scope label means incomplete trace data: consumers may retain it as
context but must not propose changing it or infer that it is `out`.

Scope says whether the improver may propose a change; the item's `kind` and
`subject` say what it is. A user requirement, model invocation, and fixed
evaluation case (a test definition) can all be `out`, yet their kinds
distinguish them. `out` does not mean irrelevant or omitted.
This relies on shared base kinds such as `requirement`, `model.invoke`,
`skill.load`, `tool.call`, and `evaluation.case`. A harness may retain a more
specific native event name, but it must map that name to a shared kind so
readers of the trace can interpret it consistently. Without that mapping,
`harness_rsi.scope: out` alone would not say what the item represents.

Each labeled item needs a stable identity, a kind, its place in the run, and a
scope. An identifiable subject and version make the label useful across runs.
The trace also identifies the convention version and the declared improvement
boundary under which its labels were assigned. Scope is relative to that
boundary: the same component may be out of scope for one harness and in scope
for another. In format-neutral notation, a short run might look like this:

```jsonl
{"trace_id":"run-17","schema_version":"2","scope_boundary":"coding-harness/v3"}
{"trace_id":"run-17","item_id":"41","parent_id":"turn-3","kind":"requirement","time":"2026-09-25T09:00:00Z","harness_rsi.scope":"out","subject":{"id":"review-contract","version":"2"}}
{"trace_id":"run-17","item_id":"42","parent_id":"turn-3","kind":"skill.load","time":"2026-09-25T09:00:00Z","harness_rsi.scope":"in","subject":{"id":"repository-spec-skill","version":"7"}}
{"trace_id":"run-17","item_id":"43","parent_id":"turn-3","kind":"model.invoke","time":"2026-09-25T09:00:01Z","harness_rsi.scope":"out","subject":{"id":"model-x","version":"2026-09"}}
{"trace_id":"run-17","item_id":"44","parent_id":"43","kind":"prompt.apply","time":"2026-09-25T09:00:01Z","harness_rsi.scope":"in","subject":{"id":"review-prompt","version":"4"}}
```

These fields define a **logical contract** that any harness can emit. The first
record identifies the trace's convention and scope boundary; the other
records are individually labeled items. `subject.id`
names what was observed or used; it is not a command to edit it. For an
`in` item, the ID should resolve to a versioned harness component.
Otherwise the retrospective could diagnose a
problem but not name a candidate change.

The producer applies a declared improvement boundary when it records an item.
That boundary should come from the harness owner's configuration, not from a
model's judgment about its own result. An improvement-scope label describes
the source item; it is not a grant of permission to edit the named subject.
The agent's later interpretation of a failure must not silently relabel a
constraint as `in`. The minimum producer rules are:

1. Label items individually; do not apply one scope to a mixed parent or an
   entire session.
2. Identify an `in` component precisely enough to compare its versions.
3. Flag a missing scope on an independently attributable action or input as
   incomplete trace data; do not guess `in` or `out`.
4. Keep item IDs and parent relationships stable so compact views can cite the
   original evidence.
5. Include the convention and scope-boundary versions in the trace, and keep
   labels attached when exporting the trace to another format.
6. Keep the item's kind and subject when exporting it; do not discard an
   `out` item merely because this loop cannot change it.

These rules create one part of the interchange point. Different runtimes can
emit items with the same meaning, without requiring readers to know how each
runtime stores its internal conversation.

## Evaluations Are Events in the Trace

An evaluation is a new trace event emitted after the behavior it assesses. It
may score a segment of work, a turn, or a complete run; a later user reaction
can also be an evaluation event. It need not judge any one earlier item. The
event's place in the trace supplies its run and turn context. Its own ID lets
later views cite the score without attaching it to a skill, tool call, or
other source item.

Each event carries a `name`, the observed `value`, and the desired `target`
value. Its optional `weight` expresses relative importance and defaults to
`1`. Here `target` is a score, not an item reference. For example, after the
searches and review finish, the harness can emit two evaluation events:

```jsonl
{"trace_id":"run-17","item_id":"45","parent_id":"turn-3","kind":"evaluation","time":"2026-09-25T09:02:00Z","harness_rsi.evaluation":{"name":"search_efficiency/v2","value":0.3,"target":1.0,"weight":2}}
{"trace_id":"run-17","item_id":"46","parent_id":"turn-3","kind":"evaluation","time":"2026-09-25T09:02:01Z","harness_rsi.evaluation":{"name":"task_correctness/v1","value":1,"target":1}}
```

The second event uses the default weight of `1`. A metric's name identifies
how to interpret its values; if its rubric or allowed range changes, the name
needs a new version so consumers do not compare unlike scores. The `target`
states the desired value, whether that is `1` for a successful binary check
or `0` for an error count. A missing evaluation means *unmeasured*, not zero.
Weights can guide prioritization, but no automatic weighted sum can replace
the business owner's decision about tradeoffs.

A user, deterministic check, business service, or model-based judge may emit
an evaluation. The evaluator may use the full task context, trace, and business
intent to assign a score; the event records the outcome, not its internal
scoring instructions. If feedback arrives after execution, it remains a later
event correlated with the run. The earlier trace items and their scope labels
stay as recorded.

## Projections Gather Context; They Do Not Rewrite the Trace

The scoped trace items and evaluation events form the shared
experience record. A **projection** is a smaller context view of that trace
for the later spec proposal stage. It keeps the event order, source IDs, scope
labels, and evaluation values needed for that stage, while replacing bulky
payloads with `[compacted]`. The source trace remains available through those
IDs if the proposal stage needs the original content.

For the model-upgrade scenario, a compact view of a fuller trace could be:

```text
run-17/41  requirement       out  review contract v2
run-17/42  skill.load        in   repository-spec-skill@7: mandatory searches
run-17/43  model.invoke      out  model-x@2026-09: [compacted]
run-17/s1  tool.call         in   spec-search-tool: search("review spec")
run-17/r1  service.response  out  [compacted]
run-17/s2  tool.call         in   spec-search-tool: search("review spec")
run-17/r2  service.response  out  [compacted]
run-17/45  evaluation             search_efficiency/v2 value=0.3 target=1 weight=2
run-17/46  evaluation             task_correctness/v1 value=1 target=1
```

This view keeps the sequence and the score events without deciding whether
the skill or model caused the repeated searches. The spec proposal stage can
inspect `run-17/r1` and `run-17/r2` if their compacted content matters. A
projection may retain more or less context for a particular task, but it
must keep source IDs and never silently turn a missing scope label into `in`
or `out`. Scores whose metric definitions differ need an explicit mapping
before comparison.

The improvement stage still has work to do. A model upgrade may explain why
an old skill is redundant. Repeated tool failures may point to a harness
wrapper, an unstable service, or a task-specific mistake. Labels and scores
narrow an investigation; they do not prove causality or that a candidate
change is beneficial. Fresh comparisons and independent acceptance criteria
remain necessary.

## From Projections to a Portable Improvement Spec

The general part of harness RSI can read projections across runs and turns,
look for recurring patterns, and produce an **improvement spec** with three
parts: **issue** describes the observed problem and suspected cause;
**proposal** names the `in` component and change to try; **predict** states
what should improve and what must remain satisfied. Source references belong
beside the claims they support, within these parts. The spec proposes a testable
change; it is not an implementation patch or a copy of the evaluator's scoring
logic.

**Issue.** Under model-x@2026-09 (`run-17/43`), repository-spec-skill@7 still
requires searches (`run-17/42`). After the relevant spec appeared in the
first result (`run-17/r1`), another search followed (`run-17/s2`). The
`search_efficiency/v2` score was 0.3 against a target of 1 (`run-17/45`),
while `task_correctness/v1` met its target (`run-17/46`). This suggests that
the skill's mandatory search step may now add avoidable work.

**Proposal.** Try a new version of repository-spec-skill@7 (`run-17/42`) that
skips the mandatory search when the relevant spec is already in context.
Preserve the review contract v2 (`run-17/41`).

**Predict.** On fresh tasks from matched starting states under the same model,
the new skill should improve `search_efficiency/v2` (`run-17/45`) without
reducing `task_correctness/v1` (`run-17/46`) or violating the review contract
(`run-17/41`). A comparison with the baseline should be able to reject this
prediction. One low score or one model upgrade is not enough to establish the
cause; other runs may contradict it.

The shared process stops at this portable spec. A **harness-specific
implementation adapter** maps the component ID to its real skill, tool, or
configuration, checks that the proposed change is supported and authorized,
and constructs a candidate. It may reject an unsupported spec with a reason.
Only the adapter knows whether `repository-spec-skill@7` is a file, a plugin
setting, or another harness surface, and how to build the candidate without
changing the `out` contract.

An independent evaluator then compares the candidate with a baseline using
the same evaluator version and matched task conditions. The proposal process
receives score events and task constraints, not the evaluator's internal
scoring instructions; that separation reduces the chance of optimizing for a
disclosed checklist instead of the intended outcome. The result becomes new
evidence for the next cycle.

```text
trace adapter + business evaluators
              |
              v
       standard experience
              |
              v
       compact trace projection
              |
              v
      diagnosis and spec proposal
              |
              v
       improvement spec
              |
              v
  harness implementation adapter
              |
              v
       candidate and evaluation
```

## The Foundation for Harness RSI

The [repository retrospective example](/blog/llm-application/harness-retrospective-loop)
starts with task traces and feedback, then proposes a bounded harness change.
This contract gives that loop two portable inputs in one trace: scope labels
identify what the harness may improve, and evaluation events describe the
outcomes that matter to the application. General projections and multi-turn
diagnosis can turn those inputs into a reviewable improvement spec. The owning
harness supplies the adapter that implements a supported spec and evaluates
its result.

This design is portable across harnesses. They need not share a plugin
system, session file format, or business rubric. They need to emit scoped
items and evaluation events whose identities, relationships, and meanings are
clear to a consumer. Independent producers can implement this
contract against different harnesses; a shared consumer can test whether their
records agree on mixed-scope runs, delayed feedback, missing scores, and metric
targets. Those interoperability tests are how this design can mature into a
formal standard. The contract gives a general trace-to-spec process a common
input today.
