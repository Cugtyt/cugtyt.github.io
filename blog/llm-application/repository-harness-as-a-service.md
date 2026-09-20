# Towards Repository Harness as a Service

A user opens an issue: “Our team needs a shared equipment booking page. People
should be able to reserve a device, see when it is available, and cancel their
own reservations.”

Today, that request often starts a series of technical handoffs. Someone chooses
a framework, sets up an environment, writes code, runs tests, configures CI, and
deploys the application. An AI agent may help with each step, but the user still
has to coordinate the development process.

What if the repository could carry that request through to a usable service?
The user would discuss the intended behavior, try the result, and give feedback.
They would not need to understand the source language, install the toolchain,
or operate the deployment pipeline.

This is the direction I mean by **Repository Harness as a Service**: a harness
driven by an intent lifecycle. The user expresses a need and reviews the
resulting change; the harness manages the software lifecycle that realizes it.
The user's decision to accept, refine, or reject the change determines what
happens next. “As a service” describes this interaction. The harness could run
locally, inside an organization, or on a hosted platform.

The [previous post](/blog/llm-application/repository-harness) proposed four
repository practices: ship specs with substantive changes, maintain references
as behavior changes, check repository-wide contracts, and make review a
repeatable workflow. Those practices provide a foundation. This post explores
what must surround them to make a usable outcome the normal unit of delivery.

## The Intent Lifecycle Drives the Software Lifecycle

The equipment-booking request starts the outer loop: a user wants something to
change. The harness inspects the current repository, existing behavior, and
applicable constraints, then produces a concrete candidate: the spec,
implementation, and verification together.

The user reviews that candidate. By default, they can focus on a working preview
and an explanation of the current state, changes, impact, risks, and remaining
gaps. They can also inspect the full spec, code, and evidence. The explanation
translates the same spec and observed results into terms the user can judge.
It must preserve consequential decisions and uncertainties even when technical
detail is omitted.

The intent loop determines what should change and whether the result is
acceptable. Within it, the software loop builds and verifies the change:

```text
                         INTENT LOOP
  User intent ◀───────────────────────────────────────────────┐
       │                                                      │
       ▼                                                      │
                  SOFTWARE LOOP                               │
  Spec + implementation ◀──────────────────────┐              │
       │                                       │              │
       ▼                                       │              │
  Tests + engineering review                   │              │
       ├─ Revise ──────────────────────────────┘              │
       │ Ready                                                │
       ▼                                                      │
  Reviewable result + impact + risks                          │
       │                                                      │
       ▼                                                      │
  User review ── Refine ──────────────────────────────────────┤
       ├─ Reject → stop this change                           │
       │ Accept                                               │
       ▼                                                      │
  Release checks → deploy → verify service                    │
       │                                                      │
       ▼                                                      │
  Evaluate outcome ── Further change ─────────────────────────┘
       │ Need met
       ▼
  Ongoing operation and maintenance
```

These decisions govern the change's progression. The spec stays with the code
throughout that work and remains an active requirements document after delivery.
Later behavior changes update it or explicitly supersede the affected
requirements through a linked spec. Acceptance does not require rewriting the
spec into a different document format.

The harness can clarify consequential ambiguities when necessary and make
routine choices within established constraints. Spec and implementation arrive
together for review. With inexpensive code generation, a concrete result can
make the discussion more useful than an abstract description alone.

## Give the User a Concrete Change to Review

Suppose the repository currently contains an equipment inventory with company
sign-in but no reservations. The harness builds a private booking preview using
sample data. Its spec records the starting state, goals, non-goals, decisions,
alternatives, and acceptance criteria. The implementation and tests accompany
that spec.

The review presented to the user could say:

```text
Current state: members can view equipment but cannot reserve it.
Ready to try: a private booking preview using sample data.
Changes: members can reserve available devices and cancel their own bookings.
         Equipment managers can cancel any booking with a visible reason.
Impact: overlapping bookings are rejected; manager cancellation frees the slot.
Risk: cancellation sends no notification. A member may arrive expecting
      equipment after a manager has cancelled their booking.
Verified: concurrent booking rejection and cancellation permission checks.
Gap: company sign-in still needs verification in the production environment.
Next decision: accept this workflow, refine it, or reject the change.
```

This is a view of the candidate change and its evidence. The full spec explains
why manager cancellation was included and what alternatives were considered;
the preview lets the user experience its consequences.

The user might accept the workflow, subject to completing production checks.
They might refine it: “Managers can cancel, but the owner must receive a
notification.” The harness then updates the spec, implementation, and tests,
and returns with a revised preview and evidence. Or the user might reject the
booking approach because the team actually needs an equipment request queue.
The harness discards the candidate and returns to that intent without changing
production behavior.

The user is a reviewer with a choice of depth. Someone familiar with the code
can inspect the diff. Someone concerned with the team's workflow can try the
preview and examine the impact summary. Both are reviewing the same change.
Neither should have to install the development toolchain merely to evaluate it.

## Engineering Work Supports the Review Decision

