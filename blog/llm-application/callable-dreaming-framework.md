# A Callable Dreaming Framework: From Traces to Improvement Specs

A harness can record what an agent did without knowing what should change.
Long traces contain requirements, external dependencies, harness-owned
components, tool results, and feedback in the same history. Reading every run
from scratch to propose an improvement is expensive, and a single successful
final answer can hide wasted work.

The [trace-scope contract](/blog/llm-application/trace-scope-for-harness-rsi)
gives us a common input: actions and inputs carry `in` or `out` improvement
scope, and evaluation events record named scores. This article describes the
next block. **Dreaming** takes completed traces and an improvement goal,
builds compact context per session, examines patterns across sessions and
turns, checks a proposed change against the traces, and returns an
evidence-backed improvement spec.

The block is callable. A host runtime chooses when to invoke it, which traces
to supply, where to store its result, and whether to act on that result. The
framework owns the work within one invocation, including parallel session
processing. That boundary lets the same dreaming process serve a scheduled
retrospective, an interactive review, or another agent framework.

## The Whole Process

For one invocation, the host selects completed traces and states what kind of
improvement it wants to investigate. Dreaming maps the traces into the shared
contract, processes each session independently, and then looks across the
session results for a candidate change. A separate evaluation pass tests the
candidate against the trace evidence before the host receives a result.

```text
host: completed traces + improvement goal
                    |
                    v
             map and check items
                    |
             +------+------+          parallel by session
             v      v      v
         session A  B      C          compact → observe
             +------+------+
                    |
                    v
          compare across sessions
                    |
                    v
          draft a candidate spec
                    |
                    v
          evaluate against traces
                    |
                    v
          improvement spec, or
          no justified proposal
                    |
                    v
host: review, implement, measure
```

The call can be expressed as `dream(traces, goal, stage_overrides)`. `traces` are
the completed records to examine. `goal` states the improvement boundary and
constraints without choosing a fix. `stage_overrides` optionally replaces
the logic of named stages below. The result is either an evidence-backed spec
or an explanation of why the evidence does not yet justify one.

Consider repository reviews under `coding-harness/v3`. The goal is to find
avoidable work while preserving the review contract. The traces include a
review skill that the harness may change, a model version it cannot change,
searches and tool results, and evaluation events for search efficiency and
task correctness. The same example follows through the stages.

## Stage 1: Map and Check the Traces

The first stage maps native event names to shared kinds while retaining their
IDs, or passes through traces that already follow the contract. It checks each
attributable action or input for an improvement scope. In the review example,
the skill is `in`, while the model and user requirement are `out`. An
evaluation is a separate event with `name`, `value`, desired `target`, and
optional `weight`; it need not score one earlier item. The call's `goal` is
the improvement question, whereas an evaluation's `target` is the desired
score for a metric.

A missing scope is incomplete data, not permission to edit the item. The
framework reports the gap rather than guessing `in` or `out`. It also keeps
stable item IDs, so later stages can refer back to original content.

## Stage 2: Compact and Observe Each Session

Each session becomes a small, trace-shaped view. Projection preserves event
order, item IDs, and the scope and evaluation labels while replacing bulky
content. For example, a search result body can become `[compacted]`, while
the search query, skill version, and result ID remain visible. The original
result remains available by ID if a later claim depends on what it said.

Session analysis can then note that the review performed two similar searches
and cite both events. It does not yet decide that the skill caused the
repetition. Sessions can be compacted and examined in parallel, while the
order of events within each session remains intact. If a selected session
cannot produce a view, the call reports that gap rather than silently
omitting it.

## Stage 3: Compare Sessions and Draft a Proposal

The cross-session analysis compares session views, component versions,
evaluations, and contrary examples. Suppose another review using the same
skill also repeats a search. The process can reopen compacted results to
check whether the relevant spec was already available. It can then ask
whether the skill's mandatory search step caused avoidable work. The model
version remains context, not an edit candidate.

A single low score or unusual run may be insufficient. Proposal logic drafts
an Issue, a bounded Proposal, and a testable Predict from the patterns it
finds. This is a candidate spec, not yet the framework's answer.

## Stage 4: Evaluate the Candidate Against the Traces

