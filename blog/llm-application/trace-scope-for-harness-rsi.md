# Trace Scope: Connecting Observability to Manipulability

An agent receives a requirement, loads a skill, calls a model, invokes a tool,
and reads an external service's response. A trace may record every step. But a
retrospective that wants to improve the agent's harness needs two more kinds
of information. Which parts of that history must be preserved, which are
outside the harness's control, and which can it improve? How well did the work
serve its purpose, across the outcomes that matter to this application?

This is the connection between the [observation and manipulation interfaces](/blog/llm-application/observability-manipulability-for-self-improving-harness).
Observation shows what happened. Manipulation defines the action space. A
**trace with scope and evaluation labels on its items** connects them: scope
records each item's role in an improvement cycle, while business-specific
evaluations record what went well or badly. Both belong to the trace item,
even when an evaluation arrives after execution. Later processes
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
identify them reliably. A broad mixed parent can remain unlabeled when its
children carry precise labels; the parent itself is not an edit candidate.

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
children carry scope. On an independently attributable item, a missing label
means incomplete trace data: consumers may retain the item as context but
must not propose changing it or infer that it is `out`.

Scope says whether the improver may propose a change; the item's `kind` and
`subject` say what it is. A user requirement, model invocation, and fixed
evaluation case can all be `out`, but a projector can treat them differently
because their kinds differ. `out` does not mean irrelevant or omitted.
This relies on shared base kinds such as `requirement`, `model.invoke`,
`skill.load`, `tool.call`, and `evaluation.case`. A harness may retain a more
specific native event name, but it must map that name to a shared kind before
a generic projector can apply kind-specific rules. Without that mapping,
`harness_rsi.scope: out` alone would not tell the projector what context to
preserve.

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

These fields define a **logical contract** that any harness can emit. They are
separate from OTel's wire format and standardized attribute names. The first
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
3. Flag a missing scope on an independently attributable item as incomplete
   trace data; do not guess `in` or `out`.
4. Keep item IDs and parent relationships stable so compact views can cite the
   original evidence.
5. Include the convention and scope-boundary versions in the trace, and keep
   labels attached when exporting the trace to another format.
6. Keep the item's kind and subject when exporting it; do not discard an
   `out` item merely because this loop cannot change it.

These rules create one part of the interchange point. Different runtimes can
emit items with the same meaning, and a downstream projector need not know how
each runtime stores its internal conversation.

## Evaluations Label the Item They Judge

An item can carry several business-specific evaluations alongside its scope.
Each evaluation has a `name`, the observed `value`, and the desired `target`
value. Its optional `weight` expresses relative importance and defaults to
`1`. The item ID already identifies what was judged; `target` is a score, not
another item ID.

For example, after observing later searches, the harness can present the
skill item from `run-17` with its evaluation attached:

```json
{
  "trace_id": "run-17",
  "item_id": "42",
  "kind": "skill.load",
  "harness_rsi.scope": "in",
  "harness_rsi.evaluations": [
    {"name": "search_efficiency/v2", "value": 0.3, "target": 1.0, "weight": 2},
    {"name": "wrong_tool_use/v1", "value": 0, "target": 0}
  ]
}
```

The second evaluation uses the default weight of `1`. A metric's name
identifies how to interpret its values; if its rubric or allowed range
changes, the name needs a new version so consumers do not compare unlike
scores. The `target` states the desired value, whether that is `1` for a
successful binary check or `0` for an error count. A missing evaluation means
*unmeasured*, not zero. Weights can guide prioritization, but no automatic
weighted sum can replace the business owner's decision about tradeoffs.

A user, deterministic check, business service, or model-based judge may supply
an evaluation. A run outcome or later user reaction can be attached to its own
item rather than forced onto the skill item. If feedback arrives after
execution, the trace adapter associates it with the original item ID in the
stored trace view. Its scope stays fixed; the evaluation enriches that item.

## How This Extends OpenTelemetry

