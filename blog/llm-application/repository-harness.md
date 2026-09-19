# Towards a Repository Harness for AI Coding

An AI coding agent can produce a large patch before a reviewer has finished
understanding the requirement. If the code, tests, and documentation all follow
the same mistaken assumption, the result can look complete while doing the
wrong thing. As changes accumulate, a feature can also break behavior far
outside the files its author intended to affect.

A repository harness is the infrastructure that helps us control those changes:
contributor instructions, specs, scripts, tests, and review workflows. This post
proposes four practices for building one: **deliver specs with substantive code
changes, maintain explicit references when specified behavior changes, regularly
check the whole repository against its contracts, and make review a repeatable
repository-owned workflow.**

These are starting points for an evolving approach. The aim is guidance that a
service, library, CLI, or application can adopt using its existing tools.
DeepSeek Harness (DSH) supplies several concrete examples through its Agent
Notes, documentation checks, and code review skill.

## 1. Deliver the Spec, Code, and Tests Together

Substantive changes to behavior, interfaces, or architecture should include a
self-contained spec, implementation, and verification in the same change. This
includes substantive bug fixes and compatibility changes. Mechanical and local
edits are exempt; normal review and relevant checks are enough for those.

The spec describes the intended behavior. It gives reviewers a basis for
judging the implementation instead of asking them to infer the requirement from
the generated code. It should explain the current state, goals and non-goals,
decisions, alternatives considered, and acceptance criteria—including how those
criteria will be tested.

### Make the intended behavior explicit

Consider adding cancellation to a background worker. “Add a stop command” leaves
important choices open. Does stopping mean sending a signal or waiting for the
child to exit? Is partial output preserved? What happens if cancellation arrives
before the worker starts?

A useful spec might contain:

```markdown
# Worker cancellation

## Current state at the start of this change
Workers run as child processes. The controller exposes start and wait,
but a caller cannot stop an active worker. Wait resolves after child exit.

## Goal
Allow callers to cancel a worker and receive its final outcome.

## Non-goals
No pause/resume support. No redesign of worker scheduling.

## Decisions
If cancellation arrives before spawn, no child starts and wait settles
as cancelled. Otherwise, stop requests cancellation and waits for child exit.
Preserve captured output and report cancellation separately from exit code.
Stopping an already finished worker returns its existing result.

## Alternatives considered
Return immediately after sending the signal: rejected because callers could
start conflicting work while the old process still owns resources.
Discard partial output: rejected because it removes useful failure evidence.

## Acceptance criteria
Cancel before spawn: no child is launched and wait settles as cancelled.
Cancel during execution: the child exits before stop resolves.
Cancel after output: the final result retains all output captured before exit.
Child traps the signal and exits zero: cancellation remains visible.
Stop after completion: the original result is returned unchanged.
```

Now the implementer and reviewer share a meaning of “stop.” The rejected
alternatives also explain why an apparently simpler implementation would be
wrong for this design. Record alternatives that were actually considered;
inventing them to fill a template preserves no useful reasoning.

When code generation is cheap, a concrete implementation can accompany the
spec during review. Discuss high-risk or ambiguous decisions earlier when
useful, but review and accept the spec, code, and tests as one change. If the
code violates an agreed requirement, fix the code or explicitly reconsider the
requirement. Do not silently redefine success around what the agent produced.

The spec ships with the code and remains an active statement of requirements.
It can say “stop waits until the child exits” before and after implementation;
completion alone requires no rewrite. The starting-state section explains the
original problem. The decisions and acceptance criteria remain authoritative
until explicitly updated or superseded by a linked spec.

### Show how acceptance is tested

An acceptance criterion should name an observable result. Checking that the
controller called `kill()` does not establish that stop waited for termination.
A stronger test launches a controlled child and observes that it has exited
before stop resolves. Another child can handle the signal and exit zero,
checking that cancellation is still reported.

