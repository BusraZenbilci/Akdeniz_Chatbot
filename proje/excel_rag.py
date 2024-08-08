import streamlit as st
import proje_rag
import time
import os
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

# Initialize LLM and embeddings
my_key_openai = os.getenv("openai_apikey")
llm_gpt = ChatOpenAI(api_key=my_key_openai, model="gpt-3.5-turbo")
embeddings = OpenAIEmbeddings(api_key=my_key_openai)

st.set_page_config(page_title="Akdeniz CSE Chatbot", layout="wide")
st.header("Akdeniz CSE Chatbot")
st.divider()


if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": 
                                      "Sen, Akdeniz Üniversitesi'nde bilgisayar mühendisliği bölümü hakkında bilgi veren yardımsever bir asistansın. "
                                      "Öğrencilerin Akdeniz Üniversitesi'nde bilgisayar mühendisliği bölümü, bölüm dersleri, harf notu, öğretim üyeleri hakkında sordukları soruları cevaplıyorsun."})

# Convert Excel files to HTML
def convert_excel_to_html():
    excel_files = ["data/faculty_members.xlsx", 
                   "data/research_assistants.xlsx", 
                   "data/undergraduate_course_content.xlsx", 
                   "data/erasmus_partners.xlsx"]
    html_files = []

    for filepath in excel_files:
        loader = UnstructuredExcelLoader(filepath, mode="elements")
        docs = loader.load()
        excel_content = docs[0].metadata["text_as_html"]
        html_filepath = filepath.replace(".xlsx", ".html")
        with open(html_filepath, "w", encoding="utf-8") as file:
            file.write(excel_content)
        html_files.append(html_filepath)

    return html_files

def summarize_text(text, max_length=3000):
    if len(text) <= max_length:
        return text
    summarization_prompt = f"Please summarize the following text:\n\n{text}"
    summary_response = llm_gpt.invoke(summarization_prompt)
    return summary_response.content

def rag_with_html(filepaths, prompt, max_documents=5, max_length=3000):
    all_texts = []

    for filepath in filepaths:
        loader = UnstructuredHTMLLoader(filepath)
        raw_documents = loader.load()

        all_texts.extend([doc.page_content for doc in raw_documents])

    ## FAISS bizim için dökümanlardan vektör yaratmamızı sağlıyor
    vectorstore = FAISS.from_texts(all_texts, embeddings)
    retriever = vectorstore.as_retriever()

    relevant_documents = retriever.get_relevant_documents(prompt)[:max_documents]
    relevant_texts = [doc.page_content for doc in relevant_documents]
    summarized_texts = [summarize_text(text, max_length=max_length) for text in relevant_texts]

    context_data = " ".join(summarized_texts)

    final_prompt = f"""I have a question: {prompt}
    To answer this question, we have the following information: {context_data}.
    Please provide an answer based only on this information. Do not use any other sources. If you do not understand the question or there is not enough information, please state that.
    """

    AI_Response = llm_gpt.invoke(final_prompt)
    return AI_Response.content, relevant_documents

def generate_response(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # File paths
    pdf_files = ["data/ders_islemleri.pdf", 
                 "data/yataygecis.pdf", 
                 "data/senior-design.pdf", 
                 "data/ders_bilgileri.pdf", 
                 "data/lisans_genel_bilgiler.pdf",
                 "data/Staj_Yonergesi.pdf"]
    html_files = convert_excel_to_html()

    response_excels, _ = rag_with_html(filepaths=html_files, prompt=prompt)
    response_pdfs, _ = proje_rag.rag_with_pdfs(filepaths=pdf_files, prompt=prompt)

    combined_response = f"{response_pdfs}\n\n{response_excels}"

    return combined_response

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajınızı Giriniz"):
    st.chat_message("user").markdown(prompt)
    response = generate_response(prompt)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
