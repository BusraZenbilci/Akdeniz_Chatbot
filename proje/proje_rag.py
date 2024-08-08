from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv

load_dotenv()

my_key_openai = os.getenv("openai_apikey")

llm_gpt = ChatOpenAI(api_key=my_key_openai, model="gpt-3.5-turbo")

embeddings = OpenAIEmbeddings(api_key=my_key_openai)

def ask_gpt(prompt):
    AI_Response = llm_gpt.invoke(prompt)
    return AI_Response.content

def rag_with_pdfs(filepaths, prompt):
    all_documents = []

    for filepath in filepaths:
        loader = PyPDFLoader(filepath)
        raw_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len
        )

        splitted_documents = text_splitter.split_documents(raw_documents)
        all_documents.extend(splitted_documents)

    vectorstore = FAISS.from_documents(all_documents, embeddings)
    retriever = vectorstore.as_retriever()

    relevant_documents = retriever.get_relevant_documents(prompt)

    context_data = ""
    for document in relevant_documents:
        context_data += " " + document.page_content

    final_prompt = f"""Şöyle bir sorum var: {prompt}
    Bu soruyu yanıtlamak için elimizde şu bilgiler var: {context_data} .
    Bu sorunun yanıtını vermek için yalnızca sana burada verdiğim eldeki bilgileri kullan. Bunların dışına asla çıkma. Eğer soruyu anlamadıysan veya yanıt için yeterli bilgi yoksa, lütfen bunu belirt.
    """

    AI_Response = llm_gpt.invoke(final_prompt)
    return AI_Response.content, relevant_documents
