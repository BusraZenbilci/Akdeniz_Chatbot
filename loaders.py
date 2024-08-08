#UnstructuredExcelLoader - Bir Excel dosyasından içerik yükleme
from langchain_community.document_loaders import UnstructuredExcelLoader

filepath1 = "./data/undergraduate_course_content.xlsx"

loader = UnstructuredExcelLoader(filepath1, mode="elements")

docs = loader.load()

excel_content = docs[0].metadata["text_as_html"]

with open("undergraduate_course_content.html", "w") as file:
    file.write(excel_content)
