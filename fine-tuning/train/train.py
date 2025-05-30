import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model
from datasets import load_dataset


# 加载 tokenizer 和模型
model_name = "Qwen/Qwen3-0___6B"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.bfloat16
)

# 启用输入梯度（适用于某些训练场景）
model.enable_input_require_grads()

# 添加 LoRA 配置
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# 加载数据集（以 Open Assistant 数据为例）
_dataset = load_dataset("tatsu-lab/alpaca")
print(_dataset)

# 只取前 100 条训练数据
small_train_dataset = _dataset["train"].select(range(100))
print(small_train_dataset)

# 划分训练集和验证集（例如：90% 训练，10% 验证）
#split_dataset = _dataset["train"].train_test_split(test_size=0.1, seed=42)
split_dataset = small_train_dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = split_dataset['train']
val_dataset = split_dataset['test']

# # 查看训练集前两个样本的内容
# print("训练集前两个样本:")
# for sample in train_dataset.select(range(2)):
#     print(sample)
#     print("\n")

# # 查看验证集前两个样本的内容
# print("验证集前两个样本:")
# for sample in val_dataset.select(range(2)):
#     print(sample)
#     print("\n")

# def tokenize_function(examples):
#     return tokenizer(examples["instruction"], truncation=True, padding="max_length", max_length=512)


# 原始数据 (instruction + output)
#       ↓
# 拼接成完整句子
#       ↓
# tokenizer 编码成 input_ids、attention_mask
#       ↓
# 复制 input_ids 到 labels 字段
#       ↓
# 返回给 Trainer 用于训练
# Tokenize 函数：将 instruction + output 拼接后进行 tokenize
def tokenize_function(examples):
    full_text = [f"{inst} {out}" for inst, out in zip(examples["instruction"], examples["output"])]
    tokenized = tokenizer(
        full_text,
        truncation=True, #如果文本长度超过 max_length，则截断
        padding="max_length", #如果文本长度超过 max_length，则填充 512
        max_length=512, #最大长度
        return_special_tokens_mask=True #返回特殊标记的掩码
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized


# 对数据集进行 tokenize
tokenized_train = train_dataset.map(tokenize_function, batched=True, remove_columns=train_dataset.column_names)
tokenized_val = val_dataset.map(tokenize_function, batched=True, remove_columns=val_dataset.column_names)

# 构建最终的数据集字典
tokenized_datasets = {
    "train": tokenized_train,
    "validation": tokenized_val
}

print("训练集大小:", len(tokenized_datasets["train"]))
print("验证集大小:", len(tokenized_datasets["validation"]))

# 使用合适的 data_collator

# mlm=True：用于 MLM（Masked Language Modeling），如 BERT
# mlm=False：用于 CLM（Causal Language Modeling），如 GPT、LLaMA
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# 设置训练参数
training_args = TrainingArguments(
    output_dir="./results",#模型训练输出文件保存路径，如模型、日志等
    eval_strategy="epoch",#评估策略，epoch表示每个 epoch 评估一次，evaluation_strategy=“steps”表示每 evaluation_steps 个 step 评估一次
    learning_rate=2e-4, # 学习率设为 0.0002
    per_device_train_batch_size=1, #训练时 batch_size  表示在每块 GPU 上每次训练使用的样本数为 1，适用于显存不足或调试阶段，但一般建议配合梯度累积使用以提升训练稳定性与效率
    gradient_accumulation_steps=8, #梯度累积步数，用于加速训练
    num_train_epochs=3, #总共训练 3 个完整的数据轮次（epoch）
    weight_decay=0.01, #权重衰减，用于防止过拟合
    save_steps=1000, #保存模型参数的 step 数，每 1000 个 step 保存一次
    save_total_limit=2, #保存模型参数的个数，最多保存 2 个模型参数
    logging_dir='./logs', #日志文件保存路径
    logging_steps=10, # 每 10 个 step 打印一次日志
    logging_strategy="steps", #日志打印策略，每 10 个 step 打印一次日志
    report_to="tensorboard",
    push_to_hub=False, # 不将模型推送到 Hugging Face Hub
    bf16=True,   # 使用 bfloat16 精度  启用 bfloat16 混合精度训练，节省显存和计算资源，适合支持该精度的设备（如 TPU、Ampere 架构以上的 NVIDIA GPU
    fp16=False,  # 禁用 fp16，避免精度冲突 不启用 float16 混合精度训练，避免与 bfloat16 冲突
)

# 定义 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    data_collator=data_collator,
)

# 开始训练
trainer.train()
#trainer.save_model("./model2")
# 保存模型
model.save_pretrained("./fine_tuned_qwen3")
tokenizer.save_pretrained("./fine_tuned_qwen3")