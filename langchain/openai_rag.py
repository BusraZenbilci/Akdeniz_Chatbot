from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd

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
    Bu sorunun yanıtını vermek için yalnızca sana burada verdiğim eldeki bilgileri kullan. Bunların dışına asla çıkma.
    """

    AI_Response = llm_gpt.invoke(final_prompt)
    return AI_Response.content, relevant_documents


def rag_with_excels(filepaths, file_descriptions, prompt):
    all_documents = []
    context_data = ""

    for filepath, description in zip(filepaths, file_descriptions):
        loader = UnstructuredExcelLoader(filepath, mode="elements")
        raw_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=0,
            length_function=len
        )

        splitted_documents = text_splitter.split_documents(raw_documents)
        all_documents.extend(splitted_documents)

        # İşlenen her bir Excel dosyasını HTML formatında kaydetme
        excel_content = raw_documents[0].metadata["text_as_html"]
        html_filename = os.path.splitext(os.path.basename(filepath))[0] + ".html"
        with open(html_filename, "w", encoding="utf-8") as file:
            file.write(excel_content)

        # Excel dosyalarını Pandas DataFrame olarak yükleyin ve içeriği işleyin
        df = pd.read_excel(filepath)
        context_data += f"\n\n{description}:\n{df.to_string(index=False)}"

    vectorstore = FAISS.from_documents(all_documents, embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

    relevant_documents = retriever.invoke(prompt)

    for document in relevant_documents:
        context_data += " " + document.page_content

    # Excel dosyalarının açıklamalarını ekleyin
    context_data += "\n\n" + "\n\n".join(file_descriptions)

    # Eğer metin çok uzunsa, parçalarına bölün
    max_tokens = 1500  # Her bir parça için maksimum token sayısı
    context_parts = [context_data[i:i + max_tokens] for i in range(0, len(context_data), max_tokens)]

    final_responses = []

    for part in context_parts:
        final_prompt = f"""Şöyle bir sorum var: {prompt}
        Bu soruyu yanıtlamak için elimizde şu bilgiler var: {part} .
        Bu sorunun yanıtını vermek için yalnızca sana burada verdiğim eldeki bilgileri kullan. Bunların dışına asla çıkma. Eğer soruyu anlamadıysan veya yanıt için yeterli bilgi yoksa, lütfen bunu belirt.
        """

        AI_Response = llm_gpt.invoke(final_prompt)
        final_responses.append(AI_Response.content)

    combined_response = "\n".join(final_responses)
    return combined_response, relevant_documents

















"""
def rag_with_excels(filepaths, file_descriptions, prompt):
    all_documents = []
    context_data = ""


    for filepath, description in zip(filepaths, file_descriptions):
        loader = UnstructuredExcelLoader(filepath, mode="elements")
        raw_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=0,
            length_function=len
        )

        splitted_documents = text_splitter.split_documents(raw_documents)
        all_documents.extend(splitted_documents)

        # İşlenen her bir Excel dosyasını HTML formatında kaydetme
        excel_content = raw_documents[0].metadata["text_as_html"]
        html_filename = os.path.splitext(os.path.basename(filepath))[0] + ".html"
        with open(html_filename, "w", encoding="utf-8") as file:
            file.write(excel_content)

         # Excel dosyalarını Pandas DataFrame olarak yükleyin ve içeriği işleyin
        df = pd.read_excel(filepath)
        context_data += f"\n\n{description}:\n{df.to_string(index=False)}"

    vectorstore = FAISS.from_documents(all_documents, embeddings)
    retriever = vectorstore.as_retriever(search_type="mmr", k=5, fetch_k=10)

    relevant_documents = retriever.get_relevant_documents(prompt)

    
    for document in relevant_documents:
        context_data += " " + document.page_content  
        
    # Excel dosyalarının açıklamalarını ekleyin
    context_data += "\n\n" + "\n\n".join(file_descriptions)

    final_prompt = f Şöyle bir sorum var: {prompt}
    Bu soruyu yanıtlamak için elimizde şu bilgiler var: {context_data} .
    Bu sorunun yanıtını vermek için yalnızca sana burada verdiğim eldeki bilgileri kullan. Bunların dışına asla çıkma. 
    Eğer soruyu anlamadıysan veya yanıt için yeterli bilgi yoksa, lütfen bunu belirt.
    

    AI_Response = llm_gpt.invoke(final_prompt)
    return AI_Response.content, relevant_documents







def rag_with_excels(filepaths, prompt):
    all_documents = []

    for filepath in filepaths:
        loader = UnstructuredExcelLoader(filepath)
        raw_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len
        )

        splitted_documents = text_splitter.split_documents(raw_documents)
        all_documents.extend(splitted_documents)

    vectorstore = FAISS.from_documents(all_documents, embeddings)
    retriever = vectorstore.as_retriever(search_type="mmr", k=5, fetch_k=10)

    relevant_documents = retriever.get_relevant_documents(prompt)

    context_data = ""
    for document in relevant_documents:
        context_data += " " + document.content

    final_prompt = fŞöyle bir sorum var: {prompt}
    Bu soruyu yanıtlamak için elimizde şu bilgiler var: {context_data} .
    Bu sorunun yanıtını vermek için yalnızca sana burada verdiğim eldeki bilgileri kullan. Bunların dışına asla çıkma. Eğer soruyu anlamadıysan veya yanıt için yeterli bilgi yoksa, lütfen bunu belirt.
    

    AI_Response = llm_gpt.invoke(final_prompt)
    return AI_Response.content, relevant_documents




def rag_with_url(urls, prompt):

    loader = WebBaseLoader(urls)

    raw_documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=0,
        length_function=len
    )

    splitted_documents = text_splitter.split_documents(raw_documents)

    vectorstore = FAISS.from_documents(splitted_documents, embeddings)
    retriever = vectorstore.as_retriever()

    relevant_documents = retriever.get_relevant_documents(prompt)

    context_data = ""

    for document in relevant_documents:
        context_data = context_data + " " + document.page_content

    final_prompt = fŞöyle bir sorum var: {prompt}
    Bu soruyu yanıtlamak için elimizde şu bilgiler var: {context_data} .
    Bu sorunun yanıtını vermek için yalnızca sana burada verdiğim eldeki bilgileri kullan. Bunların dışına asla çıkma.
    

    AI_Response = llm_gpt.invoke(final_prompt)

    return AI_Response.content

"""