[OpenTelemetry traces](https://opentelemetry.io/docs/specs/otel/trace/api/) are
made of spans with attributes and timestamped events. A span describes an
operation; an event records an occurrence within one. The OpenTelemetry
[GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)
describe agent, planning, workflow, and tool operations. They offer a common
vocabulary for **what happened**. They do not currently define whether an
item is in the improvement scope of a particular RSI loop.

An OTel producer can express this contract using custom attributes on the
relevant span or event:

```text
root span:        harness_rsi.schema.version     = "2"
                  harness_rsi.scope_boundary     = "coding-harness/v3"
execute_tool span: gen_ai.operation.name         = execute_tool
                  harness_rsi.scope              = in
                  harness_rsi.subject.id         = spec-search-tool
                  harness_rsi.subject.version    = "7"
```

The `harness_rsi.*` keys belong to this design; they are not standardized
`gen_ai.*` fields. A producer using another trace format can carry the same
logical fields; an adapter can translate them to OTel without changing their
meaning. The item kind and subject remain available beside
`harness_rsi.scope`, so a consumer can distinguish an `out` requirement from
an `out` model call.

On OTel spans, the span ID identifies the item. An OTel event has no separate
span ID, so a producer would give it an item ID attribute to preserve the
source reference. The trace-level convention and boundary versions can live
on the root span; they are not a scope label for that mixed parent.

OTel's GenAI conventions also define a
[`gen_ai.evaluation.result` event](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-events.md)
with a metric name and optional score, label, and explanation. That is a useful
carrier for one dimension, but OTel does not define this contract's desired
`target` or `weight`. When evaluations are known before a span ends, a producer
can carry them as custom item attributes where structured values are
supported. Feedback received after a span ends cannot be added to that span;
a correlated OTel event or record can carry the item ID. The trace adapter
attaches the evaluation to that item in the stored view. The per-item contract
is the same in either case.

Granularity remains essential. An OTel model span may be `out` because the
model is an external dependency, while a child event identifies an `in`
prompt supplied to it. A remote response can be `out` even when its parent
is an `in` tool operation. The span tree expresses execution relationships;
the scope attribute expresses whether the loop may propose a change.

For long runs, producers must retain the items consumers need. OTel SDKs may
discard events beyond configured [span event limits](https://opentelemetry.io/docs/specs/otel/trace/sdk/).
A single giant span with thousands of events is a poor durable history.
Meaningful operations can be child spans, while dense records can remain in a
durable event store linked to trace and span IDs. Consumers must be able to
notice missing records or labels; absence cannot mean assumed editability.

## Projections Gather Context; They Do Not Rewrite the Trace

The trace items with their scope and evaluation labels form the shared
experience record. A **projection** is a new, smaller view for a later process.
One projector may select user constraints, tool failures, their scores, and
the harness components involved. Another may select model-version changes
and comparable metric values across runs. Both retain source item IDs.

Scope and item kind can guide how much context a projection carries. It might
keep a requirement verbatim or reference its exact original; summarize a model
call by provider, version, outcome, and error; and keep more diagnostic detail
around an `in` tool or skill. Those are projection choices, not changes
to the source trace or decisions to modify the harness. If the compact view
omits a detail needed for diagnosis, the source reference lets the next stage
inspect the original item.

For the model-upgrade example, a retrospective view might be only:

```text
Constraint: review contract v2 still satisfied          source: run-17/41
Dependency: model-x changed to 2026-09                 source: run-17/43
Candidate surface: repository-spec-skill v7           source: run-17/42
Observation: repeated searches after spec was found   sources: later tool items
Scores: task_correctness=1, target=1                  source: run outcome item
        search_efficiency=0.3, target=1, weight=2     source: run-17/42
```

The view gathers the context needed to investigate a redundant skill. It
does not edit the skill, reinterpret the requirement, or claim the model
upgrade caused the extra searches. Another projection may omit most of this
run and keep only comparable skill-loading and search events across runs.
Consumers should preserve source IDs, metric names, targets, weights, and
unlabeled mixed parents. They should flag missing scope on independently
attributable items and never infer `in` or `out` from it. Scores whose metric
definitions differ need an explicit mapping before comparison.

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
`in` component, the suspected mechanism, the dimensions expected to improve,
the `out` constraints to preserve, and a comparison capable of
rejecting the proposal. Each claim points back to trace items and their
evaluations.

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
rubrics and fixed conditions. The outcome becomes new evidence for the
next cycle.

```yaml
target: repository-spec-skill@7
evidence: [run-17/42, run-21/42]
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
surface, and how to build the candidate without changing the `out` contract.

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
This contract gives that loop two portable inputs on trace items: scope
identifies what the harness may improve, and evaluations describe the outcomes
that matter to the application. General projections and multi-turn diagnosis
can turn those inputs into a reviewable improvement spec. The owning harness
supplies the adapter that implements a supported spec and evaluates its result.

This design is portable across harnesses. They need not share a plugin
system, session file format, or business rubric. They need to emit items
whose identities, relationships, scope, and evaluation meanings are clear
to a consumer. Independent producers can implement this
contract against different harnesses; a shared consumer can test whether their
records agree on mixed-scope runs, delayed feedback, missing scores, and metric
targets. Those interoperability tests are how this design can mature into a
formal standard. The contract gives a general trace-to-spec process a common
input today.
