# Draft: Trace Scope: Connecting Observability to Manipulability

An agent receives a requirement, loads a skill, calls a model, invokes a tool,
and reads an external service's response. A trace may record every step. But a
retrospective that wants to improve the agent's harness needs another piece of
information: which parts of that history must be preserved, which are outside
the harness's control, and which belong to the harness it can improve?

This is the connection between the [observation and manipulation interfaces](/blog/llm-application/observability-manipulability-for-self-improving-harness).
Observation shows what happened. Manipulation defines the action space. A
**scope-labeled trace** connects them: each relevant trace item carries its
role in an improvement cycle. Later processes can build compact views of that
history, diagnose a recurring problem, and locate a possible change without
treating every observed thing as editable.

The [harness RSI](/blog/llm-application/harness-rsi) problem makes this useful.
Models, tools, and workloads keep changing, so a harness must adapt. Yet a
model upgrade is not itself a harness edit, and a user requirement must not
become negotiable because the agent failed to satisfy it. We need a shared
language for those differences before automating the feedback loop.

Consider a model upgrade. A repository review still satisfies the user's
requirement, but the agent now performs several searches that an older skill
insists on even though the newer model has already found the relevant spec.
The requirement is a constraint; the model is a changing dependency; the
skill is a possible edit target. A final success score cannot make those
roles visible, and a transcript without scope leaves the retrospective to
rediscover the boundary every time.

## The Trace Item Is the Unit of Scope

A run does not have one improvement scope. Neither does a turn. Even one model
call may combine an external model, a harness-owned prompt, and instructions
from the user. One label for the whole call would hide the boundary we need.

The proposed convention attaches scope to the **smallest independently
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

## A Small, Portable Convention

I propose four scope values:

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
another. In format-neutral notation, two items might look like this:

```jsonl
{"trace_id":"run-17","schema_version":"1","scope_boundary":"coding-harness/v3"}
{"trace_id":"run-17","item_id":"41","parent_id":"turn-3","kind":"requirement","time":"2026-09-25T09:00:00Z","scope":"frozen","subject":{"id":"review-contract","version":"2"}}
{"trace_id":"run-17","item_id":"42","parent_id":"turn-3","kind":"skill.load","time":"2026-09-25T09:00:00Z","scope":"improvable","subject":{"id":"repository-spec-skill","version":"7"}}
{"trace_id":"run-17","item_id":"43","parent_id":"turn-3","kind":"model.invoke","time":"2026-09-25T09:00:01Z","scope":"external","subject":{"id":"model-x","version":"2026-09"}}
{"trace_id":"run-17","item_id":"44","parent_id":"43","kind":"prompt.apply","time":"2026-09-25T09:00:01Z","scope":"improvable","subject":{"id":"review-prompt","version":"4"}}
```

These field names describe a proposed **logical contract**, not an existing
wire standard. The first record identifies the trace's convention and scope
boundary; the other records are individually labeled items. `subject.id`
names what was observed or used; it is not a
command to edit it. For an `improvable` item, the ID should resolve to a
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

These rules create an interchange point. Different runtimes can emit items
with the same meaning, and a downstream projector need not know how each
runtime stores its internal conversation.

## How This Extends OpenTelemetry

[OpenTelemetry traces](https://opentelemetry.io/docs/specs/otel/trace/api/) are
made of spans with attributes and timestamped events. A span describes an
operation; an event records an occurrence within one. The OpenTelemetry
[GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)
describe agent, planning, workflow, and tool operations. They offer a common
vocabulary for **what happened**. They do not currently define whether an
item is frozen or improvable in a particular RSI loop.

An OTel producer could express this proposal using custom attributes on the
relevant span or event:

```text
gen_ai.operation.name       = execute_tool       # existing GenAI vocabulary
harness_rsi.scope           = improvable         # proposed extension
harness_rsi.subject.id      = spec-search-tool    # proposed extension
harness_rsi.subject.version = "7"                # proposed extension
harness_rsi.schema.version  = "1"                # proposed extension
```

The `harness_rsi.*` names are illustrative and would need to be fixed in a
published convention. They must not be mistaken for standardized `gen_ai.*`
fields. A producer using another trace format can carry the same logical
fields; an adapter can translate them to OTel without changing their meaning.
On OTel spans, the span ID identifies the item. An OTel event has no separate
span ID, so a producer would give it an item ID attribute to preserve the
source reference. The trace-level convention and boundary versions can live
on the root span; they are not a scope label for that mixed parent.

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

The raw trace is the shared record. A **projection** is a new, smaller view
for a later process. One projector may select user constraints, relevant tool
failures, and the harness components involved. Another may select model
version changes across runs. Both read the same labeled items and retain
references to the source item IDs.

```text
conforming producers
        |
        v
scope-labeled traces
        |
        +--> compact task view --> diagnose one failure
        +--> cross-run view ----> find recurring friction
        +--> comparison view ---> evaluate a candidate
```

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
```

The view gathers the context needed to investigate a redundant skill. It
does not edit the skill, reinterpret the requirement, or claim the model
upgrade caused the extra searches. Another projection may omit most of this
run and keep only comparable skill-loading and search events across runs.
Consumers should preserve source IDs and `unknown` labels, and should never
infer `improvable` from a missing label.

The improvement stage still has work to do. A model upgrade may explain why
an old prompt is redundant. Repeated tool failures may point to a harness
wrapper, an unstable service, or a task-specific mistake. Scope labels narrow
the possible edit surface; they do not prove causality or that a candidate
change is beneficial. Fresh comparisons and independent acceptance criteria
remain necessary.

## The Foundation for Harness RSI

The [repository retrospective example](/blog/llm-application/harness-retrospective-loop)
starts with task traces and feedback, then proposes a bounded harness change.
An item-level scope convention supplies a missing interface for that loop:
producers mark the boundary in their traces, projectors gather only the
context needed by each stage, and the improver can connect observations to
components it is actually able to change.

This design is portable across harnesses. They need not share a plugin
system, session file format, or retrospective implementation. They need to
emit items whose identity, relationships, and scope have the same meaning.
The next step is to make this proposed convention precise enough for two
independent producers and one consumer to agree on a mixed-scope run, including
what they do with missing or ambiguous labels. Only then can a generic RSI
pipeline rely on the compact views it receives.
