import streamlit as st
import openai_rag
import time

st.set_page_config(page_title="Akdeniz CSE Chatbot", layout="wide")
st.header("Akdeniz CSE Chatbot")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": 
                                      "Sen, sadece Akdeniz Üniversitesi'nde bilgisayar mühendisliği bölümü hakkında bilgi veren yardımsever bir asistansın. "
                                      "Öğrencilerin Akdeniz Üniversitesi'nde bilgisayar mühendisliği bölümü, bölüm dersleri, harf notu, öğretim üyeleri hakkında sordukları soruları cevaplıyorsun."})

def generate_response(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Birden fazla PDF dosyasının yolu
    pdf_files = ["data/ders_islemleri.pdf", "data/yataygecis.pdf", "data/senior-design.pdf", "data/mudek_akr.pdf", "data/lisans_genel_bilgiler.pdf"]
    excel_files = ["data/faculty_members.xlsx", "data/research_assistants.xlsx", "data/undergraduate_course_content.xlsx", "data/erasmus_partners.xlsx"]
    
    # Excel dosyaları için açıklamalar
    file_descriptions = [
        "faculty_members.xlsx dosyası, Akdeniz Üniversitesi Bilgisayar Mühendisliği bölümü profesör, doçent ve doktor öğretim üyelerinin bilgilerini içerir.",
        "research_assistants.xlsx dosyası, Akdeniz Üniversitesi Bilgisayar Mühendisliği bölümü araştırma görevlilerinin (asistanların) bilgilerini içerir.",
        "undergraduate_course_content.xlsx dosyası, Akdeniz Üniversitesi Bilgisayar Mühendisliği bölümü ders bilgilerini içerir.",
        "erasmus_partners.xlsx dosyası, Akdeniz Üniversitesi Bilgisayar Mühendisliği bölümünün öğrenci değişim (erasmus) programında anlaşmalı olduğu okulları, "
        "okulların bulunduğu ülkeleri ve kontenjanı içerir"
    ]

    response_excels, _ = openai_rag.rag_with_excels(filepaths=excel_files, file_descriptions=file_descriptions, prompt=prompt)
    response_pdfs, _ = openai_rag.rag_with_pdfs(filepaths=pdf_files, prompt=prompt)

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