To verify output retention, have the controlled child emit a known marker and
remain running. Wait until the controller captures the marker, then request
cancellation. Assert that the child has exited, the result reports cancellation,
and the captured output still contains the marker. Synchronize on the observed
output rather than sleeping for an assumed startup time.

Keep these tests with the implementation. For a regression fix, demonstrate
that the test detects the defective behavior. Use the real application entry
path when the requirement depends on configuration, transport, or packaging.
Where automated testing is impractical, record the verification procedure,
result, and remaining limits. Report skipped checks as skipped.

### Put the workflow in the repository

Start with a spec template and a PR template that asks for the relevant spec
and verification results. Document the procedure in `CONTRIBUTING.md`; link
coding agents to it through `AGENTS.md` or an implementation skill. A reviewer
should not need the author's chat history to understand the change.

DSH's [Agent Notes](https://github.com/deepseek-ai/deepseek-harness/blob/master/.agents/notes/README.md)
show how to preserve design reasoning. Proposed notes include the problem,
proposal, alternatives, acceptance criteria, and risks. DSH reserves these
records for lasting rationale; it does not require one for every edit. A
decision already made can start as an implemented note. Moving a proposed note
to implemented requires a rewrite into its shipped form. Our proposal borrows
the emphasis on reasoning but keeps the spec shipped with code as an active
requirements document, with no completion-triggered change of format.

A scope report can help reviewers compare the implementation with the intended
change. DSH provides:

```bash
pnpm --silent run change-scope --base <verified-base-ref> --head <reviewed-head-ref>
```

