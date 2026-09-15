# Archive and Link: The Core of Agent Context Management

> **Agent context management has two core responsibilities: archive past
> context into durable, manipulable artifacts, and link the current context
> to the relevant parts of that archive.** Session compaction and memory
> generation are different applications of these same responsibilities.

An agent works through a limited active context. As a task continues, it
accumulates requirements, decisions, tool results, failed attempts, and changes
of direction. Some of that information must remain immediately available. Much
of it can leave the active window, provided the agent can find it again when
it matters.

The key is to treat a link broadly: **a link can be instructions for finding
information, as well as an address where it lives.** A note that says “search
the previous debugging sessions for the failed retry experiment” connects the
present task to past evidence through a retrieval operation. Search, recall,
and read tools are part of linking in this model.

## From Eyes and Hands to Context Management

In [Observability and Manipulability: The Eyes and Hands of Self-Improving Harnesses](https://cugtyt.github.io/blog/llm-application/observability-manipulability-for-self-improving-harness),
I described two interfaces a harness needs. Observability lets an improvement
mechanism inspect what happened and identify a target. Manipulability gives it
a defined surface on which to act.

Context management gives those ideas a concrete form. Archiving moves context
into explicit artifacts: session files, message lists, state notes, and memory
records. With appropriate operations, the harness can organize, annotate,
summarize, split, and update these artifacts. This is the manipulation surface.

Linking makes that external context observable from the current window.
References, retrieval hints, and tools let the agent discover and inspect
information it is no longer carrying directly.

Archiving supplies the artifacts; manipulation tools make them editable.
Linking supplies paths to those artifacts; retrieval tools make them reachable.

## Archive: Give Past Context a Durable Form

An archive can contain several representations of the same experience. A
session file preserves the conversation as an ordered list of messages. Tool
outputs preserve observations. A state note records the objective, constraints,
decisions, and unfinished work. A memory record captures an insight that may
apply beyond the original session.

Each representation serves a different purpose. Original messages retain
detail. State notes make continuation cheaper. Derived memories make useful
conclusions easier to reuse. Keeping a connection to the original evidence
allows the agent to inspect how a conclusion was reached.

Session isolation fits here too. Storing sessions separately gives each one a
boundary and an identity. Earlier work can remain available without occupying
the current context. Message identifiers and ordering then let the harness
address a particular exchange inside that session.

The storage medium is secondary to these capabilities. Files, databases, and
other stores can all represent an archive. What matters is whether meaningful
units of context can be preserved, addressed, and operated on. Manipulating a
derived note need not rewrite the historical evidence behind it.

## Link: Make Past Context Reachable from the Present

A file path or message ID provides a direct reference. A descriptive hint
explains why the reference matters: “Read this experiment before changing the
retry policy.” Search can discover a relevant session whose identity is
unknown. Recall can select a useful memory. Read tools bring the selected
content into the active window.

These are different ways of connecting the present task to archived context.
Some connections are recorded in advance; others are discovered when a new
question makes old information relevant.

A useful link gives the agent a reason to retrieve information and a way to
locate it. The location may be an exact address or a search instruction.
“Previous session” offers little guidance. “Search the timeout investigation
for the failed retry experiment and its request trace before adjusting retries”
provides both a retrieval clue and a condition for using it.

Tool availability is part of this interface. A hint cannot help much if the
agent has no way to search for the target or read it. Conversely, a searchable
archive still needs enough clues for the agent to formulate a useful query.

## One Debugging Task Across Context Windows

Consider an agent investigating intermittent request timeouts. It tests a
longer retry interval, discovers that this does not fix the problem, and then
finds evidence pointing toward connection reuse. Its active context is nearly
full before it can test the next hypothesis.

The harness archives the session, including the messages and experiment
results. The agent records a continuation note: the objective remains fixing
the timeout; the retry experiment failed; connection reuse is the next
hypothesis; the relevant trace is in a particular archived tool result.

```text
Active debugging session
        |
        | archive messages, results, and current state
        v
Session archive <------- Continuation note
        ^                 objective + next step
        |                 evidence references + hints
        |                         |
        | search / recall / read  | carry forward
        |                         v
        +--------------- New active context
```

In the new window, the agent can resume from the note. If it needs to know
exactly how the retry experiment was configured, it follows the reference and
reads the original result. The continuation note does not have to anticipate
every detail the next step might require.

In this design, compaction serves **continuation of the current task**. It
selects what the next context window needs to resume: the active objective,
constraints, unfinished work, and paths back to evidence. Details can move out
of the window while remaining recoverable.

After the investigation, the agent might also save a memory: for this client
and version, this timeout pattern was associated with connection reuse. The
memory links to the confirming experiment and records its scope. A later task
can retrieve that conclusion and check whether its conditions still apply.

Memory generation serves **reuse across future tasks**. It selects what may
remain useful after the immediate work is complete, recording the conclusion,
its scope, and supporting evidence. The next debugging action belongs in the
continuation note; the confirmed behavior of this client version belongs in
the reusable memory.

Both operations archive and link. Their different purposes determine what
they preserve, how they organize it, and when the agent should retrieve it.

## What Makes Archive and Link Work Well

These two responsibilities describe an architecture. Its quality depends on
the choices made within it.

Preservation determines what can be recovered. If a failed experiment's output
was discarded, a link cannot reconstruct it. Retrieval hints determine whether
the agent knows where to look. Selection determines whether the retrieved
material deserves space in the current window.

Time and scope also matter. An early hypothesis may have been disproved. A
user may have replaced a requirement. A memory may describe an older version
of a component. Links that express “supported by,” “applies to,” and “superseded
by” help the agent interpret a record instead of treating every retrieved
statement as current truth.

Summaries remain valuable in this design. They reduce the cost of navigating
history and collect conclusions that would be expensive to reconstruct.
Keeping them as derived views over preserved evidence makes it possible to
inspect, correct, or regenerate them when necessary.

The practical design questions become concrete: what should leave the active
window, how should it be represented, and what must remain so the agent can
find it again? A useful way to evaluate the design is to resume a task in a
fresh context and ask whether the agent can recover a required detail that
was omitted from its continuation note. That exercises the connection between
what the system preserved and what the current agent can actually use.
