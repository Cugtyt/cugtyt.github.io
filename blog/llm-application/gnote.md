# Gnote: Extending Git Context and Memory Management with Vector Search

## Contact Me

- Blog: <https://cugtyt.github.io/blog/llm-application/index>
- Email: <cugtyt@qq.com>
- GitHub: [Cugtyt@GitHub](https://github.com/Cugtyt)

---

In the [previous post](./git-context-memory.md), we explored using Git to manage session context and memory for LLM applications. This post extends that approach by adding vector search capabilities for semantic retrieval.

## Background: Git-Based Context Management

As discussed previously, Git provides powerful version control and branching capabilities, allowing us to manage both current context and historical memory effectively. By storing context in a Git repository, we can track changes over time and retrieve specific versions as needed.

All context changes should be triggered by the LLM, meaning the LLM will actively call these tools to manage the context file. Here are the core tools:

* read_context(): read the current context from the context file
* update_context(new_context, commit_message): update the context file with new context and commit the changes with a commit message
* get_context_history(): get the context history via Git log
* get_snapshot(version): get the context snapshot of a specific version via Git checkout

Under the hood, these tools interact with the Git repository to perform their respective functions. The Git repository serves as the backbone for context and memory management, the context files are stored and versioned within the repository.

This Git-managed context file essentially functions as a versioned note-taking system—let's call it "gnote". Having covered basic read and write operations in the previous post, we now enhance gnote with search capabilities to quickly find relevant context entries.

## Search Capabilities

Gnote supports two complementary search methods:

**Keyword Search**: Git maintains a chronological history of all context changes. By indexing commit messages and content with keywords, we can quickly locate relevant versions through exact or partial text matches.

**Vector Search**: For semantic retrieval, we convert context into vector embeddings. This enables similarity searches that find contextually related content even without exact keyword matches, capturing meaning rather than just matching words.

Both search indices reference specific Git commit hashes, enabling precise context retrieval at any point in history. This design also supports forgetting: as old commits are deleted over time, their corresponding index entries are removed accordingly.

## How Search Works

When the LLM needs to recall context, it can use either keyword search or vector search to find relevant context entries. The search results provide references to specific Git commits, which can then be used to retrieve the full context snapshot.

### Architecture

**Git Timeline:**
```
... → commit_A → commit_B → commit_C → ...
      ↓           ↓           ↓
   (msg, diff) (msg, diff) (msg, diff)
```

**Search Index:**
- Each commit message is indexed (keyword/vector) → linked to its commit hash
- Each context diff is indexed (keyword/vector) → linked to its commit hash

**Search Flow:**
1. User submits a query (keywords or natural language text)
2. Search returns relevant commit hashes ranked by relevance
3. Use `get_snapshot(commit_hash)` to retrieve the full context at that point in time

### Available Tools

* `search_context_by_keywords(keywords)` - Returns Git commit references matching keyword criteria (exact or fuzzy text matching)
* `search_context_by_vector(query_text)` - Converts query text to embeddings and returns Git commit references with semantic similarity

## Advanced Features

### Context Merging

We can do context merging in two levels:

* **Online Search Result Merging**: When multiple search results are returned, use an LLM to merge relevant snippets into a cohesive summary, eliminating redundancy.
* **Offline Context Merging**: When updating context, an LLM can intelligently merge commits to condense history and remove redundant information, keeping the context file concise and history manageable. Then it will also update the search index accordingly.

### Context Forgetting

As the commits are managed by Git, we can set the forgetting policy. For example, we can periodically delete old commits beyond a certain age or based on relevance criteria. Correspondingly, we will also update the search index to remove references to deleted commits.

## Alternative Implementation: Custom Data Structure

While Git provides robust version control, it introduces overhead for high-frequency context updates—particularly the cost of file I/O, process spawning, and git operations. For performance-critical applications requiring rapid context updates, we can implement a custom in-memory data structure that maintains the same conceptual model with lighter-weight storage.

This alternative design uses a sequential store where each entry represents a context update with metadata for search indexing. The implementation provides more efficient retrieval and management while preserving the core benefits of version tracking and dual search capabilities.

### GnoteNode Structure

```python
class GnoteNode:
    """Represents a single entry in the gnote system"""
    
    def __init__(self, context_content, commit_message):
        self.id = str(uuid.uuid4())
        self.context_content = context_content
        self.commit_message = commit_message
        self.created_at = datetime.now()
```

**Key features:**
- Simple data structure with minimal overhead
- UUID-based identification
- Timestamp for time-based operations
- No linked list pointers (OrderedDict handles ordering)

### Gnote System

```python
class Gnote:
    """Main gnote system managing nodes and search indices"""
    
    def __init__(self, keyword_index, vector_index, embedding_model):
        self.keyword_index = keyword_index
        self.vector_index = vector_index
        self.embedding_model = embedding_model
        self.nodes = OrderedDict()  # Maintains insertion order
    
    def add_node(self, context_content, commit_message):
        """Create and index a new node"""
        node = GnoteNode(context_content, commit_message)
        self.nodes[node.id] = node
        
        self.keyword_index.add(node.id, context_content, commit_message)
        embedding = self.embedding_model.encode(context_content + " " + commit_message)
        self.vector_index.add(node.id, embedding, {"created_at": node.created_at})
        
        return node
    
    def search_by_keywords(self, keywords):
        """Search for nodes by keywords"""
        result_ids = self.keyword_index.search(keywords)
        return [self.nodes[id] for id in result_ids if id in self.nodes]
    
    def search_by_vector(self, query):
        """Search for nodes by semantic similarity"""
        query_embedding = self.embedding_model.encode(query)
        result_ids = self.vector_index.search(query_embedding)
        return [self.nodes[id] for id in result_ids if id in self.nodes]
    
    def forget_before(self, cutoff_time):
        """Remove nodes created before cutoff time"""
        forgotten = []
        for node_id in list(self.nodes.keys()):
            node = self.nodes[node_id]
            if node.created_at < cutoff_time:
                self.keyword_index.remove(node_id)
                self.vector_index.remove(node_id)
                del self.nodes[node_id]
                forgotten.append(node_id)
        return forgotten
    
    def merge_range(self, start_id, end_id, merge_fn):
        """Merge nodes from start_id to end_id using merge_fn"""
        ids_to_merge = []
        in_range = False
        for node_id in self.nodes.keys():
            if node_id == start_id:
                in_range = True
            if in_range:
                ids_to_merge.append(node_id)
            if node_id == end_id:
                break
        
        if len(ids_to_merge) < 2:
            return None
        
        contents = [self.nodes[id].context_content for id in ids_to_merge]
        messages = [self.nodes[id].commit_message for id in ids_to_merge]
        
        merged_content = merge_fn(contents)
        merged_message = " | ".join(messages)
        
        self.nodes[start_id].context_content = merged_content
        self.nodes[start_id].commit_message = merged_message
        
        self.keyword_index.update(start_id, merged_content, merged_message)
        embedding = self.embedding_model.encode(merged_content + " " + merged_message)
        self.vector_index.update(start_id, embedding, {"created_at": self.nodes[start_id].created_at})
        
        for node_id in ids_to_merge[1:]:
            self.keyword_index.remove(node_id)
            self.vector_index.remove(node_id)
            del self.nodes[node_id]
        
        return self.nodes[start_id]
    
    def get_current(self):
        """Get current (latest) node"""
        if self.nodes:
            return next(reversed(self.nodes.values()))
        return None
    
    def get_history(self):
        """Get all nodes in order"""
        return list(self.nodes.values())
```

**Design principles:**
- **OrderedDict**: Natural insertion ordering without manual linked list management
- **Separation of concerns**: Nodes store data, indices handle search, Gnote orchestrates
- **Automatic indexing**: Every node is automatically indexed in both keyword and vector search
- **Time-based forgetting**: Simple, predictable cleanup based on creation time
- **Flexible merging**: Pluggable merge function for custom content consolidation
- **Clean API**: Simple methods for common operations (add, search, forget, merge, get history)

This structure provides efficient context management while maintaining the core benefits of version tracking and dual search capabilities discussed earlier in this post.

## Implementation Trade-offs

**Git-based approach:**
- ✅ Robust persistence and version control
- ✅ Works across processes and restarts
- ✅ Standard tooling (git commands, GitHub)
- ❌ Higher overhead for frequent updates

**Custom data structure approach:**
- ✅ Lower latency for frequent operations
- ✅ Fine-grained control over memory usage
- ✅ Easier to extend with custom features
- ❌ Requires manual persistence implementation
- ❌ Less mature tooling ecosystem

Choose based on your application's needs: Git for durability and standard workflows, custom structures for performance-critical in-memory operations.