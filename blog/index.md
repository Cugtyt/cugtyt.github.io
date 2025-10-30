# **Blogs**

## Contact me

* Blog -> <https://cugtyt.github.io/blog/index>
* Email -> <cugtyt@qq.com>
* GitHub -> [Cugtyt@GitHub](https://github.com/Cugtyt)

---

# 最近文章：


## [**AgentBase: Designing a Full-Agent Lifecycle with Factory, Runtime, and Observer**](https://cugtyt.github.io/blog/llm-application/agent-base)

> 1. **AgentFactory** – constructs a runnable agent workflow from specs.
> 2. **AgentRuntime** – executes the workflow on a concrete task input.
> 3. **AgentObserver** – scores the outcome and feeds improvements back into the factory.

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


## [**The Three-Stage Evolution of LLM Agents: From Learning to Creating**](https://cugtyt.github.io/blog/llm-application/agentlauncher)

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

# 系列博客：

## [**LLM Application*系列***](https://cugtyt.github.io/blog/llm-application/index)

> 关于LLM的应用实践思考

---

## [**论文笔记*系列***](https://cugtyt.github.io/blog/papers/index)

> 阅读的一些论文

---

## [**算法题目*系列***](https://cugtyt.github.io/blog/algo/index)

> 做过的一些算法题目和练习

---

## [**Effective Python *系列***](https://cugtyt.github.io/blog/effective-python/index)

> 高效使用python

---

## [**Effective Pytorch *系列***](https://cugtyt.github.io/blog/effective-pytorch/index)

> 高效使用Pytorch等相关工具

---

## [**intv *系列***](https://cugtyt.github.io/blog/intv/index)

> 算法笔记

---

## [**Blogs of 2020**](https://cugtyt.github.io/blog/2020/index)

---

## [**Blogs of 2019**](https://cugtyt.github.io/blog/2019/index)

---

## [**Blogs of 2018**](https://cugtyt.github.io/blog/2018/index)

---

## [**Blogs of 2017**](https://cugtyt.github.io/blog/2017/index)

---

## [**机器学习实战部分代码精简优化*系列***](https://cugtyt.github.io/blog/ml-in-action/index)

> 在学习《*Machine Leaning In Action*》发现代码实现很不好  
> 很多代码实现繁琐，效率低  
> 使用语言特性可以优化，如列表推导，zip等  
> 利用第三方包可以简化代码，提升效率，如numpy广播，矩阵处理等  
> 数学上的简化更加有效

---

## [**机器学习和数据科学相关*系列***](https://cugtyt.github.io/blog/ml-data/index)

> 一些关于机器学习、数据科学的算法和应用相关内容

---

## [**Udacity Deep RL *系列***](https://cugtyt.github.io/blog/udacity-deep-rl/index)

> Udacity Deep RL代码理解，笔记

---

## [**Crafting Your Research Future 笔记 *系列***](https://cugtyt.github.io/blog/CYRF/index)

> 阅读《Crafting Your Research Future *A guide to Successful Master’s and Ph.D. Degrees in Science & engineering*》笔记

---

## [**Kaggle*系列***](https://cugtyt.github.io/blog/kaggle/index)

> 记录Kaggle上的尝试

---

## [**强化学习相关*系列***](https://cugtyt.github.io/blog/rl-notes/index)

> 强化学习相关笔记
