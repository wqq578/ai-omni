import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# 设置模型路径
model_path = "./Qwen/Qwen3-0___6B"

# 加载 tokenizer 和 model
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    torch_dtype=torch.bfloat16
)

# 构造对话输入
messages = [
    {"role": "system", "content": "你是一个医学专家，请给出专业建议。"},
    {"role": "user", "content": "医生，我最近被诊断为糖尿病，听说碳水化合物的选择很重要，我应该选择什么样的碳水化合物呢？"}
]

# 应用 chat template
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# 编码输入
inputs = tokenizer(text, return_tensors="pt").to(model.device)

# 生成响应
outputs = model.generate(
    inputs.input_ids,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)

# 解码输出
response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)

print("模型回复：")
print(response)