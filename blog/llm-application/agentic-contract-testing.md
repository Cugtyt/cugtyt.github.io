# Agentic Contract Testing: Making Project Intent Executable

> TL;DR: An agentic contract test is a small, human-readable project promise. A human defines what must be true and what coverage is required to justify a result. An agent chooses how to investigate, while a harness controls execution. The output is a structured report whose passes are coverage-backed and whose failures are evidence-backed.

A project may promise that every administrative operation is authenticated, authorized, and audited. That promise can span routes, middleware, configuration, and runtime behavior. It is too broad for one unit test, but “ask an agent to review the repository” is too vague for CI.

Agentic contract testing sits between those approaches. A human states the project property that must hold. An agent decides how to inspect the project, exercise the implementation, and search for counterexamples. The result is not a free-form code review, but a bounded report with explicit coverage and inspectable evidence.

The contract is the oracle. The agent is an adaptive test runner.

## From Contract Evaluation to a Test

In [From Code Generation to Contract Reconciliation](/blog/llm-application/contract-evaluation), I described contract evaluation as the watcher in a software reconciliation loop. The contract is the desired state, the project is the observed state, and the evaluator reports drift so humans can decide how to reconcile it.

That describes the larger loop, but not its smallest executable unit. “Review the project against the documentation” leaves important questions unanswered:

- Which promise is being tested?
- Where does it apply?
- What must be true?
- What must be examined before a pass is credible?
- What evidence justifies a failure?

A conventional unit test fixes both the expected result and the procedure used to check it:

```text
arrange inputs
call a function
assert an output
```

An agentic contract test fixes the expected project state but leaves the evaluation procedure open:

```text
identify the promise
bound its subject
state what must be true
state the coverage needed for a pass
let an agent choose the observations and probes
require a structured, evidence-backed report
```

The evaluator may inspect source code, trace dependencies, read configuration, run existing tests, generate temporary probes, start a service, issue requests, or search for a counterexample. The exact procedure can adapt as the project evolves.

What it may not do is reinterpret the contract until the implementation passes.

Role | Responsibility
--- | ---
Contract author | Defines identity, subject scope, required conditions, and explicit coverage
Agent | Plans the investigation and interprets observations
Harness | Controls tools, isolation, permissions, budgets, and execution
Report | Mirrors the contract with per-condition verdicts and coverage evidence

The procedure may vary. The meaning of the test should not.

## A Minimal Contract Test

A contract test can remain small even when its evaluation is sophisticated. For example, it can be represented as a short YAML document containing an identity, a subject scope, and the conditions that must hold:

```yaml
id: architecture.model-selection

scope:
  include:
    - src/**

must:
  - Generic model-call operators must not select models based on tenant TPM capacity.
```

The fields in this example play distinct roles:

- `id`: a stable identity for the promise;
- `scope`: the project elements governed by the promise;
- `must`: the conditions that must all hold.

The representation can be extended when more precision is useful:

- `cover`: what the evaluator must account for before reporting a pass;
- `examples`: examples that clarify acceptable and violating behavior.

Humans author intent; machines record execution detail.

### `id`: stable identity

An ID such as `api.user-lookup` or `security.no-hardcoded-secrets` should remain stable when a test moves between files. It should not be derived from the filename. Namespaced IDs make collisions less likely and allow CI systems to retain history across reorganizations.

### `scope`: the subject of the promise

`scope` identifies the project elements governed by the contract:

```yaml
scope:
  include:
    - openapi.yaml
    - src/users/**
    - src/routes/**
  exclude:
    - generated/**
```

Paths are interpreted relative to the subject root, normally the repository root. Making the subject explicit avoids accidentally claiming something about generated code, vendored dependencies, build artifacts, or unrelated projects.

Subject scope is not necessarily the same as evidence access. Evaluating a route may require inspecting shared middleware, generated configuration, a dependency, or runtime behavior outside the governed paths. The contract says what the promise applies to; runner configuration says what the evaluator is permitted to read or execute.

### `must`: independently reportable conditions

Every item in `must` must hold for the test to pass:

```yaml
must:
  - Administrative operations must require authentication.
  - Administrative operations must verify administrative permission.
  - Every attempted administrative operation must produce an audit event.
```

Each item should be independently reportable. Avoid hiding unrelated requirements inside one long sentence. If conditions require different subject scopes or substantially different interpretations, make them separate tests.

The items do not need handwritten IDs. A report can reference their positions, repeat their text, and optionally record a digest of the normalized statement.

### `cover`: what makes a pass credible

`cover` describes what the evaluator must account for before it may report a pass:

```yaml
cover:
  - all public routes capable of returning a user
  - route aliases, compatibility paths, and fallback routes
  - user ID parsing and normalization
  - cached and uncached lookup paths
```

