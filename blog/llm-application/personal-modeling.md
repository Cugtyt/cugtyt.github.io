# Personal Modeling Through Models and Harnesses

## Contact Me

- Blog: <https://cugtyt.github.io/blog/llm-application/index>
- Email: <cugtyt@qq.com>
- GitHub: [Cugtyt@GitHub](https://github.com/Cugtyt)

---

In [Two Signals for Harness RSI](/blog/llm-application/signals-for-harness-rsi),
I discussed how a personal agent can learn from a user's instructions,
corrections, and choices. These signals help the harness adapt to how that
person wants to work. A correct result becomes more useful when it also fits
the user's goals, preferences, and circumstances.

This suggests a broader direction. As an agent learns to serve a person, it
accumulates a representation of that person. The model supplies general
capabilities; the harness supplies personal context and procedures for using
those capabilities. Together, they can become an executable model of how the
person might choose, respond, and work in a particular situation.

**Personal modeling could connect individual agents to population simulation.**
If we can build useful models of many people, we can explore their different
needs, study demand, and investigate how work might be organized. Recommendation,
advertising, and labor modeling become applications of the same underlying
question: what would these people do under these conditions?

## A Personal Harness Fits a Person Across Domains

A domain harness organizes an agent around a kind of work. A coding harness
might provide repository tools, validation procedures, and review workflows.
A personal harness has another organizing principle: the person it serves.
That person's priorities continue across writing, shopping, planning, learning,
and professional work.

Consider someone who values control over their schedule, dislikes maintaining
complex tools, and prefers paying more when it reliably saves time. Those
priorities could affect which software they adopt, which trip they book, and
how they delegate a project. Each domain needs its own knowledge and tools;
the personal harness helps apply them according to the same person's context.

This makes personal fit a central objective for a personal agent. General
competence establishes what the system can do. Personal adaptation helps
determine which of those capabilities are useful now, which tradeoffs to
present, and when to ask the user to decide.

The [harness RSI loop](/blog/llm-application/harness-rsi) can sustain that fit.
It observes mismatches, proposes changes to memory or workflow, and evaluates
whether later interactions improve. Its target includes both changing technical
dependencies and a person whose circumstances and priorities also change.

## The Person Model Lives in the Whole Agent

Personal modeling does not require training separate model weights for every
person. A shared foundation model can interpret different personal memories,
instructions, and histories through different harnesses.

A useful conceptual representation is:

```text
shared model capabilities
          +
personal harness
  memories and supporting evidence
  goals, preferences, and constraints
  tools and working procedures
          +
current situation and available choices
          |
          v
predicted response or proposed action
```

The representation is distributed. A memory may record that the user avoids
overnight travel. A planning procedure may prioritize uninterrupted work time.
A tool may expose the calendar constraints that make an otherwise attractive
option impossible. The model brings these pieces together when considering a
new situation.

This is more expressive than a list of interests. It can represent conditional
tradeoffs: a person may prefer the cheapest option for routine purchases but
pay for reliability when a deadline matters. A useful model preserves the
conditions under which a preference applies and the evidence supporting it.

There is also a distinction between helping someone and predicting them. An
assistant may recommend a new habit that would help its user, while a simulator
tries to predict whether the person would actually adopt it. These purposes
need explicit objectives and separate evaluation, even when they use the same
personal context.

## From Personal Models to Virtual Populations

Once a person model can respond to scenarios, we can assemble many such models
into a virtual population. We could present a new service, vary its price or
features, and examine how responses differ across people and circumstances.
The result could expose competing needs that an average preference hides.

There is research evidence for parts of this direction.
[LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals](https://arxiv.org/abs/2411.10109v3)
built agents using interviews, surveys, or both from 1,052 Americans and
evaluated predictions on held-out survey items and other behavioral measures.
This supports investigating agents grounded in evidence about individuals.
The continuing personal harness proposed here extends that direction toward
learning through ongoing assistance.

Population modeling introduces another layer. A collection of independent
responses can estimate a distribution of preferences under a fixed scenario.
Modeling adoption over time also requires assumptions about how people influence
each other, share resources, and encounter changing prices or availability.
A product that looks attractive to every isolated agent may become less useful
when everyone competes for the same limited service.

Scale therefore involves both the number of represented people and the
environment connecting them. Copying one agent many times adds simulated
responses without adding evidence about additional people. A population needs
coverage of the relevant differences and an explicit account of who is missing.

## Recommendation and Advertising Through Personal Simulation

Simulation already has a place in recommender research. Google's
[RecSim](https://research.google/pubs/recsim-a-configurable-simulation-platform-for-recommender-systems/)
provides configurable environments for sequential recommendation, including
assumptions about user preferences, changing states, and response behavior.
Personal models suggest a way to investigate richer user representations
within this broader simulation approach.

For example, imagine a service for learning a professional skill. A virtual
population could compare a cheap course requiring a fixed weekly schedule,
a flexible course with less support, and a more expensive course with coaching.
The simulation could explore which constraints drive rejection, which groups
remain underserved, and which product changes are worth testing with people.

This could move recommendation toward evaluating how an option fits a person's
current goals and constraints. Advertising could use related simulations to
explore whether an offer addresses a need, which information helps people
assess it, and how interest changes with price or timing. These are hypotheses
for real experiments; simulated interest alone does not establish demand or
incremental sales.

The objective matters. A personal agent chooses on behalf of its user. An
advertising system may optimize a seller's return. The same representation can
produce different decisions under those objectives. Sharing a personal model
with another system should therefore be a separate, user-controlled decision,
with a defined purpose and limits on the information exposed.

One possible design keeps the detailed personal context with the agent. An
external service submits an offer, and the agent evaluates it locally against
the user's needs. Population analysis could use permitted aggregate results.
The access boundary becomes part of the system design rather than assuming
that personalization requires exporting a person's history.

## Understanding Needs and Modeling Work

The same approach could explore needs before a product exists. Suppose many
agents struggle to find a service satisfying their users' scheduling,
accessibility, or budget constraints. Those repeated mismatches suggest demand
that the current catalog does not meet. A population simulation could help
formulate and compare possible services before a team invests in building one.

Work adds the supply side. Personal models could represent aspects of a
worker's skills, availability, preferred tasks, coordination habits, and
willingness to accept different assignments. Combined with a task environment,
they could help explore staffing, training, and collaboration between people
and agents.

For example, a team considering an AI tool could simulate several ways of
distributing research, implementation, and review. Different scenarios might
reveal where supervision becomes a bottleneck or where a new skill would make
someone more effective. The output would be a set of assumptions and predicted
outcomes to test in actual work.

Predicting a person's preferences does not establish their productive capacity.
A simulated worker needs evidence about task completion, quality, time, and
coordination under relevant conditions. An agent that writes a convincing
account of someone's work has not demonstrated that it can perform that work.
Using an agent to carry out tasks also requires its own tools, access, and
execution checks.

With those distinctions, personal modeling offers a way to study demand and
work together: what people need, what they are willing and able to do, and how
new tools might change the relationship between the two.

## Validate the Model Against the Person

The central test is whether the model predicts useful aspects of its person's
behavior on new situations. A plausible explanation is easy to mistake for
understanding. Evaluation needs choices and outcomes that were unavailable
when the relevant personal representation was built.

For individual models, compare predictions with later decisions and track
where the model is uncertain. For populations, compare predicted distributions
with observed responses, including differences between groups. Check whether
personal context improves predictions over a shared model given only the
scenario or broad demographic information.

Models sharing the same foundation model may also share errors. More simulated
agents cannot remove a common mistaken assumption. Real observations are needed
to identify those errors and revise the representation or environment.

Personal models must remain correctable as people change. A person should be
able to inspect, revise, or remove the memories and inferences used to represent
them. Predictions should retain their context and uncertainty, especially when
they inform decisions about opportunities or work.

## Personal Adaptation as a Foundation for Population Modeling

The immediate value of a personal harness is better assistance for one person.
Ongoing interaction gives it opportunities to learn which goals, constraints,
and working methods matter, then test that understanding through later work.

That creates a path toward a broader capability:

```text
personal assistance and feedback
              |
              v
model and harness adapted to an individual
              |
              v
validated predictions in new situations
              |
              v
populations with explicit environments and interactions
              |
              v
experiments on demand, recommendations, and work
              |
              v
real outcomes that refine the models
```

The opportunity is to make accumulated personal understanding usable across
scenarios. A harness that increasingly fits one user can become a foundation
for modeling that person's choices. Many validated person models, connected
through an appropriate environment, could help us understand groups and design
services and ways of working around their different needs.
