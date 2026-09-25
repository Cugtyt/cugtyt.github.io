# Trace Scope: Connecting Observability to Manipulability

An agent receives a requirement, loads a skill, calls a model, invokes a tool,
and reads an external service's response. A trace may record every step. But a
retrospective that wants to improve the agent's harness needs two more kinds
of information. Which parts of that history must be preserved, which are
outside the harness's control, and which can it improve? How well did the work
serve its purpose, across the outcomes that matter to this application?

This is the connection between the [observation and manipulation interfaces](/blog/llm-application/observability-manipulability-for-self-improving-harness).
Observation shows what happened. Manipulation defines the action space. A
**scope-labeled trace with linked evaluations** connects them: trace items
record their role in an improvement cycle, while business-specific evaluators
record what went well or badly. Both are records in the trace
contract, even when an evaluation arrives after execution. Later processes
can build compact views of that history, diagnose a recurring problem, and
produce a bounded improvement specification without treating every observed
thing as editable.

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
attributable trace item**. An item may be a timed operation, an event within an
operation, or a separately recorded input. If an item combines influences with
different scopes, the producer emits distinguishable child items when it can
identify them reliably. Otherwise it marks the mixed item `unknown`. A broad
parent operation can remain unlabeled when its children carry precise labels.

```text
agent turn                         mixed; no single scope
├── user requirement               frozen
├── repository skill               improvable
├── model invocation               external
│   └── harness prompt             improvable
├── tool implementation            improvable
└── remote service response        external
```

Here *scope* means the item's role in **this harness improvement process**.
It does not claim that a model or requirement can never change in another
process. A different team may improve the model; harness RSI observes its
version as a dependency and adapts its own components around it.
Likewise, `frozen` means held fixed for this improvement cycle. It does not
mean a requirement or evaluation suite can never be revised by its owner.

## Scope Is One Part of the Trace Contract

The scope vocabulary has four values:

| Scope | Meaning to a harness improver |
| --- | --- |
| `frozen` | A requirement, constraint, or evaluation condition to preserve for the current improvement cycle. |
| `external` | A dependency the harness can observe and adapt to but cannot edit through this loop. |
| `improvable` | A harness-owned component or procedure that this loop may propose changing. |
| `unknown` | The producer cannot establish the boundary; later stages must not assume editability. |

Each labeled item needs a stable identity, a kind, its place in the run, and a
scope. An identifiable subject and version make the label useful across runs.
The trace also identifies the convention version and the declared improvement
boundary under which its labels were assigned. Scope is relative to that
boundary: the same component may be external to one harness and improvable by
another. In format-neutral notation, a short run might look like this:

```jsonl
{"trace_id":"run-17","schema_version":"1","scope_boundary":"coding-harness/v3"}
{"trace_id":"run-17","item_id":"41","parent_id":"turn-3","kind":"requirement","time":"2026-09-25T09:00:00Z","scope":"frozen","subject":{"id":"review-contract","version":"2"}}
{"trace_id":"run-17","item_id":"42","parent_id":"turn-3","kind":"skill.load","time":"2026-09-25T09:00:00Z","scope":"improvable","subject":{"id":"repository-spec-skill","version":"7"}}
{"trace_id":"run-17","item_id":"43","parent_id":"turn-3","kind":"model.invoke","time":"2026-09-25T09:00:01Z","scope":"external","subject":{"id":"model-x","version":"2026-09"}}
{"trace_id":"run-17","item_id":"44","parent_id":"43","kind":"prompt.apply","time":"2026-09-25T09:00:01Z","scope":"improvable","subject":{"id":"review-prompt","version":"4"}}
```

These fields define a **logical contract** that any harness can emit. They are
separate from OTel's wire format and standardized attribute names. The first
record identifies the trace's convention and scope
boundary; the other records are individually labeled items. `subject.id`
names what was observed or used; it is not a command to edit it. For an
`improvable` item, the ID should resolve to a
versioned harness component. Otherwise the retrospective could diagnose a
problem but not name a candidate change.

The producer applies a declared improvement boundary when it records an item.
That boundary should come from the harness owner's configuration, not from a
model's judgment about its own result. A scope label describes the source
item; it is not a grant of permission to edit the named subject. The agent's
later interpretation of a failure must not silently relabel a frozen
requirement as improvable. The minimum producer rules are:

1. Label items individually; do not apply one scope to a mixed parent or an
   entire session.
2. Identify an improvable component precisely enough to compare its versions.
3. Record `unknown` when ownership or scope cannot be established.
4. Keep item IDs and parent relationships stable so compact views can cite the
   original evidence.
