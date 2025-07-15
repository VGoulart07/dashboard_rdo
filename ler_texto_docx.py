import os
from docx import Document

folder_path = r"C:\Users\vinic\OneDrive - DSolar\Documentos\Performance\RDO"

for filename in os.listdir(folder_path):
    if filename.lower().endswith('.docx'):
        filepath = os.path.join(folder_path, filename)
        print(f"\n\n==== Conteúdo do arquivo: {filename} ====\n")
        doc = Document(filepath)
        for para in doc.paragraphs:
            print(para.text)
