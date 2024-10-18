# 微软内部用LLM 做内部文档问答的实践

## Contact me

* Blog -> <https://cugtyt.github.io/blog/llm-application/index>
* Email -> <cugtyt@qq.com>
* GitHub -> [Cugtyt@GitHub](https://github.com/Cugtyt)

---

本文将介绍一些微软内部在使用LLM做内部文档问答的实践。想到哪写哪......

## 为啥要做

我们有一个平台使用的门户软件，用于操作这个平台上面的资源，这里的资源包括像K8S 集群和集群上的服务，机器，网络资源等。用户在使用的时候可能会遇到一些问题，比如资源状态不正常，自己的服务有问题，配置没生效等等。
这时候就需要查阅一些内部的文档和资料去了解发生了什么问题，为什么会发生，怎么处理。如果这时候门户软件能提供
一个内部的文档问答，用户就能更快捷和方便的去解决遇到的问题。

## 可以问哪些文档

内部文档有很多，当用户在门户软件上操作的时候，并不会需要检索所有的文档，因此在面对这个场景的时候，
一个优势是对用户的询问范围有一定的先验知识。知道了门户软件遇到问题可能会涉及到哪些文档，就可以比较方便的
集成这些文档，作为知识库在用户遇到问题的时候提供辅助。

## 怎么提供服务

用户遇到了问题需要帮助，这里有两类方法来提供文档问答内容以解决用户问题：

第一类是用户以聊天的方式去问，这是最直接符合chatgpt的形式。可以通过用户的对话来检索相关的文档，
然后将文档拼接到GPT的提示词中，让GPT根据这些资料回答。这样用户不用再去专门的搜索相关的文档然后
人工阅读理解了，极大的减少了用户在场景切换，手动检索，人工阅读理解的成本，效果也是非常明显的。

第二类是根据用户当前的问题直接触发相关文档回答。上一种方式可以说文档辅助和场景是隔离的，
只不过把文档问答放到了用户的流量入口，更进一步，门户软件是可以某种程度上知道用户面对了什么问题。
比如K8S集群挂了，服务启动不起来，容器状态不正常，这种问题可以相对简单的检测到，一旦检测到这类问题，
可以自动推荐对应的文档来进行回答。当然对于这种确定的问题可以不通过LLM来总结回答，直接就可以点对点对接
相关文档，如果问题很复杂，需要提供更多数据信息，文档内容很多也可以让LLM来做一些分析然后回答问题原因和如何解决。

## 怎么实现文档问答

对于第一类问题，就是做一个对话形式的聊天窗口，这样用户能在遇到问题的第一时间将问题输入对话框，
然后触发文档问答，找到相关文档，总结文档内容，回答用户问题。

文档问答基本分两块，一个是离线任务建立文档的向量数据库，一个是在线任务接收请求，
检索数据库相关内容，LLM总结回答。

### 建立文档检索

这部分可以通过一个离线的流水线来做到，将文本文档转变成向量数据库里面的数据

首先将文档按照长度进行切片，比如切成每篇只有几百个字的短文档，这样的好处是防止某些文档过长导致
检索时相关性不大，占用太多token，也便于向量生成和计算。

第二步就是将切分好的文档片段进行向量化，这部分可以使用一些开源的嵌入模型embedding model来做，比如openai提供了嵌入模型，hugging face上也有很多开源的嵌入模型可以将文档进行向量化，我们使用了hugging face提供的
开源模型本地做向量化。

第三步就是将向量化后的文档存入数据库，数据库需要能根据相似向量进行快速检索，以便在收到查询时能
根据向量相似度找到相关的文档内容转换成原始文档。这里我们使用的是FAISS包来转成本地的向量数据库。

做完这些后，我们就得到了一个文档的向量数据库，最简单的情况下，这个数据库就可以做到服务用户了。
用户可以直接提问向量数据库，向量数据库返回相似度高的向量对应的文档片段，用户可以自己读到有用的信息。

### 接入LLM

LLM 将在两块起主要作用，第一个是将对话转成合适的检索语句，第二个是对数据库返回的相关文档信息进行总结回答。

第一步，根据对话生成合适的检索语句。如果仅仅是单条检索，不考虑对话，这一步也不需要，直接将用户的消息去检索
文档数据库就可以。但是用户可能有多轮对话，因此简单将用户单词输入或者全部对话去检索数据库无法得到用户
真正想问的东西，所以需要让LLM在这里理解用户意图，将对话上下文变成一条合适的检索语句。

在处理这一步的时候，还需要考虑对话使用的token，在对话过长token超出限制的情况需要及时的缩减token，
比如只保留最近的对话内容，或者让LLM总结精炼之前的对话内容进而减少整体的token使用。

第二步，检索文档向量数据库，将第一步得到的检索语句去检索之前生成的文档数据库，得到相关的文档。

第三步，构建提示词，将文档信息，LLM的设定，比如要让它做的事情，回答的方式和逻辑进行指定，
这部分具有比较大的灵活性。

第四步，把LLM根据提示词的回答已经相关的数据信息返回到前端，完成一轮对话。

在完成这些步骤后，基本就做完了一个文档问答系统，但是对于辅助用户这个目标还是有很多可以做的功能。

## 根据问题触发文档问答

对于点对点的文档解决比较简单，直接设定好对应的文档和问题的关联就能做到，这里不讨论。
对于一个问题可能有很多文档来讨论和解决的，还是可以让LLM做到总结和推荐。

### 问题检测

对于门户软件，可以根据用户当前操作的资源和页面设定一些检测手段，比如资源状态检测，规则设定等自动触发。
自动触发的目的是收集必要的信息和数据，然后替代用户手动输入和描述问题，直接进行文档问答。

### 自动问题辅助

在问题被检测到后，可以把数据和一些信息发给LLM，让LLM进行总结，直接生成对应的检索语句，
对接到上面文档问答的后续步骤，将回答显示到对话框中，提示用户遇到的问题和文档提示的解决方案。

还有很多其他的功能，今天先暂时写到这里......

> 如果有用欢迎打赏

![](../buymeacoffee.jpg)