import os                                                                       
from langchain.agents import load_tools                                         
from langchain.agents import initialize_agent                                   
from langchain.llms import OpenAI                                               
from langchain.prompts import PromptTemplate 

llm = OpenAI(model_name='text-davinci-003', temperature = 0.7, openai_api_key = "<my openAPI key> ")
tools = load_tools(['serpapi'], llm=llm)

PREFIX = '''You are an AI data scientist. You have done years of research in studying all the AI algorthims. You also love to write. On free time you write blog post for articulating what you have learned about different AI algorithms. Do not forget to include information on the algorithm's benefits, disadvantages, and applications. Additionally, the blog post should explain how the algorithm advances model reasoning by a whopping 70% and how it is a plug in and play version, connecting seamlessly to other components.
'''

FORMAT_INSTRUCTIONS = """To use a tool, please use the following format:
'''
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
'''

When you have gathered all the information regarding AI algorithm, just write it to the user in the form of a blog post.

'''
Thought: Do I need to use a tool? No
AI: [write a blog post]
'''
"""

SUFFIX = '''

Begin!

Previous conversation history:
{chat_history}

Instructions: {input}
{agent_scratchpad}
'''

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    return_intermediate_steps=True,
    agent_kwargs={
        'prefix': PREFIX, 
        'format_instructions': FORMAT_INSTRUCTIONS,
        'suffix': SUFFIX
    }
)

res = agent({"input": query.strip()})
print(res['output'])