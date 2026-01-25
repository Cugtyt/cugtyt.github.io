# **Blogs of *LLM Application***

## Contact me

* Blog -> <https://cugtyt.github.io/blog/index>
* Email -> <cugtyt@qq.com>
* GitHub -> [Cugtyt@GitHub](https://github.com/Cugtyt)

---

本系列博客主要是关于大语言模型的应用。

---

## [**Agent Inference: The Shift from Model to Agent Optimization**](https://cugtyt.github.io/blog/llm-application/agent-inference)

> When we talk about AI inference today, we mostly mean model inference—the infrastructure for making LLMs fast and efficient. But as agents become the basic unit of AI applications, the focus will shift to a higher abstraction layer: Agent Inference.

* **Agent Role & Prompt Management**: Identity from system prompts, runtime injection, version control
* **Tool Infrastructure & Distribution**: Package-like distribution (like npm), registry, routing, execution
* **Memory Orchestration**: Conversation state, persistent storage, context window management
* **Lifecycle Orchestration**: Standardized agent loop as first-class infrastructure
* **Sub-Agent Delegation**: Dynamic launching, context isolation, unified infrastructure
* **Skill Discovery & Distribution**: SOPs as packaged domain expertise, runtime loading, marketplace

---

## [**From Prompts to SOPs: The Rise of Intelligence Engineering**](https://cugtyt.github.io/blog/llm-application/agent-intelligence-sop)

> As base models become commoditized, the differentiation shifts to the agent layer. Intelligence Engineering is the discipline of designing SOPs (Standard Operating Procedures) that transform raw model intelligence into production-ready, scenario-specific solutions.

* **Two Layers of Intelligence**: Model Layer (thinking) vs Agent Layer (doing)
* **SOPs as the Core**: Tools + Instructions + Workflow + Success Criteria
* **Standardized Runtime**: Portable SOPs across implementations via uniform agent lifecycle
* **The Discipline**: Design, version control, test, and iterate SOPs as first-class engineering artifacts

---

## [**Gnote: Extending Git Context and Memory Management with Vector Search**](https://cugtyt.github.io/blog/llm-application/gnote)

> This post extends the Git-based context management approach by integrating vector search capabilities for semantic retrieval. Gnote provides dual search methods—keyword and vector-based—enabling both exact matching and semantic similarity searches across versioned context history.

* **search_context_by_keywords(keywords)**: Returns Git commit references matching keyword criteria (exact or fuzzy text matching)
* **search_context_by_vector(query_text)**: Converts query text to embeddings and returns Git commit references with semantic similarity
* **Context Merging**: Online and offline strategies to condense search results and history
* **Context Forgetting**: Time-based or relevance-based policies to prune old commits
* **Alternative Implementation**: Custom in-memory data structure for performance-critical applications

---

## [**Context Management for LLM Agent Systems**](https://cugtyt.github.io/blog/llm-application/context-management)

> Effective context management is critical for maintaining performance, coherence, and scalability in complex LLM applications. This post presents an integrated approach combining three complementary strategies that work together to handle context at multiple levels—from real-time optimization to persistent memory.

All three strategies are invoked by the LLM calling appropriate tools, with conversation management additionally triggered by system signals:

* **Conversation Management**: Real-time optimization of active conversation to fit within LLM context window—LLM-triggered or system-forced when token limits exceeded
* **Sub-Agent Offloading**: Delegates simple independent tasks to isolated, temporary agent instances—LLM decides when to offload
* **Git Context Memory**: Persistent memory storage with version control for cross-session context—LLM calls tools to checkpoint and recall

---

## [**Agentic Conversation Management**](https://cugtyt.github.io/blog/llm-application/conversation-manage)

> We can use an Agent-based approach to manage conversations more intelligently, by giving the LLM tools to edit, summarize, or delete parts of the conversation as needed.

* **edit_message(message_id, new_content)**: Edit a specific message in the conversation.
* **delete_message(message_id)**: Remove a specific message from the conversation.
* **summarize_messages(start_id, end_id)**: Summarize a range of messages into a concise form and replace them with the summary.

---

## [**Universally Manage Session Context and Memory via Git**](https://cugtyt.github.io/blog/llm-application/git-context-memory)

> At a high level, context is the input of an LLM, and memory is the historical context.
> Using Git for context and memory management provides powerful version control and branching.

* **read_context()**: read the current context from the context file
* **update_context(new_context, commit_message)**: update the context file with new context and commit the changes with a commit message
* **get_context_history()**: get the context history via Git log
* **get_snapshot(version)**: get the context snapshot of a specific version via Git checkout

---

## [**Context Offload via Sub-Agent in LLM Applications**](https://cugtyt.github.io/blog/llm-application/context-offload-via-subagent)

> In complex LLM applications, efficiently managing context and computational resources is crucial. While current practices often rely on offloading to external databases like file systems, this post explores a more elegant solution: **context offloading via sub-agent workflows**.

```
# Within the main agent's lifecycle
if needs_specialized_handling:
    # Dynamically create comprehensive instructions
    subagent_instructions = craft_instructions_with_task_context(current_task)
    
    # Launch sub-agent with instructions and tools
    subagent_result = launch_subagent(
        instructions=subagent_instructions,
        tools=selected_tools
    )
    
    # Continue with condensed result
    conversation.append(subagent_result)
```

---

## [**AgentBase: Designing a Full-Agent Lifecycle with Factory, Runtime, and Observer**](https://cugtyt.github.io/blog/llm-application/agent-base)

> 1. **AgentFactory** – constructs a runnable agent workflow from specs.
> 2. **AgentRuntime** – executes the workflow on a concrete task input.
> 3. **AgentObserver** – scores the outcome and feeds improvements back into the factory.

---

## [**LLM Generates Tokens, Agent Generates Messages, AgentLauncher Generates Agents**](https://cugtyt.github.io/blog/llm-application/agent-gen)

> LLM generates tokens, Agent generates messages, AgentLauncher generates agents.

```
function agent_life_cycle(system_message, user_message, llm_call, tool_call):
    conversation = [system_message, user_message]
    tool_set = [tool1, tool2, ...]

    while True:
        llm_output_messages = llm_call(conversation, tool_set)
        conversation.extend(llm_output_messages)
        if tool_call_message in llm_output_messages:
            tool_result_message = tool_call(tool_call_message, tool_set)
            conversation.append(tool_result_message)
        else:
            break
    return conversation
```

---

## [**AgentLauncher**](https://cugtyt.github.io/blog/llm-application/agentlauncher)

> AgentLauncher GitHub: https://github.com/Cugtyt/agentlauncher
>
> AgentLauncher is an event-driven, multi-agent framework for solving complex tasks by dynamically generating sub-agents.
> The main agent coordinates strategy, while sub-agents handle specialized tasks.
> Agent lifecycles are managed automatically, similar to jobs in Kubernetes—sub-agents are lightweight and ephemeral.

---

## [**The Three-Stage Evolution of LLM Agents: From Learning to Creating**](https://cugtyt.github.io/blog/llm-application/agent-three-stage)

> * **照猫画虎** (learning from data) - Foundation models trained on curated datasets
> * **适应环境** (adapting to environment) - Agents with memory, tools, and planning capabilities  
> * **改造环境** (transforming environment) - Creative agents that build tools and manufacture subagents

---

## [**Process Supervision Is All You Need for AI Coding**](https://cugtyt.github.io/blog/llm-application/ai-coding-process)

> Agent-based coding is increasingly popular in AI development,
> but it often veers off course.
> To achieve better results and minimize risks,
> active supervision of the process is essential.

---

## [**Massive Search: LLM Structured Outputs is All You Need**](https://cugtyt.github.io/blog/llm-application/massive-search)

> Executing complex searches across entities with diverse attributes
> —such as text, numbers, booleans, and images—can be challenging.
> These searches often require intricate queries,
> potentially involving joins across multiple data sources.
> For example, searching for a book might involve filtering by its title,
> description, price, user comments, and cover image simultaneously.
> 
> Massive Search provides a method for querying such complex
> but logically grouped data by leveraging LLM Structured Outputs.
> "Logically grouped" means all the data pertains to the same core entity,
> like a specific book product.

---

## [**Smart Diagnosis Solution**](https://cugtyt.github.io/blog/llm-application/smart-diagnosis)

> Smart Diagnosis Solution, stack and layers

---


## [**Manufacturer-Executor-Evaluator: A General LLM Agentic Pattern for Collective Intelligence**](https://cugtyt.github.io/blog/llm-application/mee)

> * Manufacturer is responsible for generating the task specification based on the task examples, 
> which is the system start point and objective,
> * the Executor is responsible for executing the task based on the task specification, it is the final solution output,
> * and the Evaluator is responsible for evaluating the execution result to make sure the task specification
> meets the objective, feedback or comments from Evaluator will be used to improve the task specification in the next iteration.

---

## [**Prompt Factory**](https://cugtyt.github.io/blog/llm-application/prompt-factory)

> Prompt Factory help user to write prompt from provided samples

> Writer generates prompt
>
> Actor practices prompt
>
> Critic evaluates prompt

---

## [**软件实现Copilot的架构图**](https://cugtyt.github.io/blog/llm-application/copilot-arch)

> 软件实现Copilot的架构图

---

## [**一个应用的Copilot要怎么做**](https://cugtyt.github.io/blog/llm-application/copilot-basic)

> 简单介绍如何给一个应用做Copilot

---

## [**LLM 做文档问答应用**](https://cugtyt.github.io/blog/llm-application/llm-doc-answer-application)

> LLM具有很强的文字总结能力，结合文档检索可以做文档的智能问答，本文将介绍在微软内部的一些实践。

---

## [**LLM Patterns - 中文**](https://cugtyt.github.io/blog/llm-application/llm-unit-cn)

> Extractor 单元
>
> Composer 单元
>
> Converter 单元
>
> Router 单元

---

## [**LLM Patterns**](https://cugtyt.github.io/blog/llm-application/llm-unit)

> Extractor unit
>
> Composer unit
>
> Converter unit
>
> Router unit


---
