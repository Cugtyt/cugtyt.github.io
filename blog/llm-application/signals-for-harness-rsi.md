# Two Signals for Harness RSI: Verifiable Outcomes and Personal Preferences

## Contact Me

- Blog: <https://cugtyt.github.io/blog/llm-application/index>
- Email: <cugtyt@qq.com>
- GitHub: [Cugtyt@GitHub](https://github.com/Cugtyt)

---

In [Towards Harness RSI](/blog/llm-application/harness-rsi), I discussed how an
agent system can keep adapting its harness as models, tools, skills, and
conditions change. Feedback helps the system decide what to change and whether
the change improves its work.

But feedback comes in different forms. Some tasks provide a clear result: a
math answer is correct, a program passes a test, or a player wins a game. Other
tasks depend on something the system cannot directly observe: what this user
prefers, how they want the agent to work, and what makes a result useful to them.

**Harness RSI needs to improve both task performance and its understanding of
the individual user.** A personal agent can complete a task correctly and still
leave its user repeatedly asking for a different tone, level of detail, or way
of working.

## When the Target Is Verifiable

Reinforcement learning from verifiable rewards, or RLVR, gives a model a reward
based on an outcome that can be checked. The
[DeepSeek-R1 paper](https://arxiv.org/abs/2501.12948) describes accuracy rewards
for tasks such as math problems and coding problems with executable checks.
These settings provide a concrete basis for training: the system can try an
answer and receive evidence about whether it satisfies the verifier.

A harness improvement loop can use similar evidence without changing model
weights. It might compare two tool workflows by completion rate, test results,
latency, or cost. The target is already defined; the experiment asks which
workflow reaches it more reliably or efficiently.

Suppose a coding agent repeatedly misses an edge case. A regression test exposes
the problem. The harness can revise its investigation or validation procedure,
then compare the revised version with the current one on fresh executions.
There is an observable criterion for deciding whether the candidate helps.

The signal is strong within the verifier's coverage. Passing a test suite does
not establish that the entire issue is fixed, and a correct final answer does
not establish that the user received a useful explanation. Even a clear score
is evidence about a defined part of the goal.

## When the Target Depends on the User

Now consider writing. Two drafts can both be accurate and grammatically sound.
One is formal and detailed; the other is warm and direct. Which is better?

The answer depends on the user, audience, and purpose. There is no universal
score that tells a personal agent which draft this user will prefer today.
Similar differences appear in how an agent works: whether it explains each
step, asks questions early, takes initiative, or presents a compact result for
review.

Human preference learning already exists in model training. RLHF uses human
feedback to guide model behavior. For example,
[InstructGPT](https://arxiv.org/abs/2203.02155) used human comparisons of outputs
to train a reward model, then used that reward model for reinforcement learning.
That provides a useful starting point for following instructions and producing
responses people prefer under the training setup.

A personal agent has an additional problem: it must learn the preferences of
one particular user through ongoing interaction. A generally preferred response
may still be poorly suited to that person. The evidence is often sparse,
indirect, and mixed with other information in the conversation.

For harness RSI, this creates a second kind of improvement target. The system
must discover what better means for this user while improving how it delivers
that result.

| Dimension | Verifiable outcome signals | Personal preference signals |
| --- | --- | --- |
| Main question | Did the result meet a defined criterion? | Did the result suit this user in this context? |
| Examples | Correct answer, passing tests, winning a game | Tone, detail, structure, initiative, workflow |
| Evaluation | Apply an available verifier | Interpret instructions, corrections, choices, and reactions |
| Main uncertainty | Whether the verifier covers the actual goal | What the feedback means and how broadly it applies |
| Harness change | Improve task execution and validation | Improve user context, instructions, and working procedures |

These signals can appear in the same task. A coding change may pass every check,
yet its review explanation may be too long for the user. A writing task may have
subjective style preferences alongside an explicit, verifiable word limit.
The distinction concerns the evidence available, rather than a strict division
between domains.

Personal preferences are the main example here, but the same idea extends to
learning how to fit a setting or role. The same user may prefer detailed
explanations at a desk, brief spoken responses while driving, and suggestions
adapted to their immediate surroundings while traveling. An agent working
as a company employee might learn team communication conventions and when
colleagues expect it to escalate a decision. An agent acting as a waiter might
learn when guests welcome attention and when they prefer space. Each setting
combines explicit requirements with expectations that emerge through feedback.
Harness RSI can use those signals to improve its fit to the role, just as a
personal agent learns to better serve an individual user.

## Mining Preferences From Interaction

The user rarely supplies a complete preference profile before the agent starts.
The agent has to learn from the interaction itself.

An explicit instruction provides direct evidence: "Use a friendly tone" or
"Start with the decision." A correction provides evidence tied to a particular
result: "This is too formal" or "Remove the background explanation." Edits and
choices can be informative too. If the user repeatedly chooses a concise draft
over a detailed one for status reports, the agent has a reason to investigate a
preference for concise status reports.

Other reactions are harder to interpret. "Great" may express satisfaction with
the main result without endorsing every aspect of the response. Frustration may
come from a wrong answer, excessive delay, or an unwanted workflow. Continued
conversation may indicate interest, correction, or new scope. Silence leaves
the outcome unknown.

Calling these **weak signals** describes uncertainty in the evidence. It does
not mean that every personal preference is weak. An explicit instruction can be
clear and actionable even when the underlying preference is subjective.

| User evidence | Possible interpretation | Limit on the inference |
| --- | --- | --- |
| "Keep future status reports short" | A stated preference for concise status reports | Does not establish a preference for short tutorials |
| "This sounds too formal" | The current draft's tone is unsuitable | The desired replacement tone may still be unclear |
| Repeated selection of shorter drafts | Evidence for concision in comparable writing tasks | Audience or task differences may explain the choices |
| "Thanks, this works" | Positive feedback about the result | Does not identify which features the user valued |
| No reply | No observed feedback | Does not establish acceptance |

The useful output of signal mining is a supported, scoped hypothesis. "Prefers
concise status reports" retains more meaning than "likes short answers." It
should remain connected to the evidence that produced it, so later feedback can
correct it.

## From a Reaction to a Harness Change

The [repository retrospective loop](/blog/llm-application/harness-retrospective-loop)
already treats user replies as evidence about whether a result served their
intent. Personal preference learning extends that idea across interactions.
The following is a proposed design, rather than a report of measured results.

```text
task result + user response
            |
            v
interpret the feedback in its task context
            |
            v
form a preference hypothesis with evidence and scope
            |
            v
propose a bounded harness change
            |
            v
observe later comparable tasks and user feedback
            |
            v
retain, refine, or reverse the change
```

Consider a user who repeatedly removes long introductions from project updates.
The retrospective first checks what those edits mean. Did the agent repeat
information the audience already knew? Did it misunderstand the requested
format? Or does the user generally prefer project updates to lead with the
decision?

Suppose the evidence supports the last interpretation. A candidate harness
change could add a scoped instruction: for this user's project updates, state
the decision first and include background only when it helps the reader act.
This changes an instruction or writing procedure; it does not require training
new model weights.

The proposal should make a prediction: later project updates will need fewer
edits to their openings while preserving necessary context and accuracy.
Historical edits motivate the hypothesis. Fresh outputs and subsequent feedback
provide evidence about whether the changed harness actually helps.

Fewer corrections are useful evidence, but they are not sufficient alone. The
user may stop correcting an agent they no longer trust. When evidence is
ambiguous and the distinction matters, a brief question or a comparison of two
drafts can help clarify the preference. The system should keep uncertainty
visible rather than turn every reaction into a permanent rule.

## Preserve Context and Correctability

Preferences have scope. A user may want concise updates and detailed technical
explanations, friendly personal messages and formal client proposals. A request
for one draft can be a local instruction rather than a durable preference.
Preferences can also change over time.

A useful preference record therefore retains the task context, original
evidence, confidence in the interpretation, and whether the preference was
explicitly stated or inferred. The user must be able to correct or remove it.
New explicit instructions should guide the current task when an older inferred
preference conflicts with them.

The goal is better service to the user's intent. Positive reactions should not
become an incentive to agree with incorrect claims or omit inconvenient facts.
Preference adaptation still needs to preserve correctness and the requirements
of the task. A preferred tone cannot compensate for a false answer.

## Improving the Signal-Mining Process Itself

The recursive part becomes concrete when the harness also improves how it
learns preferences. Its retrospective may notice that it generalizes too far
from single corrections, confuses new requirements with dissatisfaction, or
keeps asking questions the user has already answered.

Those patterns can motivate changes to the feedback interpretation procedure,
the context stored with preferences, or the way relevant preferences are
retrieved. Evaluation should ask whether the revised procedure produces better
supported interpretations and reduces recurring mismatches. Extracting more
preferences is not itself evidence of improvement.

Verifiable outcomes and personal preferences give harness RSI complementary
directions. One provides evidence about performance against defined criteria.
The other helps the system discover and serve a particular user's expectations.
A personal agent needs both: the ability to do the work well, and the ability to
learn what doing it well means for the person it serves.