Inside the software lifecycle, the harness prepares the environment, implements
the change, runs tests and CI, and builds the usable result. For the booking
service, verification includes concurrent attempts to reserve the same device,
cancellation by the wrong user, and the availability shown after cancellation.
A demonstration of the happy path cannot establish these promises.

The repository-owned review workflow challenges both the spec and the code.
For example, a spec might allow any signed-in user to cancel any reservation.
An implementation could follow that spec perfectly and still violate the team's
ownership expectations. Review needs to expose that design problem, as well as
implementation mistakes such as enforcing permissions only in the page while
leaving the API unprotected.

Failed checks lead to investigation and repair within this loop. A discovery
that materially changes cost, risk, feasibility, or behavior returns to the
intent discussion. If reliable notifications require a new paid service, the
harness should explain that consequence and the available choices. Routine
technical decisions remain its responsibility within the established limits.

The user’s acceptance establishes that the direction and result meet their
need. It does not turn a failed permission check into a pass. The harness must
complete applicable engineering checks before the corresponding delivery stage
can proceed. For the booking example, accepting the private preview can
advance the work toward production while production sign-in remains a required
check.

## Put Lifecycle Knowledge in the Repository

The harness needs reliable ways to prepare the environment, evaluate changes,
and deliver them. Those procedures must survive the conversation that first
established them. Existing repository tools can expose the necessary capabilities:

| Responsibility | What the harness needs |
| --- | --- |
| Prepare | Repeatable setup, dependency constraints, and declared external services |
| Implement | Active specs, architecture guidance, and rules for substantive changes |
| Verify and review | Test commands, inspectable results, and a skill that challenges requirements and code |
| Deliver | Build and deployment workflows identifying the artifact and target environment |
| Operate | Health checks, diagnostic access, recovery procedures, and contract checks |

The harness must verify the delivered result. A deployment command's successful
exit does not establish that the booking page is reachable in the intended
environment. Check the service through its real entry path and attach that
evidence to the release.

Keep a durable record connecting the intent, spec, code revision, verification,
user decisions, and deployed artifact. Acceptance should identify the candidate
and delivery stage it covers; a materially revised result needs renewed review.
Another agent run can then resume interrupted work and check whether a deployment
already happened before retrying it.

## Delegate Execution Within Clear Authority

The user establishes which environments the harness may use, what it may spend,
which data it can access, and when it may release. Within those limits, the
harness can complete ordinary work without asking the user to coordinate each
command.

For the booking service, that might allow previews with sample data and
production deployment after acceptance and passing checks. A user may also
delegate acceptance for a defined class of changes, such as routine dependency
patches that preserve behavior and pass required checks. Automatic release then
exercises authority granted through the intent lifecycle. Changes outside that
scope return to the user for review.

Moving private data to a new provider, exceeding the budget, or removing a
promised capability changes the agreement. The harness should explain the
consequence and the decision needed. When blocked, it should report progress
precisely: “The preview is ready; production requires access to the company
sign-in configuration.”

## Evaluate the Delivered Outcome

After release, the team may discover that choosing equipment is awkward on a
phone. Passing tests and accepting a preview cannot settle every question about
actual use. That observation becomes a refinement of the intent and triggers
another iteration of the software lifecycle.

The next review should explain what changed, which earlier decisions still
apply, and what remains unresolved. If adding notifications also changes who
can see booking details, that consequence belongs in the explanation. Reporting
only the requested feature would hide a decision the user needs to make.

The active specs and decision history give the harness the context for this
iteration. The user can describe the problem they experienced without
reconstructing the project's technical history.

## Delivery Starts an Ongoing Responsibility

Dependencies age, credentials expire, and external integrations change. The
service needs an agreed operational scope: what the harness monitors, what it
can repair, and when it must involve an owner.

Health checks can detect an unavailable booking API. Scheduled Zombie Hunter
evaluations can investigate whether all booking routes still prevent overlaps
and all cancellation paths enforce permissions, including code untouched by the
latest change. Failures lead to diagnosis and repair within the delegated scope.
Changing a promised behavior returns to the intent loop; the harness cannot
quietly weaken a contract to make a check pass.

Recovery also needs preparation. Reverting code may be insufficient after a
data migration. Release procedures should establish when rollback or a forward
repair is possible. Users need an account of what was affected, whether the
service recovered, and any decision that remains theirs to make.

## Towards an Outcome-Oriented Repository

A practical first step is one repository with one supported delivery path. Give
it a repeatable environment, the four quality practices, an automated preview,
and a release procedure. Take a real issue through that path and observe where
the user still has to translate intent into technical instructions. Each such
handoff identifies missing knowledge, tooling, or authority in the harness.

The intent lifecycle gives users a way to steer the work through concrete
results. They express a need, review its realization, and accept, refine, or
reject the change. The software lifecycle produces the spec, implementation,
and evidence that make those decisions informed. The repository harness
connects the two and carries accepted work through delivery and maintenance.

There are still questions to develop: how to measure successful delivery, how
much operational authority to delegate, and how to maintain quality as both the
software and its harness evolve. Repository Harness as a Service gives us a
direction for exploring them through working systems.
