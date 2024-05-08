# Prompt Factory

## Contact me

* Blog -> <https://cugtyt.github.io/blog/llm-application/index>
* Email -> <cugtyt@qq.com>
* GitHub -> [Cugtyt@GitHub](https://github.com/Cugtyt)

---

Prompt is always needed to instruct LLM do what you want it to do,
but describe a task - write your thought down concretly - in a prompt is not trivial, 
it requires time to thought and iterate. But we can leverage LLM to speed and automate this process.

Prompt Factory is for this process, it divides the iterate process to three
steps pipeline and delegates the job to three types of agents, Writer, Actor, Critic.

## Prompt Factory Pipeline

This pipeline mimics the prompt writing iteration: write prompt, run the prompt, evaluate it with criterias.
Then iterate the process to generate better prompt based on the evaluation result.

User needs to prepare the task samples for prompt generation and the criterias for the evaluation, 
this should be the only required input ideally.

The pipeline starts from Writer agent, it is responsible for writing prompt based on the provide data samples 
and generate the draft prompt. Apart from the data samples, Writer can also see the last iteration prompt
and failed samples.

Next the draft prompt will be used by Actor agent to generate responses for each sample data 
for later evaluation.

Then the Critic will evaluate each response based on the criterias provide by user. Critic should at least to
output pass or fail to indicate the result, and other optional messages. 

All the failed samples will be added to next iteration of Writer data samples then repeat the process 
for better prompt.

## Agents

### Writer

As the first step of pipeline, Writer generates prompt based on these:

- Data samples, it can be full or partial of the full user provided data. 
Logically, the data should be list of basic X -> Y format. 
Here X is the input of the final prompt consumer and Y is the expected output. 
For example you want classify if a sentence talked about animal, 
you need to prepare [ ("I like cat", "YES"), ("I play football", "No"), ... ]. 
The real format can be extended based on that.

- Prompt in previous iteration, as the pipeline may iterate many times to improve the final prompt, 
Writer needs to see the previous prompt to optimize.

- Bad cases in previous iteration, the Critic evaluates the response of Actor and determins if the
result meets the criteria, the failed ones should be feed to Writer to improve next prompt.

- Optional user hint. User can optionally give basic hint for Write to get well beginning.

Writer will generate the prompt and feed to Actor and 

### Actor

Actor will

### Critic