Coverage obligations describe completeness, not procedure. “Account for every compatibility route” is coverage; “run `grep`” is an instruction. The author controls the former, while the agent chooses the latter.

When `cover` is absent, the evaluator should explain what it examined and why that was sufficient. Different evaluators may make different choices, so a CI policy can require explicit coverage obligations before accepting a pass for high-value contracts.

### `examples`: clarifying the boundary

Examples communicate intent without becoming the normative contract:

```yaml
examples:
  pass:
    - Business logic selects a model and passes it to a generic model-call operator.
  fail:
    - The generic operator reads remaining TPM capacity and selects a model itself.
```

If an example conflicts with a `must` condition, the evaluator should report the ambiguity rather than silently choose an interpretation.

## A Worked Evaluation

Consider a service whose public contract says that user lookup requires a non-empty ID and that unknown users return a not-found response. The primary route follows the contract, but an old compatibility route remains:

```python
@app.get("/users/{user_id}")
def get_user(user_id: str):
    user = users.get(user_id)
    if user is None:
        raise HTTPException(status_code=404)
    return user

@app.get("/users/")
def legacy_user_lookup():
    return users["default"]
```

A contract test can express the promise without assuming where the violation will be found:

```yaml
id: api.user-lookup

scope:
  include:
    - openapi.yaml
    - src/routes/**
    - src/users/**

must:
  - Every public user lookup requires a non-empty user ID.
  - A missing, blank, or normalized-to-empty user ID must not return a successful response.
  - A syntactically valid but unknown user ID must return a not-found result.

cover:
  - every public route capable of looking up a user
  - route aliases, compatibility paths, and fallback routes
  - user ID parsing and normalization
```

A fixed test of `/users/{user_id}` might pass while never exercising `/users/`. An adaptive evaluator can enumerate the routes, trace both handlers, start the service, and probe the compatibility path. It then has a concrete counterexample: `GET /users/` returns `200` with the default user.

The important property is not that every evaluator follows those exact steps. It is that a failure contains an inspectable observation, while a pass must account for all three declared coverage obligations.

## An Example Report

One possible report mirrors the handwritten contract rather than introducing a second, more complicated object. In this example, result arrays correspond by position to the contract arrays: every `must` item receives a verdict, and every declared `cover` item receives evidence showing what the evaluator accounted for.

```yaml
id: api.user-lookup
verdict: fail

must:
  - verdict: fail
    evidence:
      - GET /users/ returned 200 with a default user.
      - src/routes/users.py:41-43 defines the compatibility handler.

  - verdict: fail
    evidence:
      - GET /users/ returned 200 with a default user.

  - verdict: pass

cover:
  - evidence:
      - inspected GET /users/{user_id}
      - inspected GET /users/

  - evidence:
      - inspected compatibility route GET /users/

  - evidence:
      - tested missing, blank, whitespace-only, and unknown IDs
```

`cover` does not need a `complete` verdict. Declaring coverage complete would merely ask the evaluator to certify itself. The evidence and known gaps allow a runner or reviewer to judge whether the coverage obligation was sufficiently addressed.

If the evaluator cannot satisfy a coverage obligation, it records the evidence it did obtain and the remaining gap:

```yaml
cover:
  - evidence:
      - inspected all statically registered routes
    gaps:
      - dynamically registered routes could not be enumerated
```

Unless a concrete violation already establishes `fail`, an unresolved coverage gap makes the result `inconclusive`.

Runner version, model, permissions, duration, subject revision, and contract digest are useful for auditing an execution, but they are not contract results. A harness may store them in an optional execution envelope or a separate audit record without complicating the primary report.

Useful evidence may include source locations, commands and exit codes, HTTP exchanges, dependency edges, logs, traces, generated artifacts, and replayable counterexamples. Reports should contain observable evidence rather than private model reasoning.

The evaluator may be probabilistic. Its reported claim should still be inspectable.

## Verdict Semantics

For the example to be useful, its global verdicts need consistent meanings rather than policies invented separately for each test.

### `pass`

The evaluator found no violation of any `must` condition within the declared subject scope, and the evidence for every required coverage obligation contains no unresolved gaps.

A pass is an evidence-bounded result, not proof that no violation exists. Its strength depends on the evaluator, available observations, and the coverage evidence in the report.

### `fail`

At least one `must` condition has a concrete, evidence-backed violation. One verified counterexample is sufficient to fail a universal promise.

The evaluator may stop before examining the remaining coverage after finding a verified violation, but the report must expose the resulting gaps. An unsupported opinion is not a failure.

### `inconclusive`

No verified violation was established, but the evaluator could not justify a pass. The contract may be ambiguous, coverage may be incomplete, authoritative evidence may conflict, or necessary observations may be unavailable.

