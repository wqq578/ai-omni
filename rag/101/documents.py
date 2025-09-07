import os
from PyPDF2 import PdfReader
from docx import Document

# =============================
# Step 1: 加载单个文档内容（支持 txt, pdf, docx）
# =============================
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf_file(file_path):
    from PyPDF2 import PdfReader
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def read_docx_file(file_path):
    from docx import Document
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def load_single_document(file_path):
    if file_path.endswith(".txt"):
        content = read_text_file(file_path)
    elif file_path.endswith(".pdf"):
        content = read_pdf_file(file_path)
    elif file_path.endswith(".docx"):
        content = read_docx_file(file_path)
    else:
        raise ValueError("不支持的文件格式")

    # 分段处理：按换行符分割成多个段落
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    return paragraphs

# 示例：指定你要读取的文件路径
file_path = "./data/my_doc.txt"  # 你可以换成 .pdf 或 .docx 文件
documents = load_single_document(file_path)

print(f"共加载 {len(documents)} 段内容")