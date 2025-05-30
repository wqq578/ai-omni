import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread

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
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# 编码输入
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

# 创建 streamer
streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

# 构建生成参数
generation_kwargs = dict(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"],
    streamer=streamer,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id
)

# 启动一个线程进行推理
thread = Thread(target=model.generate, kwargs=generation_kwargs)
thread.start()

# 实时读取并输出生成内容
print("模型回复：")
for new_text in streamer:
    print(new_text, end="", flush=True)

thread.join()