5. Include the convention and scope-boundary versions in the trace, and keep
   labels attached when exporting the trace to another format.

These rules create one part of the interchange point. Different runtimes can
emit items with the same meaning, and a downstream projector need not know how
each runtime stores its internal conversation.

## Evaluations Are Linked Records, Not One Success Bit

An evaluation describes a named dimension of an item, turn, run, or later
user outcome. Its author may be a user, a deterministic check, a business
service, or a model-based judge. The evaluator defines the metric's meaning;
the trace convention defines how to attach and interpret the result. For each
numeric metric, the record needs at least:

| Field | Purpose |
| --- | --- |
| Target ID | Identifies the item, turn, or run being judged. |
| Metric name and rubric version | Prevents scores from different definitions being mixed. |
| Value, allowed range, and direction | Makes `0`, `1`, and fractional scores interpretable. |
| Evaluator and evidence reference | Lets a later stage inspect who judged what and why. |

For example, `task_correctness = 1` on a binary `[0, 1]` metric can mean the
final result met the acceptance criteria. `search_efficiency = 0.3` on a
continuous `[0, 1]` metric can indicate avoidable work. Both say higher is
better, but they measure different things. A duration or error-count metric
may instead say lower is better. A thumbs-up or thumbs-down from a user is a
human feedback dimension; it should not silently become a complete task
correctness judgment. A missing evaluation means *unmeasured*, not zero.

A format-neutral evaluation record looks like this:

```json
{
  "evaluation_id": "e-7",
  "target": {"trace_id": "run-17", "item_id": "42"},
  "metric": {"name": "search_efficiency", "rubric_version": "2",
             "min": 0, "max": 1, "better": "higher"},
  "value": 0.3,
  "evaluator": {"id": "review-rubric", "kind": "code"},
  "evidence": ["run-17/45", "run-17/52"]
}
```

The score is linked to the skill item because that is what this evaluator is
judging. Its evidence cites the later search events. Another evaluator could
score the complete run's correctness or attach a user reaction after the
agent has finished. Evaluation records may arrive later than the events they
judge; they append to the experience record and retain target references.
They do not rewrite the original trace or retroactively change its scope
labels. Multiple dimensions remain separate unless the business owner defines
an explicit aggregation rule and tradeoff.

## How This Extends OpenTelemetry

