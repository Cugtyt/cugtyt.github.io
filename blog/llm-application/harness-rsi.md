# Towards Harness RSI: Evolving the System That Does the Work

A repository harness captures what we have learned about working with coding
agents. We add specs because intent gets lost, skills because useful procedures
repeat, tools because information is difficult to reach, and review workflows
because plausible code can still violate a contract.

But everything those practices depend on keeps changing. Models become more
capable. Tools expose better interfaces. Skills gain new techniques. The
repository grows, and its users ask for different things. A workflow that helped
one model finish a task may waste the next model's time. A manual procedure may
become a single tool call.

**The core problem is that the dependencies of a solution keep changing, so the
solution must keep adapting.** A harness built for a particular combination of
models, tools, skills, and repository needs cannot be assumed to remain suitable
as that combination evolves. Even a harness that works well today needs a way
to reconsider its design tomorrow.

This is the problem that motivates **harness recursive self-improvement, or
harness RSI**, in this post. The goal is an ongoing capacity to adapt the harness
as its foundations change. A loop built around feedback signals is one approach
to that goal: observe changes and outcomes, revise the harness, and evaluate
whether the revision fits the new conditions. A coding harness provides a
concrete starting example.

## The Core Problem: Dependencies Keep Changing

In [Towards a Repository Harness for AI Coding](/blog/llm-application/repository-harness),
I proposed four practices: deliver specs with substantive code changes, maintain
their references, check repository contracts regularly, and make review a
repository-owned workflow. These practices establish a useful starting point.
Their implementation should continue to evolve.

A review skill might initially require several explicit investigation steps
because the model otherwise misses relevant constraints. Later, a stronger model
and a tool that retrieves those constraints may make the sequence unnecessary.
The requirement to check the constraints remains; the procedure for finding
them changes.

