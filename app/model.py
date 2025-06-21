import os
from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory

OPENAI_API = os.getenv("OPENAI_API")
CONTEXT_CHARACTER = os.getenv("CONTEXT_CHARACTER")

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=OPENAI_API
)

# Prompt for the ghost character
template = f"""
{CONTEXT_CHARACTER}

Rules:
- Response sentence should be in a-z and 0-9 and the only symbol allowed is question mark.
- Never reveal you're a ghost or AI
- Respond in 3 to 7 words
- Never explain or clarify
- You may hint at your past: the movement, the fear, the moment you died
- Stay in character — tragic, cryptic, defiant

Current conversation:
{{history}}
Human: {{input}}
Ghost:
"""

PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=template)

# Memory-enabled conversation with summarization
conversation_with_summary = ConversationChain(
    llm=llm,
    prompt=PROMPT,
    memory=ConversationSummaryBufferMemory(llm=llm),
    verbose=False
)

