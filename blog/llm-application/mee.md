# Manufacturer-Executor-Evaluator: A General Agentic Pattern for Collective Intelligence

## Contact me

* Blog -> <https://cugtyt.github.io/blog/llm-application/index>
* Email -> <cugtyt@qq.com>
* GitHub -> [Cugtyt@GitHub](https://github.com/Cugtyt)

---

The idea of Collective Intelligence is widely used in the AI area, 
like reward and action in Reinforcement Learning,
the voting mechanism in the ensemble learning,
generator and discriminator in Generative Adversarial Networks (GAN),
mixture of experts in the recent llm models, etc.
Multi-agent systems draw much attention with the development of latest LLM trends.
In this article, I will introduce a general agentic pattern for Collective Intelligence, 
which has three parts: Manufacturer, Executor, and Evaluator (MEE), it can be extended to many multi-agent systems as a general framework.

## Introduction

Generative Adversarial Networks (GAN) and Reinforcement Learning (RL) are two popular paradigms in the AI area, they have some common characteristics:

For GAN:
1. Generator and Discriminator are two agents.
2. Generator generates fake data, and Discriminator distinguishes real data from fake data.
3. The two agents interact with each other, and the system can learn and perform better.

For RL:
1. Agent and Environment are two agents.
2. Agent takes actions, and Environment gives rewards.
3. The two agents interact with each other, and the system can learn and perform better.

These are for the learning process, it requires expert knowledge to design the objective function, reward function, etc.
For multi-agent systems, we can leverage the Manufacturer-Executor-Evaluator (MEE) pattern to design the system 
to learn directly from the task examples or human actions.

The Manufacturer is responsible for generating the task specification, the Executor is responsible for executing the task,
and the Evaluator is responsible for evaluating the execution result.
The three agents interact with each other, and the system can learn and perform better, 
the process can be under the supervision of human or not.
The system is agnostic to the task, it can be applied to many multi-agent systems as a general framework.

## Manufacturer-Executor-Evaluator (MEE)

The basic idea of Manufacturer-Executor-Evaluator (MEE) is to mimic the human working process
by adapting the agents interaction mechanism from GAN and RL. 
MEE has three agents: Manufacturer, Executor, and Evaluator.

Manufacturer generates the task specification for the Executor
based on the task examples or human actions.
Executor executes the task based on the task specification from the Manufacturer
and gives the result to the Evaluator.
Evaluator evaluates the execution result from the Executor
and gives feedback to the Manufacturer.
The three agents interact with each other and find the optimal solution for executor.
Finally, the system will produce the executor with the task specification to users to execute on the real task.

### Manufacturer

As the first step, Manufacturer generates task specification based on these:

* Data samples, it can be full or partial of the full user provided data. 
Logically, the data should be list of basic X -> Y format. 
Here X is the task input and Y is the expected output. 
For example you want classify if a sentence talked about animal, 
you need to prepare [ (“I like cat”, “YES”), (“I play football”, “No”), … ].
The real format can be extended based on that.

* Task specification in previous iteration, as the process may iterate many times 
to improve the final specification, Manufacturer needs to see the previous specification to optimize.

* Bad cases in previous iteration and comments from Evaluator, 
the Evaluator evaluates the results of Executor and determines if the result meets the criteria,
the failed ones should be feed to Manufacturer to improve.

* Optional user hint. User can optionally give basic hint for Manufacturer to get good start.

### Executor

Manufacturer will generate the task specification and feed to Executor, 
Executor will actually act based on these specification to generate the result for task input.
Intuitively Manufacturer is more powerful and intelligent than the Executor.

Executor is setup by the task specification, then it takes the input X and map X to Y. 
Y is the Executor result and this process can be done in parallel.

Executor is the target specification consumer means it should be configured just what you want to use in the production.

### Evaluator

Evaluator is responsible for evaluating the Executor result based on the criteria,
ideally criteria is provided by user, but this can be enriched by Evaluator from user interaction during the process.

Evaluator takes these as input:

* Executor results, this is the criteria will evaluate on.

* Task specification - from Manufacturer, Evaluator can give direct feedback for Manufacturer to improve.

* Criteria, this is the core of Evaluator and need to be carefully supervised in the pipeline.


## MME Example for Prompt Generation

Prompt engineering is a hot topic in the latest LLM models,
it requires expert knowledge to design the prompt for the model.
Commonly, human experts design the prompt for the model,
evaluating the model performance, then adjust the prompt to get better performance.
The process is time-consuming and requires expert knowledge.
We can leverage the Manufacturer-Executor-Evaluator (MEE) pattern to design the prompt for the model
to learn directly from the task examples to ease the human effort.

![](R/prompt-factory/prompt-factory.png)

For example, we want the model to answer questions with these requirements:

1. The answer should be polite.
2. The answer should be in json format with the key "answer".
3. The answer should be in English.
4. The answer should be in a single sentence.
...

We can provide the task examples to the Manufacturer,
the Manufacturer writes the prompt for the Executor,
the Executor takes the prompt with examples input to generate the answer,
the Evaluator evaluates the answer based on the requirements,
the Evaluator gives feedback to the Manufacturer,
the Manufacturer adjusts the prompt based on the feedback,
the system will find the optimal prompt for the Executor.
Just like the human working process, the system can learn and perform better.

Compared with traditional model training, the MEE pattern does not require
expert knowledge to design the objective function, reward function, etc.
It can learn directly from the task examples or human actions
that can ease the human effort and be applied to many scenarios.

## Conclusion

In this article, I introduced a general agentic pattern for Collective Intelligence,