This verdict is essential for evaluator independence. A weaker evaluator should report incomplete knowledge rather than convert uncertainty into a pass or fail.

### `error`

The evaluation did not execute correctly because setup, the harness, or the evaluator failed. An unavailable dependency or broken environment is not contract drift.

The two central rules are:

> A pass must be coverage-backed.

> A fail must be evidence-backed.

## Reproducibility and Trust

Agentic evaluation introduces risks that deterministic tests do not. Repository content may contain instructions intended to manipulate an evaluator. Generated probes may execute unsafe code. Source inspection may expose credentials, and network access may leak them.

A production runner should therefore:

- treat repository text as untrusted data, not evaluator instructions;
- evaluate an immutable project snapshot;
- isolate generated scripts, tests, logs, and other temporary artifacts;
- disable network access by default;
- expose secrets only when a test explicitly requires them;
- restrict commands, writable paths, processes, time, and compute;
- record material permissions and environment details in an execution audit record.

Results also depend on evaluator capability. Different models, tools, or budgets may discover different violations. The primary report cannot remove that variability. An optional execution audit record can make runs more comparable by recording the contract digest, subject revision, runner and model versions, and execution policy without mixing those details into the contract result.

For high-risk contracts, a project may require repeated evaluation, multiple independent evaluators, or deterministic confirmation of discovered counterexamples. Model independence does not mean every evaluator is equally capable.

## Toward Interchange

The YAML representation in this article is illustrative, not a fixed contract schema. Projects can choose their own file layout and serialization while applying the same separation between human-authored promises, adaptive evaluation, and evidence-backed results.

If an ACT interchange specification eventually emerges, its boundary should remain small. It could define field meanings, verdict and coverage semantics, evidence requirements, and a report schema. It should not standardize prompts, private chain-of-thought, model parameters, planner implementations, tool APIs, multi-agent topology, or orchestration frameworks.

Reaching that point requires more than this proposal: a formal schema, reference fixtures, at least one runner, and a conformance suite are still needed.

## Relationship to Existing Tests

Agentic contract tests do not replace unit tests.

Dimension | Unit test | Agentic contract test
--- | --- | ---
Target | Function, class, or module | Project-level promise
Expectation | Code assertion | Human-readable required conditions
Procedure | Fixed by the test author | Selected adaptively by the evaluator
Scope | Usually local | May span code, docs, config, and runtime
Pass condition | Fixed assertions succeed | No violation found and coverage evidenced without gaps
Failure output | Assertion and stack trace | Evidence-backed finding or counterexample

A unit test is better when the procedure is known and deterministic. An agentic contract test is useful when the intended property is clear but the implementation path is distributed, evolving, or difficult to encode as one fixed test.

The two can reinforce each other:

```text
contract test
     |
     v
agent searches for drift
     |
     v
concrete counterexample
     |
     v
deterministic regression test
```

Once an evaluator discovers a stable failure mode, that counterexample should usually become a conventional unit, integration, architecture, or end-to-end test. Agentic evaluation searches the semantic space; deterministic tests preserve what the project has learned.

“Contract testing” also commonly refers to validating interactions between service consumers and providers. Tools such as [Pact](https://docs.pact.io/) focus on whether requests and responses conform to a shared integration contract. Agentic contract testing can evaluate such a contract, but the proposed primitive is broader: it can express an architecture boundary, CLI guarantee, compatibility promise, security policy, migration rule, or other project-level intention.

## Limits

This approach does not make probabilistic evaluation deterministic. It cannot guarantee that an evaluator will discover every violation, and natural-language conditions can still be ambiguous. Broad promises may be expensive to investigate, while vague coverage obligations may create results that look stronger than they are.

Agentic contract tests should therefore be used for promises whose meaning can be reviewed, whose subject can be bounded, and whose coverage can be explained. They complement formal verification and deterministic tests; they do not weaken the need for either.

## The Workflow

The practical loop is:

1. Humans write important project promises as small contract-test objects.
2. A runner validates the contracts and evaluates an immutable project snapshot.
3. The agent chooses observations and probes within harness policy.
4. The runner emits per-condition verdicts and per-obligation coverage evidence.
5. Humans review failures and inconclusive results.
6. Reconciliation changes the code, the contract, or both under supervision.
7. Stable counterexamples become deterministic regression tests.

Agentic contract tests do not make an agent's judgment automatically trustworthy. They make its claims bounded and reviewable.

Humans define the promise and the coverage required to justify a result. The evaluator chooses how to investigate. The harness controls execution. The report records what was observed.

> Identify the promise. Bound its subject. Require coverage. Let the agent search—and require evidence for what it claims.