The [script](https://github.com/deepseek-ai/deepseek-harness/blob/master/scripts/change-scope.ts)
records the resolved commits and separates committed, staged, unstaged, and
untracked paths. It makes the actual scope visible; the reviewer still needs to
choose the correct base and decide whether the changes are justified.

Templates and scripts support the agreement. They cannot determine whether the
goal is worthwhile or whether a design tradeoff is acceptable. Those remain
review decisions.

## 2. Account for Every Change to Specified Behavior

A spec stays useful only if later changes account for its promises. **Every
behavior change covered by an existing spec should appear in a self-contained
update to that spec or in a new spec that explicitly replaces the affected
behavior.** Make that documentation change alongside the code and tests.

Specs are maintained documents. Clear updates and references let readers find
the current requirements without moving every document through a complex
lifecycle.

### Update in place or add a linked spec

Update the existing spec when the change fits its purpose and the revised
account remains clear on its own. Change the affected decisions, examples, and
acceptance criteria together. Appending a correction while leaving the original
requirement intact creates two answers to the same question.

Create a new spec when a materially different design or reversal deserves its
own explanation. Describe the new behavior, motivation, alternatives, and
acceptance criteria. Identify exactly which earlier behavior it replaces, and
add a reference from the earlier spec so readers can find the current rule
from either document.

Suppose a later worker API separates requesting cancellation from waiting for
termination. The references could say:

```text
New spec: asynchronous worker cancellation
Supersedes the stop-operation completion semantics in worker-control.md.
Stop acknowledges the cancellation request; wait observes final completion.
Output retention and stopping an already completed worker remain unchanged.

Earlier spec: worker control
The stop-operation completion semantics are superseded by
asynchronous-worker-cancellation.md. The other requirements still apply.
```

The new design needs its own rationale and tests. The references identify the
part that changed without implying that the entire earlier spec is obsolete.
A generic “related documents” link would leave readers to resolve that
ambiguity themselves.

Both documents remain editable for corrections and factual updates. If a chain
of replacements becomes difficult to follow, consolidate the current
requirements and retain links to useful decision rationale. A new contributor
should be able to understand today's behavior without reconstructing every
intermediate change.

### Check references and documentation against code

Begin with a small checker for required sections and internal links. If
replacement references use a defined field or convention, check that the target
exists and the reference back is present. Give the checker valid and invalid
fixtures, including newly added specs, broken links, and missing replacement
references. Run it in CI.

DSH provides examples of executable documentation checks:

| Tool | What it checks |
| --- | --- |
| [`verify-agent-note-format`](https://github.com/deepseek-ai/deepseek-harness/blob/master/scripts/verify-agent-note-format.ts) | Required sections and metadata for DSH's Agent Note format |
| [`verify-md-links`](https://github.com/deepseek-ai/deepseek-harness/blob/master/scripts/verify-md-links.ts) | Relative Markdown link targets and heading anchors |
| [`verify-type-equiv`](https://github.com/deepseek-ai/deepseek-harness/blob/master/scripts/verify-type-equiv.ts) | Marked documentation declarations against their mapped source symbols |
| [`doc-typecheck`](https://github.com/deepseek-ai/deepseek-harness/blob/master/scripts/doc-typecheck.ts) | TypeScript examples covered by the documentation checker |

These checks have ordinary command-line entry points:

```bash
pnpm run verify-md-links
pnpm run verify-type-equiv
pnpm run doc-typecheck
```

DSH groups its documentation gates under `pnpm run doc-sync`. Another project
can use its own language and tools to compile examples, validate documented
schemas, or regenerate API references and reject stale committed copies.
The reference-back check proposed above would be an additional rule for our
spec convention.

The checker must discover the full set of relevant documents. A newly added
folder that falls outside its search pattern can make an incomplete check look
successful. Include that case when testing the checker itself.

### Review the meaning of the change

A valid link cannot establish that every affected requirement was updated.
A matching type declaration cannot establish correct error or cancellation
behavior. When specified behavior changes, the PR should identify the affected
specs and say whether each was updated or replaced in a particular area.
Reviewers can then trace those requirements into the code and tests.

This keeps the work focused: scripts catch structural inconsistencies, while
review checks that the documents still describe the intended behavior.

## 3. Run a Zombie Hunter Against Repository-Wide Contracts

Even with good specs and references, successive changes can leave the repository
inconsistent. A fix updates the primary API handler but misses a compatibility
route. A shared helper changes behavior for another feature. Several dependency
additions gradually violate the architecture. Each patch can pass its focused
tests while the combined project breaks a promise nobody re-examined.

A **Zombie Hunter** regularly checks whether the repository still satisfies its
overall contracts, including code untouched by the latest diff. It builds on
[agentic contract testing](/blog/llm-application/agentic-contract-testing): define
the promise, specify what an evaluation must cover, and require evidence for
the result.

### Define the promises the repository must keep

Give the evaluator an authoritative contract document. An API reference can
serve this purpose when it describes inputs, results, errors, side effects,
and compatibility guarantees. Endpoint signatures alone leave much of that
behavior unspecified.

For example, a section in `docs/contracts/api.md` could say:

```markdown
## api.user-lookup

### Must hold
Every public user lookup requires a non-empty user ID.
Missing or blank IDs never return a successful lookup.
A valid but unknown ID returns a not-found result.

### Coverage required
All public user-lookup routes, including aliases and compatibility routes.
ID parsing and normalization, including whitespace-only input.
Cached and uncached lookup paths.
```

The coverage requirement matters as much as the expected result. Testing only
`GET /users/{id}` cannot justify a pass if an older `GET /users/` route still
returns a default user. The evaluator must discover all relevant entry points,
including newly introduced ones.

Architecture contracts need the same precision. “Domain packages never import
transport packages” requires examining the relevant dependency graph.
“Every administrative action checks permissions where the action runs” requires
tracing the execution paths, including alternate callers. Checking a few
representative files is insufficient for either claim.

Keep each behavioral promise in one authoritative place: its owning spec, API
reference, or architecture document. Zombie Hunter contracts select the
assertions to evaluate and define the required coverage. They can reference
the owning document's sections or stable assertion IDs instead of copying the
behavioral definitions. If that document already contains the assertion and
coverage requirements, the runner can evaluate it directly.

### Combine programs with bounded agent investigation

Use a program for a mechanical assertion. A dependency checker can enumerate
forbidden imports; an API test can probe expected responses. Reuse these checks
rather than asking an agent to approximate them.

Use an agent when the investigation requires discovery and interpretation:
find every route that performs a lookup, trace shared middleware, inspect
configuration variants, or check alternate callers. Give it a particular
contract and coverage requirements. It can inspect source, run existing tests,
and perform controlled probes in an isolated environment.

Keep evaluation separate from repair. The investigator should report the
repository state it observed, without rewriting the contract or fixing code
to make the check pass. A finding can then lead to a reviewed change through
the spec-and-code workflow.

### Schedule the check and retain evidence

A daily CI job is a useful starting point. Evaluate a recorded repository
commit and contract revision, and attach the report to those versions. Cover
the relevant repository state, including files that have not changed recently.
Cheap assertions may also run on each PR; broader investigations can run on a
schedule or before a release.

A small runner can read the selected contract sections, invoke existing checks
and agent investigations, and save reports as CI artifacts. Each report should
identify the assertion, observations, verdict, and any coverage gaps. For the
lookup example:

```text
Contract: api.user-lookup
Subject: recorded repository commit and contract revision
Verdict: fail
Coverage: primary and compatibility lookup routes; ID normalization
Counterexample: GET /users/ returned 200 with a default user
Location: compatibility route in src/routes/users.py
Gap: cached lookup behavior was not evaluated
```

The counterexample establishes failure despite the remaining gap. A pass needs
evidence addressing all declared coverage requirements. If the runner cannot
enumerate dynamic routes, lacks credentials, or exhausts its budget, the
unresolved check is inconclusive. Finding no violation does not by itself
justify a pass.

Retain observations a maintainer can reproduce, such as requests and responses,
commands and exit codes, or offending dependency edges. An agent's conclusion
alone is insufficient. Test the evaluator against known violations so a broken
runner or incomplete search cannot silently turn the daily job green.

### Reconcile the finding with the intended behavior

A finding may reveal an implementation defect, an intentional change with a
missing contract update, an ambiguous requirement, or an evaluator error.
Establish which one occurred before deciding what to change.

Unintentional drift calls for a fix and regression evidence. An intentional
behavior change calls for the spec update or explicit replacement reference
from the second practice. Update the authoritative definition and any affected
evaluation references or coverage requirements together. The implementation's
current behavior is not, by itself, a reason to relax the assertion.

Feature acceptance asks whether one change satisfies its spec. The Zombie
Hunter asks whether the accumulated repository still honors its API and
architecture promises. That broader view can expose side effects and missed
updates that individual reviews did not catch.

## 4. Make Review a Repository-Owned Workflow

A reviewer needs to evaluate more than whether the new feature works. The change
may also violate a security rule, alter an existing API, weaken a test, or place
behavior in the wrong component. Repeating “review carefully” in every request
leaves the review procedure dependent on what that reviewer happens to remember.

Put the procedure in a repository-owned review skill. It should locate the
applicable rules, challenge the spec and implementation, select checks, and
produce a report that supports an acceptance decision. Link it from the contributor instructions so
both people and agents can find it.

### Establish the scope and applicable rules

Start with the exact base and reviewed revision. Include staged, unstaged, and
untracked changes when reviewing a worktree, and record which state the evidence
covers. Check that the required environment is available and that reported
checks actually ran against that state. A previous green result may no longer
apply after another edit.

Then find the owning specs, affected contracts, and repository instructions.
Follow references to security policies, architecture rules, testing guidance,
and style configuration.

DSH's [code review skill](https://github.com/deepseek-ai/deepseek-harness/blob/master/.agents/skills/dsh-code-review/SKILL.md)
uses this approach. It starts by verifying the base and head and running its
scope report, then points reviewers to repository rules, defensive patterns,
testing policy, and documentation standards. It prioritizes correctness,
lifecycle, security, and required behavior over stylistic findings.

### Select checks according to the change's effects

The review skill is extensible: any requirement that must be validated before
accepting a change can become part of its workflow. Keep each rule in its
authoritative location, define when it applies and what evidence satisfies it,
and have the skill discover and apply it. The areas below are examples, not an
exhaustive checklist.

| Area affected | What review should establish |
| --- | --- |
| Permissions or untrusted input | Authorization is enforced where actions run; alternate callers cannot bypass it; inputs and secrets are handled safely |
| APIs, schemas, or stored data | Consumers remain compatible, or the proposed change and migration are justified against consumer needs and compatibility policy |
| Shared components or dependencies | Ownership and dependency rules hold, and existing consumers still work |
| Async work or resource ownership | Errors, cancellation, retries, and cleanup preserve the required behavior |
| Published or user-facing behavior | Built entry paths, documentation, diagnostics, accessibility, and localization remain correct where applicable |
| Style, types, and performance | Configured lint/type checks pass, and relevant resource or performance budgets are tested |

Run mechanical checks through the repository's existing commands. Use semantic
review for questions those commands cannot settle: whether a new abstraction
is needed, whether a test asserts the right outcome, or whether a permission
check can be bypassed through another path. Trace affected consumers beyond the
edited lines.

Apply the rules according to scope. A wording correction does not need a
migration review or a new spec. An authorization change needs evidence beyond
formatting and unit tests. If a prerequisite blocks one check, record that gap
and continue independent checks without claiming the blocked behavior passed.

### Report defects and the limits of verification

A finding should identify the violated requirement, location, trigger, impact,
and evidence. For example:

```text
Requirement: cancellation preserves captured output.
Change: the cleanup path clears the output buffer before returning the result.
Trigger: stop a worker after it emits output but before it completes.
Impact: callers lose output that the worker spec promises to retain.
Evidence: source location and a regression test reproducing the loss.
```

Review should red-team both the spec and the implementation. Look for mistaken
assumptions, missing cases, unsafe decisions, and conflicts with existing
contracts or policies. Code can faithfully implement a flawed spec. For
example, a cancellation spec that permits discarding captured output deserves
challenge if callers rely on that output to diagnose failures.

An intentional behavior change needs explicit review of the changed requirement,
its effects on consumers, and compliance with applicable policies. Updating a
spec does not by itself justify the change. Findings can identify a defective
requirement as well as an implementation violation; explain the concrete impact
and supporting evidence in either case.

Alongside findings, report what was checked, what failed, and what remains
unverified. A review with no findings and missing security evidence is not
equivalent to a completed security review.

This review complements the Zombie Hunter. Review starts from a proposed diff
and traces its effects before acceptance. The Zombie Hunter starts from ongoing
contracts and investigates the accumulated repository state. They can share
checkers and report conventions while covering different opportunities for
mistakes. An agent can perform either investigation, but its conclusions still
need evidence that a maintainer can inspect.

## A Starting Point for Further Work

A minimal setup can use the repository's existing conventions:

```text
CONTRIBUTING.md              procedure and commands for contributors
AGENTS.md                   links agents to the same procedure
.agents/skills/code-review/  review workflow referencing existing policies
docs/spec-template.md       context, goals, decisions, alternatives, acceptance
docs/specs/                 specs with explicit replacement references
docs/contracts/             assertions, coverage, and links to their owners
scripts/check-docs.*         structure, references, and interface consistency
scripts/check-contracts.*    recurring evaluation and evidence reports
tests/                      acceptance and regression tests
CI configuration            PR checks and scheduled contract evaluation
```

Start with one substantive change and one important repository-wide promise.
Deliver the change with its spec and verification, and review it through the
repository's procedure. Add checks for the document references, then schedule
an evaluation of the broader promise. Expand the harness when an actual gap
calls for another check.

This puts [contract reconciliation](/blog/llm-application/contract-evaluation)
into everyday development. The reports also provide observations for
[improving the harness itself](/blog/llm-application/observability-manipulability-for-self-improving-harness).

Specs explain individual changes, references preserve continuity, the Zombie
Hunter checks the accumulated result, and the review skill brings the applicable
rules into each acceptance decision. Together, they give us a starting point
for keeping quality high as code changes faster. Later posts can develop these
practices as experience reveals what works and what is still missing.
