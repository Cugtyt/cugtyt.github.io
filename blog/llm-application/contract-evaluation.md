# Docs as Spec, Code as Status

AI coding makes implementation cheaper.

That changes the real bottleneck.

When code was expensive to write, human review naturally focused on the code
itself. A reviewer could inspect the diff, reason through the implementation,
and decide whether the change was acceptable.

When agents can produce large patches quickly, this model starts to break.
The reviewer is no longer only checking one human's carefully prepared change.
The reviewer is supervising a project state that may be changed by many sources:

- humans
- coding agents
- refactoring agents
- generated code
- dependency upgrades
- quick production fixes
- experiments that quietly become permanent

The codebase becomes a fast-moving state machine.

The problem is not only whether the latest patch works.

The deeper problem is whether the current project still matches the contract it
is supposed to satisfy.

## The Core Gap

Most projects have some form of expected behavior.

It may be an OpenAPI spec, a README, a CLI help page, a design doc, an
architecture decision record, a migration guide, or a set of acceptance
criteria.

But these contracts are often weakly enforced.

Sometimes the contract is missing.
Sometimes it exists as static text.
Sometimes it is spread across docs, tests, examples, and maintainer memory.
Sometimes it was correct last week, but the code has moved since then.

Code changes quickly.
Contracts change slowly.

That gap creates contract drift:

```text
expected behavior
        |
        |  weak or delayed enforcement
        v
current project behavior
```

Contract drift is not just a bug.
It is not just stale documentation.
It is the loss of alignment between what the project says should be true and
what the project currently does.

Once this happens, the project becomes harder to maintain.

Humans must rediscover intent from implementation details.
Agents receive conflicting signals about what to follow.
Review becomes less about judging a known contract and more about reconstructing
the contract from scattered evidence.

That is expensive.

## A Public Example

Imagine a small REST service with an OpenAPI contract:

```yaml
paths:
  /users/{id}:
    get:
      parameters:
        - name: id
          in: path
          required: true
      responses:
        "200":
          description: user found
        "404":
          description: user not found
```

The public promise is simple:

- `id` is required
- a known user returns `200`
- an unknown user returns `404`

Now the implementation changes.

Maybe a human adds a compatibility path.
Maybe an agent refactors routing.
Maybe a framework upgrade changes how empty path parameters are handled.

After the change, `/users/` returns `200` with a default user.

The service still runs.
Some tests may still pass.
The patch may even look reasonable in isolation.

But the contract is broken.

The expected state says `id` is required.
The observed state says an empty `id` is accepted.

This is exactly the kind of drift that is easy to miss in code review and easy
for future agents to build on incorrectly.

## Contract Evaluation as Watch Loop

Kubernetes gives a useful mental model.

In Kubernetes, desired state lives in `spec`.
Observed state lives in `status`.
Controllers watch the difference and reconcile the system.

Software development can use the same shape:

| Kubernetes | Development |
| ---------- | ----------- |
| `spec` | contract, docs, schemas, acceptance criteria |
| `status` | code, tests, examples, runtime behavior |
| watch loop | contract evaluation |
| reconciliation | code or contract updated under supervision |

The contract evaluator is the watch mechanism.

It links expected behavior to current project state.
It walks through the contract.
It observes the implementation, tests, examples, or runtime behavior.
Then it reports drift:

```text
expected: /users/{id} requires id
observed: /users/ returns 200 with a default user
verdict: contract drift
```

The evaluator should be read-only.

Its job is not to silently rewrite the code.
Its job is not to edit the docs to justify the implementation.
Its job is to make the mismatch visible.

After that, reconciliation is a supervised decision:

- change the code to restore the contract
- change the contract because the new behavior is intentional
- add acceptance tests so the decision becomes enforceable
- clarify the contract because it was ambiguous

The important part is that drift becomes explicit.

## Human Supervision Moves Up

This is the trend AI coding pushes us toward.

Humans should not spend all their effort reading every generated line forever.
As code generation becomes cheaper, line-by-line review becomes a weaker
control surface.

The stronger control surface is the contract.

Humans are better used designing:

- what behavior is acceptable
- which interfaces are public
- which examples must keep working
- which compatibility promises matter
- which architectural boundaries should not be crossed
- which risks require manual judgment

Agents can produce code against that contract.
Evaluators can check the project against that contract.
Humans supervise the contract and the reconciliation decisions.

The workflow becomes:

```text
human designs acceptance contract
        |
        v
human or agent changes code
        |
        v
contract evaluator watches project state
        |
        v
human supervises reconciliation
```

This does not remove human responsibility.

It moves human responsibility to the layer where it has the most leverage.

## Designing Good Contracts

A useful contract does not have to be perfect or fully formal.

It only needs to make the important expectations visible enough to evaluate.

For a web API, that may be an OpenAPI spec plus a few example requests.

For a CLI tool, it may be the README, `--help` output, exit-code rules, and
golden examples.

For a library, it may be public API docs, executable examples, and compatibility
notes.

For an infrastructure project, it may be policy rules, Terraform plans,
runbooks, and architecture decisions.

The common pattern is:

```text
expected contract
        |
        v
observable project state
        |
        v
drift report
        |
        v
supervised reconciliation
```

Tests still matter.
Static checks still matter.
Code review still matters.

But they become part of a larger supervision loop.

The goal is not to replace engineering judgment.
The goal is to give judgment a better object to inspect.

## The Practice

For agentic development, the practical steps are simple:

1. Write down the contract.
2. Define acceptance criteria.
3. Make project behavior observable.
4. Add a read-only contract evaluator.
5. Run it during review, before merge, or in CI.
6. Let humans decide how to reconcile drift.

This turns a fast-moving codebase into something watchable.

The project no longer relies only on humans noticing every important behavior
change inside every patch.

Instead, humans define the expected behavior, agents help move the code, and
contract evaluation watches whether the current state still matches the intent.

That is the spec/status loop for AI coding:

> Code moves fast. Contracts keep it steerable. Evaluation keeps it honest.
