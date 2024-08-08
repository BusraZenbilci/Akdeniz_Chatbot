import openai
import os
from dotenv import load_dotenv
import streamlit as st

# .env dosyasını yükleyin
load_dotenv()

# API anahtarını alın
my_key = os.getenv("openai_apikey")

# API anahtarını ayarlayın
openai.api_key = my_key

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": "Sen yardımsever bir asistansın."})

def generate_response(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})

    AI_Response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
    )

    return AI_Response.choices[0].message["content"]

st.header("Akdeniz CSE Chatbot")
st.divider()

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajınızı Giriniz"):
    st.chat_message("user").markdown(prompt)

    response = generate_response(prompt)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
