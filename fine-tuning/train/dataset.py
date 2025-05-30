from datasets import load_dataset

# 加载远程数据集
dataset = load_dataset("tatsu-lab/alpaca")

# 查看结构
print(dataset)


# 保存整个训练集为一个 JSON 文件
# dataset["train"].to_json("./alpaca_train.json", orient="records")
dataset["train"].to_json("./alpaca_train.jsonl", orient="records", lines=True)


# 如果是 .json 文件：
# dataset = load_dataset("json", data_files="./alpaca_train.json", split="train")
# 从本地加载 JSONL 文件
dataset = load_dataset("json", data_files="./alpaca_train.jsonl", split="train")

#  数据集分割
split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = split_dataset["train"]
val_dataset = split_dataset["test"]

print("训练集大小:", len(train_dataset))
print("验证集大小:", len(val_dataset))