The candidate enters a dedicated evaluation context with the goal, compact
views of all selected sessions, their evaluation events, and access to the
original items. This pass checks the proposed change rather than generating
another idea. It can look beyond the candidate's citations for contrary
evidence and reopen items when compact views omit needed details.

In the review example, it asks whether the second search found information
that the first search lacked. If it only repeated available information
across the affected runs, skipping it could improve search efficiency while
preserving task correctness. If it supplied unique information, the proposal
could hurt correctness. The pass also checks the review contract and can
accept the spec, send it back for revision, or explain why the traces do not
justify a proposal.

For each affected run, the evaluator can ask which actions the proposal would
have changed and how that might affect its scored outcomes. This infers an
expected performance gain from past runs; it cannot observe the outcome of a
change that has not been implemented. Its judgment should name the score
dimensions it expects to improve, the constraints it expects to preserve,
and the evidence or uncertainty behind both. A later comparison on new runs
is needed to measure whether the gain occurs.

## The Resulting Spec

After the candidate passes that evaluation, the spec for the review example
could read:

**Issue.** Under model-x@2026-09 (`run-17/43`), the review skill still requires
searches (`run-17/42`). The first search returned the relevant spec
(`run-17/r1`), yet another search followed (`run-17/s2`). Search efficiency
fell below its desired value (`run-17/45`), while task correctness met its
target (`run-17/46`). Another review shows the same skill and a repeated
search (`run-21/42`, `run-21/s2`). The mandatory search step may now add
avoidable work.

**Proposal.** Try a new version of the review skill (`run-17/42`) that skips
the mandatory search when the relevant spec is already in context. Preserve
the review contract (`run-17/41`).

**Predict.** On fresh, matched tasks under the same model, the new skill
should reduce repeated searches and improve search efficiency without
reducing task correctness or violating the review contract. A comparison
with the current skill should be able to reject that prediction.

The spec carries the problem, a bounded change, expected effects, and source
references. Each claim can be checked against the trace. The framework does
not prescribe a patch format, and another harness can produce the same kind
of spec even if its editable component is a workflow setting rather than a
skill file.

## Replace the Logic of a Stage

The framework runs named stages with defined inputs and outputs.
`stage_overrides` lets a harness replace the logic of any stage for a call;
the next stage still receives the same kind of result:

- **`mapTrace`: native session → shared trace items.** Replace the mapping
  when a harness has its own event names or component IDs. A standardized
  trace needs no mapping change.
- **`projectSession`: shared session → compact view.** The ordinary projector
  can replace a bulky tool result with `[compacted]`. A replacement might
  summarize that result or retain selected facts for the harness's task,
  while preserving event order, labels, and source IDs.
- **`analyzeSession`: compact view → referenced observations.** A replacement
  can recognize patterns such as repeated searches or incorrect tool use.
- **`proposeSpec`: goal and session results → candidate spec or no proposal.**
  A replacement can apply the harness's rules for recurrence, constraints,
  and which `in` component is a plausible change target.
- **`evaluateSpec`: candidate and trace evidence → accept, revise, or reject.**
  A replacement can judge the expected gain using business-specific score
  dimensions and inspect original items for counterevidence.

The host supplies only the replacements it needs. Each can use code, an
agent, or both. The framework still sequences the stages, processes sessions
in parallel, and checks their outputs: references must resolve, attributable
actions and inputs must have scope labels, and a proposed change must name an
`in` component. Replacing one stage does not require replacing the others.

The producer of trace evaluation events is separate from this spec evaluation
pass. It may use the full task context and business intent to score a run.
Dreaming reads those events, but does not need the producer's internal scoring
instructions. That keeps proposal generation from optimizing against a
disclosed checklist instead of the intended outcome.

## How a Host Uses the Block

The host decides what happens after dreaming returns. It can show the spec to
a person, pass it to a harness-specific implementation adapter, or record a
no-proposal result and wait for more evidence. An implementation adapter
resolves the named `in` component and creates a candidate implementation. An
independent evaluation compares that implementation with a baseline under
matched conditions. This is where an inferred gain can be measured. The host
handles adoption and any recurring trigger for the next call.

This separation makes the framework useful inside different runtimes. Its
portable responsibility is narrow: turn completed labeled traces and a goal
into a reviewable, evidence-backed spec. The harness supplies the meaning of
its components and business patterns; the host controls the lifecycle around
the call.
