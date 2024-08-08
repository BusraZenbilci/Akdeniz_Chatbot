import streamlit as st
import pdf_rag
import excel_rag
import time

st.set_page_config(page_title="Akdeniz CSE Chatbot", layout="wide")
st.header("Akdeniz CSE Chatbot")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": 
                                      "Sen, Akdeniz Üniversitesi'nde bilgisayar mühendisliği bölümü hakkında bilgi veren yardımsever bir asistansın. "
                                      "Öğrencilerin Akdeniz Üniversitesi'nde bilgisayar mühendisliği bölümü, bölüm dersleri, harf notu, öğretim üyeleri hakkında sordukları soruları cevaplıyorsun."})


def generate_response(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # File paths
    pdf_files = ["data/ders_islemleri.pdf", "data/yataygecis.pdf", "data/senior-design.pdf", "data/ders_bilgileri.pdf", "data/lisans_genel_bilgiler.pdf"]
    html_files = excel_rag.convert_excel_to_html()

    response_excels, _ = excel_rag.rag_with_html(filepaths=html_files, prompt=prompt)

    # excel_files = ["data/faculty_members.xlsx", "data/research_assistants.xlsx", "data/undergraduate_course_content.xlsx", "data/erasmus_partners.xlsx"]
    # response_excels, _ = excel_rag.rag_with_excels(filepaths=excel_files, prompt=prompt)
    
    response_pdfs, _ = pdf_rag.rag_with_pdfs(filepaths=pdf_files, prompt=prompt)

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
