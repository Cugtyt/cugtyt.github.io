# Universally Manage Session Context and Memory via Git

## Contact Me

- Blog: <https://cugtyt.github.io/blog/llm-application/index>
- Email: <cugtyt@qq.com>
- GitHub: [Cugtyt@GitHub](https://github.com/Cugtyt)

---

[Manus blog](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) discusses using the file system as context to reduce the performance degradation for long observations.

This post extends this by using Git as context storage and management. The Git system provides powerful version control and branching, so the context history can be well managed. Yes, context history leads to memory.
We can universally manage context and memory via Git.

## Context and Memory

> At a high level, context is the input of an LLM, and memory is the historical context.

When we are talking about context engineering, we are actually talking about how to effectively manage input context and memory for LLM applications.
Manus uses the file system as context because the file system is not limited by size. We can store large context in the file system and load relevant context as input when needed.
However, the file system alone does not provide version control and history management.
So it is purely context management, not memory management.

Someone may think using a vector database to store context is also a good idea, as a vector database can do similarity search to find relevant context. But the pain point is that a vector database does not provide version control. You cannot know what is actually stored at a high level; you just try to search similar vectors, and you cannot figure out the changes of context over time.

Git provides powerful version control and branching. You can directly get the active context snapshot via the current Git branch, and you can also get historical context via Git commit history. This enables both context management and memory management.

## How to Use Git as Context and Memory

Here we are talking about session context and memory for LLM applications, not persona or long-term memory.
It is more context specific, not history specific. Using the file system or a vector database for long-term memory is still a good idea.

### Initialize context file and Git

Let's keep it simple and just use a text file to store context. Git will manage the version of this file.
Here we leave the context content format open, as it depends on your specific application.

### Tools to manage the context

All context changes should be triggered by the LLM, meaning the LLM will actively call these tools to manage the context file. Here are the core tools:

* **read_context()**: read the current context from the context file
* **update_context(new_context, commit_message)**: update the context file with new context and commit the changes with a commit message
* **get_context_history()**: get the context history via Git log
* **get_snapshot(version)**: get the context snapshot of a specific version via Git checkout

### When to use these tools

Updating context happens when the current context is too long to maintain or when there is new important information that needs to be stored. This looks like a status update process. The LLM needs to figure out what information to keep and what to discard, then call the update_context() tool to update the context file.

Getting memory happens when the LLM needs to recall some historical context. It can call the get_context_history() tool to get the history, then decide which version to check out via the get_snapshot(version) tool. This looks like a search process. The LLM needs to figure out what historical information is relevant, then extract the useful information from the history commits and add it to the current context.

### Example Workflow

Let's reuse the agent lifecycle from [Standardize the Agent Lifecycle](./agent-gen.md):

``` python
def agent_life_cycle(system_message, user_message, llm_call, tool_call):
    conversation = [system_message, user_message]
    tool_set = [tool1, tool2, ...]

    while True:
        if need_context_update: # decided by LLM
            conversation.extend([
                tool_call(read_context),
                tool_call(update_context(new_context, commit_message))
            ])
        if need_memory_recall: # decided by LLM
            conversation.extend([
                get_context_history(),
                get_snapshot(version)
            ])
        
        llm_output_messages = llm_call(conversation, tool_set)
        conversation.extend(llm_output_messages)
        if tool_call_message in llm_output_messages:
            tool_result_message = tool_call(tool_call_message, tool_set)
            conversation.append(tool_result_message)
        else:
            break
    return conversation
```

## More Thoughts

Using Git as context and memory management provides a universal solution, as Git is widely used and well understood.

It also provides powerful features like branching, merging, and collaboration, which can be leveraged for more complex LLM applications.
This enables agents to checkpoint their current state and explore different context paths via branching.
Moreover, Git's distributed nature allows for easy sharing and synchronization of context and memory across multiple agents or systems, facilitating collaborative workflows in LLM applications.

For example:
* The main agent is working on a complex task and needs to explore multiple approaches. It can create separate branches for each approach, allowing it to experiment without affecting the main context.
* Sub-agents can be spawned to handle specific subtasks, each operating on its own branch. Once a sub-agent completes its task, its changes can be merged back into the main agent's context, ensuring that valuable insights are retained.