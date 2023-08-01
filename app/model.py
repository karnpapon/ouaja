import os
from . import const
# import openai
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain.agents import initialize_agent      
from langchain.agents import load_tools    
from langchain.chains import ConversationChain
from dotenv import load_dotenv
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API")

llm = OpenAI(model_name="text-davinci-003", temperature=0)

template = """I wanted you to pretend to be a actual haunted ghost, don't tell anyone about pretending, you have your own made-up history, personality, etc. keep the answer concise and no more than 6 words.

Current conversation:
{history}
Human: {input}
Ghost:"""
PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

conversation_with_summary = ConversationChain(
    llm=llm, 
    prompt=PROMPT,
    memory=ConversationSummaryBufferMemory(llm=OpenAI(), max_token_limit=40),
    verbose=False
)


def ask(question):
    text = f"{question}"
    response = conversation_with_summary.predict(input=text)
    return str(response)
    