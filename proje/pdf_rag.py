from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from openai import embeddings

load_dotenv()

my_key_openai = os.getenv("openai_apikey")

llm_gpt = ChatOpenAI(api_key=my_key_openai, model="gpt-3.5-turbo")

embeddings = OpenAIEmbeddings(api_key=my_key_openai)


def rag_with_pdfs(filepaths, prompt):
    all_texts = []

    for filepath in filepaths:
        loader = PyPDFLoader(filepath)
        raw_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len
        )

        splitted_texts = text_splitter.split_documents(raw_documents)
        all_texts.extend([text.page_content for text in splitted_texts])

    vectorstore = FAISS.from_texts(all_texts, embeddings)
    retriever = vectorstore.as_retriever()

    relevant_documents = retriever.get_relevant_documents(prompt)

    context_data = " ".join([doc.page_content for doc in relevant_documents])

    final_prompt = f"""I have a question: {prompt}
    To answer this question, we have the following information: {context_data}.
    Please provide an answer based only on this information. Do not use any other sources. If you do not understand the question or there is not enough information, please state that.
    """

    AI_Response = llm_gpt.invoke(final_prompt)
    return AI_Response.content, relevant_documents