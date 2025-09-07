import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer

# 加载模型和 tokenizer
model_path = "./Qwen/Qwen3-0___6B"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype=torch.bfloat16)

# 构造输入
messages = [
    {"role": "system", "content": "你是一个医学专家，请给出专业建议。"},
    {"role": "user", "content": "医生，我最近被诊断为糖尿病，听说碳水化合物的选择很重要，我应该选择什么样的碳水化合物呢？"}
]

prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

# 使用 TextStreamer 实现实时输出（只能打印在终端）
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

# 推理并实时输出
output = model.generate(
    **inputs,
    streamer=streamer,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id
)