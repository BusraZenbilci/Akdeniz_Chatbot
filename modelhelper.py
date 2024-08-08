import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

my_key_openai = os.getenv("openai_apikey")

from langchain_openai import ChatOpenAI

def ask_gpt(prompt, temperature, max_tokens):

    llm = ChatOpenAI(api_key=my_key_openai, temperature=temperature, max_tokens=max_tokens, model="gpt-3.5-turbo-0125")

    AI_Response = llm.invoke(prompt)

    return AI_Response.content


my_key_google = os.getenv("google_apikey")

from langchain_google_genai import ChatGoogleGenerativeAI

def ask_gemini(prompt, temperature):

    llm = ChatGoogleGenerativeAI(google_api_key=my_key_google, temperature=temperature, model="gemini-1.5-flash")

    AI_Response = llm.invoke(prompt)

    return AI_Response.content





my_key_anthropic = os.getenv("anthropic_apikey")

from langchain_community.chat_models import ChatAnthropic

def ask_claude(prompt, temperature, max_tokens):

    llm = ChatAnthropic(anthropic_api_key=my_key_anthropic, temperature=temperature, max_tokens=max_tokens, model_name="claude-v1")

    AI_Response = llm.invoke(prompt)

    return AI_Response.content