This is already a concrete engineering concern. Anthropic describes adding
context resets to address premature stopping in one model, then finding those
resets unnecessary with a later model. Its discussion of
[Managed Agents](https://www.anthropic.com/engineering/managed-agents) explicitly
connects harness evolution to assumptions that become stale as models improve.

If every failure adds an instruction and nothing ever removes one, a harness
accumulates the limitations of all its previous models. Improvement must include
deletion, consolidation, and replacement. Each practice needs evidence for why
it still earns its place.

## What I Mean by Harness RSI

> Harness RSI is an agent system's capacity to continually adapt its own
> harness as the models, tools, skills, and conditions it depends on change,
> including adapting the machinery that enables further improvement.

This definition separates the adaptation problem from a particular method for
addressing it. The rest of this post explores feedback-driven iteration as one
practical approach. Other triggers, such as a model release or a new tool
interface, can initiate adaptation before failures appear in task records.
Feedback helps determine whether the resulting change is useful.

The object being changed matters:

| Improvement target | What changes | What the change can enable |
| --- | --- | --- |
| Model | Weights, training procedures, or model architecture | Different learned capabilities |
| Inference infrastructure | Kernels, scheduling, memory management, or serving systems | Faster, cheaper, or more reliable model execution |
| Agent harness | Skills, tools, instructions, context management, and workflows | More effective use of the available model on tasks |

These layers can reinforce each other. They still require different evidence.
A faster inference engine does not by itself demonstrate better reasoning, and
a better coding workflow does not imply that model weights have improved.

Z.ai's [account of GLM helping build its inference infrastructure](https://z.ai/blog/glm-built-its-inference-infrastructure)
illustrates the relationship: an agent helps improve the system that runs a
model. The account emphasizes local, attributable feedback from correctness
checks, profiling, and performance experiments, with humans retaining
responsibility for objectives and consequential decisions. It explicitly says
the work has not yet reached RSI. For harness design, the useful lesson is how
engineering feedback lets the agent select and test its next action.

The recursive part of harness RSI deserves similar care. Revising one skill
establishes an improvement cycle. Recursion becomes more concrete when the
improved harness also supports the next cycle: a better trace tool helps the
retrospective diagnose failures; a better experiment runner helps it compare
candidates; a better retrospective skill helps it choose worthwhile experiments.

The system is improving some of the machinery through which it improves.
That describes a design direction. It does not establish unlimited progress,
autonomous goal setting, or an accelerating rate of improvement.

## Public Work Already Points in This Direction

There are public examples of important parts of this loop. OpenAI's
[harness engineering account](https://openai.com/index/harness-engineering/)
describes feeding agent difficulties back into repository tools, documentation,
and enforceable constraints. Anthropic describes
[using Claude to improve its own tools](https://www.anthropic.com/engineering/writing-tools-for-agents)
through evaluation and transcript analysis.

Research also addresses automatic harness evolution directly.
[Agentic Harness Engineering](https://arxiv.org/abs/2604.25850) proposes a loop
combining editable components, inspectable experience, and predictions checked
against subsequent outcomes. Its reported experiments provide evidence for
bounded harness optimization.

These examples make harness RSI a useful subject for practical discussion
today. The open question is how to turn such mechanisms into an ongoing
capability that remains useful as models, tools, and workloads change. A gain on
a particular evaluation is evidence about that setting; maintaining improvement
across generations requires further work.

## One Approach: Two Loops Connected by Feedback

Changing dependencies create the need to adapt; feedback provides evidence for
how to adapt and whether a proposed solution works. A useful loop should
therefore consider changes in available capabilities as well as signals from
completed tasks. Waiting only for errors would miss opportunities created by
better models and tools.

The working agent and the improvement mechanism operate at different time
scales. The working agent handles the current request. The improvement mechanism
studies experience across requests and changes the environment for later work.

```text
WORK LOOP
User intent -> current harness + model -> result -> acceptance feedback
                       ^                                |
                       |                                v
                       |                      traces and outcome records
                       |                                |
IMPROVEMENT LOOP        |                                v
                       |                    diagnose a recurring mechanism
                       |                                |
                       |                                v
                       |                    propose a bounded harness change
                       |                                |
                       |                                v
                       |                    compare candidate with baseline
                       |                         /              \
                       |                     accept          reject/revise
                       |                       |                  |
                       +-- adopt new version <-+                  |
                                               evidence <---------+

The adopted harness also equips the next improvement cycle.
Model and tool changes trigger fresh comparisons of existing practices.
```

My earlier post,
[Observability and Manipulability: The Eyes and Hands of Self-Improving Harnesses](/blog/llm-application/observability-manipulability-for-self-improving-harness),
focused on the interfaces that make this possible. Observability exposes the
evidence needed to identify a target. Manipulability exposes the surfaces on
which a bounded change can be made.

Harness RSI adds the question of continuity: how does an accepted change become
part of the next working system, and how does that system produce evidence for
the next improvement?

Feedback must connect an outcome to a changeable mechanism. “The task took too
long” leaves many explanations open. Records showing repeated searches for the
same API contract suggest a specific investigation. The retrospective must
still test that explanation; a plausible story about a trace is a hypothesis.

Successful tasks matter too. They can reveal a reliable technique worth sharing,
or show that a newer model completes work without an old intervention. Failure
analysis alone would miss opportunities to simplify the harness.

## A Coding Harness as the Starting Example

Consider an illustrative repository with specs, a review skill, contract checks,
and records of completed coding tasks. The following is a proposed workflow,
not a report of measured results.

### 1. Find a recurring cost

A retrospective notices that agents repeatedly spend time locating the specs
and validation commands relevant to changed files. Some reviews also miss
requirements outside the edited directory. The final patches often work, but
the user has to point out missing checks.

The retrospective gathers several examples, including successful reviews. It
records the model, harness version, repository revision, tool calls, checks run,
and user corrections. It investigates whether the problem is missing
information, poor retrieval, or a review procedure that fails to use information
already available.

This distinction determines the intervention. Repeating “read the specs” would
not repair a broken reference map.

### 2. Turn the diagnosis into an experiment

Suppose the evidence supports a retrieval problem. The candidate change is a
repository tool that returns declared links from changed areas to relevant specs
and validation commands, together with a narrow update to the review skill.
The tool exposes its sources and reports gaps so the agent can investigate
beyond its results.

The proposal makes a prediction: reviews will spend less effort rediscovering
known relationships while preserving detection of contract violations. It also
names a failure condition: if agents treat incomplete results as exhaustive,
review quality may decline.

The experiment has an explicit scope, a baseline, and criteria for rejection.
Its purpose is to test the mechanism before making the procedure routine.

### 3. Evaluate on fresh executions

Run the old and candidate harnesses on comparable tasks from the same starting
repository states, with the same model and resource limits. Include cases
outside those used to design the tool: changes spanning directories, missing
links, stale references, and ordinary local fixes.

Historical transcripts help diagnose the problem. They cannot show how a
different harness would have acted. That requires fresh agent runs. Repeated
trials help distinguish a durable effect from a lucky trajectory.

Compare whether the reviews find known violations, which checks they actually
perform, how much human correction they require, and their time and token cost.
A faster review that misses relevant requirements should fail acceptance.

### 4. Adopt, then keep observing

If the evidence supports the candidate, adopt a versioned change with its
rationale, evaluation results, and a way to restore the previous version.
Subsequent real tasks provide another source of feedback. A regression can
justify rollback or a new experiment.

The same retrieval tool can now help the retrospective locate the contracts
governing its own proposed changes. Improving the working harness has also
improved part of the improvement workflow. Whether that actually makes later
cycles more effective remains something to measure.

### 5. Revisit the solution after an upgrade

Later, a new model or repository search tool becomes available. The retrospective
tests whether the custom retrieval procedure still adds value. It may retain
the source links while removing a redundant script or shortening the skill.

Evaluate both harness variants under the new model. If useful, also compare
both under the old model to understand the interaction. Comparing only the old
model with the old harness against the new model with the new harness would
confound two changes.

The contract remains that reviews examine relevant requirements. The evidence
determines which procedure best supports that contract now.

## What Should Count as Improvement?

A harness has several objectives. Correctness, completion rate, latency, cost,
and human supervision can move in different directions. An improvement proposal
should state the tradeoff it intends to make and the constraints it must preserve.

For a coding harness, I would start with four questions:

- Does it deliver changes that satisfy the user's intent and repository contracts?
- Does it preserve successful behavior on tasks beyond the motivating examples?
- Does it reduce total effort, including human correction and review?
- Does the expected benefit justify the cost of discovering and maintaining it?

The last question is easy to overlook. An optimizer can spend far more compute
than its proposed change will save. Experiments need budgets and stopping rules.
For a frequently used workflow, a small saving may repay substantial evaluation;
for a rare task, a local solution may be enough.

Acceptance also needs some independence from the candidate. An improver can
propose new evaluation cases, but changing a workflow and weakening its grader
in the same experiment undermines the comparison. Keep acceptance criteria
fixed during that comparison and review changes to those criteria separately.

Held-out tasks, regression cases, and later operational feedback provide
different checks. Repeatedly tuning against the same held-out set eventually
makes it part of development, so evaluations need renewal as experience grows.
Neither a passing test suite nor the improver's explanation is sufficient
evidence of general progress.

## Improving the Improvement Mechanism

The retrospective itself has limitations. It may overreact to memorable failures,
propose instructions when a tool change would help more, or spend too much effort
on low-value patterns. Those behaviors can become improvement targets.

For example, a retrospective might repeatedly fail to attribute a regression
because records omit harness versions. Adding version information makes future
comparisons more interpretable. Another might discover that experiments are too
expensive to repeat and propose a smaller, representative screening suite before
the full acceptance evaluation.

These changes need evaluation at their own level: better attribution, more
reliable candidate selection, or lower experiment cost without worse decisions.
Producing more proposed patches is not enough.

This recursion needs a boundary. The system can improve its diagnosis and
experimentation procedures while humans retain authority over goals,
consequential tradeoffs, and the criteria for accepting changes to those
procedures. Human review is compatible with a useful self-improvement loop.
Autonomy can expand where evidence supports it.

## Build for Continuing Adaptation

The starting requirement is that the harness can change with its dependencies.
The feedback loop described here is a practical way to support that requirement.

A first implementation can be modest: preserve useful task records, run a
periodic retrospective, propose one bounded harness change, compare it with the
current version, and keep the evidence whether the proposal succeeds or fails.
There is no need to make every part of the harness editable at once.

The important transition is making harness maintenance an explicit part of the
system's work. Model upgrades and new tools become reasons to re-evaluate
assumptions. Repeated friction becomes material for experiments. Accepted
improvements become infrastructure for both ordinary tasks and later
improvement cycles.

The repository practices we use today can be the starting point. Their
foundations will keep changing, so the solution must keep adapting. Harness RSI
asks how the system can sustain that adaptation, including improving its own
ability to adapt. Feedback loops give us one concrete way to begin.
