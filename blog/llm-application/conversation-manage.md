# Agentic Conversation Management

## Contact Me

- Blog: <https://cugtyt.github.io/blog/llm-application/index>
- Email: <cugtyt@qq.com>
- GitHub: [Cugtyt@GitHub](https://github.com/Cugtyt)

---

In LLM applications, managing conversations effectively is crucial for maintaining context and ensuring coherent interactions. When the conversation is too long, it can overwhelm the LLM's context window, leading to degraded performance. Practices like summarization and simply deleting old messages are commonly used, but they are not flexible enough for dynamic scenarios.

We can use an Agent-based approach to manage conversations more intelligently, by giving the LLM tools to edit, summarize, or delete parts of the conversation as needed.

## Inputs of Conversation Management Agent

1. **Current Conversation**: The full conversation history up to the current point.
2. **Management Goals**: Specific objectives for managing the conversation, such as reducing length, maintaining key information, or focusing on certain topics.
3. **Available Tools**: A set of tools the agent can use to manipulate the conversation.

## Conversation Management Tools

* **edit_message(message_id, new_content)**: Edit a specific message in the conversation.
* **delete_message(message_id)**: Remove a specific message from the conversation.
* **summarize_messages(start_id, end_id)**: Summarize a range of messages into a concise form and replace them with the summary.

## Agent Workflow

We can reuse the agent lifecycle pattern discussed in [Standardize the Agent Lifecycle](./agent-gen.md):

```python
def conversation_management_agent(conversation, management_goal, llm_call):
    management_tools = [edit_message, delete_message, summarize_messages]
    while not is_goal_achieved(conversation, management_goal):
        llm_output = llm_call(conversation, management_goal, management_tools)
        for tool_call in llm_output.tool_calls:
            tool_result = execute_tool(tool_call, management_tools)
            conversation = update_conversation(conversation, tool_result)
    return conversation
```

## Integration with Main Agent

The conversation management agent can be integrated into the main agent lifecycle. When the main agent detects that the conversation is becoming too long or unwieldy, it can invoke the conversation management agent to optimize the conversation before proceeding.

```python
def main_agent_lifecycle(system_message, user_message, llm_call, tool_call):
    conversation = [system_message, user_message]
    tool_set = [other_tools...]

    while True:
        if conversation_too_long(conversation):
            conversation = conversation_management_agent(
                conversation,
                management_goal="reduce_20_percent_length",
                llm_call=llm_call
            )

        llm_output_messages = llm_call(conversation, tool_set)
        conversation.extend(llm_output_messages)
        
        if tool_call_message in llm_output_messages:
            tool_result_message = tool_call(tool_call_message, tool_set)
            conversation.append(tool_result_message)
        else:
            break
    return conversation
```

## Benefits of Conversation Management

1. **Dynamic Adaptation**: The agent can adaptively manage the conversation based on current needs and goals.
2. **Preservation of Key Information**: By using summarization and selective editing, important context can be preserved while reducing overall length.
3. **Improved Coherence**: A well-managed conversation helps maintain coherence and relevance in interactions with the LLM.

This agentic approach is like a kind of GC process for main agent, helping to keep the conversation clean and efficient.