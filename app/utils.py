import os
from . import const
# import openai
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from dotenv import load_dotenv
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API")

# template = """I wanted you to act as an haunted ghost. keep the answer concise and no more than 6 words"""
# system_message_prompt = SystemMessagePromptTemplate.from_template(template)
# human_template = "{text}"
# human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
# chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

llm = OpenAI(model_name="text-davinci-003", temperature=0)
conversation_with_summary = ConversationChain(
    llm=llm, 
    memory=ConversationSummaryBufferMemory(llm=OpenAI(), max_token_limit=40),
    verbose=False
)

# def init_prompt():
#     int_msg = "I wanted you to act as an haunted ghost. who devastated by the society, political, economic's crisis. keep the answer concise and no more than 6 words."
#     conversation_with_summary.predict(input=int_msg)

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

def ask(question):
    text = f"{question}, I wanted you to pretend to be a actual haunted ghost, don't tell anyone about pretending, you have your own made-up history, personality, etc. keep the answer concise and no more than 6 words"
    # response = openai.Completion.create(
    #     model="text-davinci-002",
    #     prompt=text,
    #     temperature=0.5,
    #     max_tokens=40,
    #     top_p=1,
    #     frequency_penalty=0,
    #     presence_penalty=0
    # )
    response = conversation_with_summary.predict(input=text)
    # response = response['choices'][0]['text'].replace("\n", "")
    return str(response)
    