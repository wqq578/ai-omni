# -*- coding: utf-8 -*-
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

import os
from PyPDF2 import PdfReader
from docx import Document

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
file_path = "./my_doc.txt"  # 你可以换成 .pdf 或 .docx 文件
documents = load_single_document(file_path)

# =============================
# Step 1: 准备文档数据库
# =============================
# documents = [
#     "Python 是一种高级编程语言，广泛用于 Web 开发、数据分析和人工智能。",
#     "JavaScript 可以在浏览器中运行，并且通过 Node.js 在服务器端也得到了广泛应用。",
#     "Java 以其跨平台特性著称，常用于企业级应用开发。",
#     "Rust 是一门注重安全性的系统编程语言，适用于底层开发。",
# ]

# =============================
# Step 2: 编码文档并构建 FAISS 索引
# =============================
# 下载模型并保存到本地
#model_embedding = SentenceTransformer('all-MiniLM-L6-v2')
#model_embedding.save('./all-MiniLM-L6-v2')  # 保存到当前目录下的文件夹
model_embedding = SentenceTransformer('./all-MiniLM-L6-v2')
doc_embeddings = model_embedding.encode(documents)

dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(doc_embeddings))

# =============================
# Step 3: 检索函数
# =============================
def retrieve(query, top_k=2):
    query_embedding = model_embedding.encode([query])
    distances, indices = index.search(np.array(query_embedding), top_k)
    return [documents[i] for i in indices[0]]

# =============================
# Step 4: 加载 Qwen3 模型（使用 Transformers）
# =============================
#model_name = "Qwen/Qwen3-7B"  # 替换为你本地或 HF 上的模型路径
model_name = "./Qwen/Qwen3-0___6B"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",  # 自动分配到 GPU/CPU
    trust_remote_code=True,
    torch_dtype=torch.float16  # 使用 float16 节省内存
).eval()

# 设置生成参数（可选）
generation_config = GenerationConfig.from_pretrained(model_name)
print("模型加载完成")

# =============================
# Step 5: 定义 RAG 问答函数
# =============================
def rag_qwen3(question):
    context_list = retrieve(question)
    context = "\n".join(context_list)

    prompt = f"""你是问答助手，请根据以下资料回答问题，只输出一句完整的中文回答，不要任何解释、格式或多余内容。

资料：
{context}

问题：
{question}

答案：
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        repetition_penalty=1.2,        # 防止重复
        no_repeat_ngram_size=2,        # 禁止重复二元组
        temperature=0.1,               # 更确定性
        do_sample=False,               # 不采样，使用 greedy 解码
    )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer

# =============================
# Step 6: 测试 RAG + Qwen3 系统
# =============================
if __name__ == "__main__":
    question = "Python 主要用于哪些领域？"
    response = rag_qwen3(question)

    print("Q:", question)
    print("A:", response)