[OpenTelemetry traces](https://opentelemetry.io/docs/specs/otel/trace/api/) are
made of spans with attributes and timestamped events. A span describes an
operation; an event records an occurrence within one. The OpenTelemetry
[GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)
describe agent, planning, workflow, and tool operations. They offer a common
vocabulary for **what happened**. They do not currently define whether an
item is frozen or improvable in a particular RSI loop.

An OTel producer can express this contract using custom attributes on the
relevant span or event:

```text
gen_ai.operation.name       = execute_tool       # existing GenAI vocabulary
harness_rsi.scope           = improvable         # this convention's extension
harness_rsi.subject.id      = spec-search-tool    # this convention's extension
harness_rsi.subject.version = "7"                # this convention's extension
harness_rsi.schema.version  = "1"                # this convention's extension
```

The `harness_rsi.*` keys belong to this design; they are not standardized
`gen_ai.*` fields. A producer using another trace format can carry the same
logical fields; an adapter can translate them to OTel without changing their
meaning.
On OTel spans, the span ID identifies the item. An OTel event has no separate
span ID, so a producer would give it an item ID attribute to preserve the
source reference. The trace-level convention and boundary versions can live
on the root span; they are not a scope label for that mixed parent.

OTel's GenAI conventions also define a
[`gen_ai.evaluation.result` event](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-events.md)
with a metric name and optional score, label, and explanation. That is a useful carrier
for one evaluation dimension. The metric's allowed range, improvement
direction, rubric version, evaluator identity, and links to multiple evidence
items are extensions in this contract, not fields that OTel already
standardizes. If feedback arrives after a target span has ended, an OTel
producer cannot add an event to that ended span. It needs a new correlated
record or span linked to the target. The logical evaluation record retains
the same target ID regardless of its transport.

Granularity remains essential. An OTel model span may identify the external
model while a child event identifies the improvable prompt supplied to it.
An external response can carry `external` even when its parent is a
harness-owned tool operation. The span tree expresses execution relationships;
the scope attribute expresses the improvement boundary.

For long runs, producers must retain the items consumers need. OTel SDKs may
discard events beyond configured [span event limits](https://opentelemetry.io/docs/specs/otel/trace/sdk/).
A single giant span with thousands of events is a poor durable history.
Meaningful operations can be child spans, while dense records can remain in a
durable event store linked to trace and span IDs. Consumers must be able to
notice missing records or labels; absence cannot mean assumed editability.

## Projections Gather Context; They Do Not Rewrite the Trace

The raw trace and linked evaluations form the shared experience record. A
**projection** is a new, smaller view for a later process. One projector may
select user constraints, tool failures, their scores, and the harness
components involved. Another may select model-version changes and comparable
metric values across runs. Both retain references to source item and
evaluation IDs.

Scope can guide how much context a projection carries. It might keep a frozen
requirement verbatim or reference its exact original; summarize an external
call by provider, version, outcome, and error; and keep more diagnostic detail
around an improvable tool or skill. Those are projection choices, not changes
to the source trace or decisions to modify the harness. If the compact view
omits a detail needed for diagnosis, the source reference lets the next stage
inspect the original item.

For the model-upgrade example, a retrospective view might be only:

```text
Constraint: review contract v2 still satisfied          source: run-17/41
Dependency: model-x changed to 2026-09                 source: run-17/43
Candidate surface: repository-spec-skill v7           source: run-17/42
Observation: repeated searches after spec was found   sources: later tool items
Scores: task_correctness=1/1 (binary, higher better)
        search_efficiency=0.3/1 (rubric v2, higher better)  sources: evaluations
```

The view gathers the context needed to investigate a redundant skill. It
does not edit the skill, reinterpret the requirement, or claim the model
upgrade caused the extra searches. Another projection may omit most of this
run and keep only comparable skill-loading and search events across runs.
Consumers should preserve source IDs, score definitions, and `unknown` labels.
They should never infer `improvable` from a missing label or compare two scores
whose rubric versions or directions differ without an explicit mapping.

The improvement stage still has work to do. A model upgrade may explain why
an old skill is redundant. Repeated tool failures may point to a harness
wrapper, an unstable service, or a task-specific mistake. Labels and scores
narrow an investigation; they do not prove causality or that a candidate
change is beneficial. Fresh comparisons and independent acceptance criteria
remain necessary.

## From Projections to a Portable Improvement Spec

The general part of harness RSI can read projections across runs and turns,
look for recurring patterns, and produce an **improvement spec**. That spec is
an evidence-backed proposal, not an implementation patch. It identifies the
improvable component, the suspected mechanism, the dimensions expected to
improve, the frozen conditions to preserve, and a comparison capable of
rejecting the proposal. Each claim points back to trace items or evaluations.

For the example, it might say: under the newer model, the review skill's
mandatory search sequence appears redundant in several runs. Try a skill
version that skips searches once the relevant spec is already in context.
Predict higher `search_efficiency` without reducing `task_correctness` or
violating the review contract. The spec must also cite runs that contradict
the hypothesis. One low score or one model upgrade is not enough to establish
the mechanism.

The shared process stops at this portable spec. A **harness-specific
implementation adapter** maps the component ID to its real skill, tool, or
configuration, checks that the proposed change is supported and authorized,
and constructs a candidate. It may reject an unsupported spec with a reason.
The evaluator then compares that candidate with a baseline under compatible
rubrics and fixed conditions. The outcome becomes new linked evidence for the
next cycle.

```yaml
target: repository-spec-skill@7
evidence: [run-17/42, run-17/e-7, run-21/e-4]
hypothesis: Mandatory searches repeat work after the relevant spec is found.
desired_change: Skip those searches when the spec is already in context.
predict:
  search_efficiency: increase under rubric v2
  task_correctness: no decrease under rubric v1
preserve: [review-contract@2]
compare: Fresh tasks from matched starting states under the same model and rubrics.
```

This is an illustrative spec, not a command format. The generic process can
produce it from evidence. Only the adapter knows whether
`repository-spec-skill@7` is a file, a plugin setting, or another harness
surface, and how to build the candidate without touching the frozen contract.

```text
trace adapter + business evaluators
              |
              v
       standard experience
              |
              v
   general projection and diagnosis
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
This contract gives that loop two portable inputs: item-level scope identifies
what the harness may improve, and linked evaluations describe the outcomes
that matter to the application. General projections and multi-turn diagnosis
can turn those inputs into a reviewable improvement spec. The owning harness
supplies the adapter that implements a supported spec and evaluates its result.

This design is portable across harnesses. They need not share a plugin
system, session file format, or business rubric. They need to emit items and
evaluations whose identities, relationships, scope, and score definitions have
the same meaning to a consumer. Independent producers can implement this
contract against different harnesses; a shared consumer can test whether their
records agree on mixed-scope runs, delayed feedback, missing scores, and metric
direction. Those interoperability tests are how this design can mature into a
formal standard. The contract gives a general trace-to-spec process a common
input today.
