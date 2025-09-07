import requests
import random

token_cy_user= "sk-NTk4LTIxODU5OTcwNjc1LTE3NTA5MTYyNjU3MjQ="
token_user_cy = "sk-MzIzLTExMzE3NDI0MTQ1LTE3NTA4MjAwODkzNjU="
ebd1 = "sk-OTc2LTIxMDc3ODAxMTE3LTE3NTA5MTY5NjEzNzU="
ebd2 = ""
ebd3 = ""

API_URL =  "https://itos.sugon.com/acx/llm/v1/embeddings"
headers = {"Content-Type": "application/json",
           "Authorization": f"Bearer {token_user_cy}"}

# 生成指定 token 长度的文本
def generate_text(token_count):
    base_char = "测"  # 单个中文字符 ≈ 1 token
    return base_char * token_count

def random_num():
    return random.choice([2048,1536,1024,768,512,256,28,64])

def max_string_list():
    random_dimension_1 = random_num()
    random_dimension_2 = random_num()
    random_dimension_3 = random_num()
    test_cases_all = [
        # # dimension 参数测试
        # (f"dimension设置为{random_dimension_1}", [generate_text(3) for _ in range(10)],random_dimension_1,200),
        # (f"dimension设置为{random_dimension_2}", [generate_text(3) for _ in range(10)],random_dimension_2,200),
        # (f"dimension设置为{random_dimension_3}", [generate_text(3) for _ in range(10)], random_dimension_3, 200),
        # input 参数测试
        # ("含需求范围内超长项（单条<=8192Tokens）列表, expected: 200 status",[generate_text(8191)] , 1024, 200)
        # ("含需求范围内超长项（单条<=8192Tokens）列表, expected: 200 status",[generate_text(1)] * 9 + [generate_text(8191)],1024,200),
        # ("含超范围超长项（单条>8192Tokens）列表, expected: 422 status",[generate_text(1)] * 9 + [generate_text(8192)],1024,422),
        # ("超数量列表 (11项)，, expected: 422 status",[generate_text(10)] * 11, 1024,422),
        # # 逐渐增加输入字符串列表的大小,测试最大输入Tokens量
        ("列表 (6x8191)",[generate_text(8191)] * 5, 1024,200)
        # ("列表 (8x8191)",[generate_text(8191) for _ in range(8)],1024,200)
        # ("列表 (9x8191)",[generate_text(8191) for _ in range(9)],1024,200)
        # ("列表 (10x8191)",[generate_text(8191) for _ in range(10)],1024,200)
        # ("列表 (10x6000)",[generate_text(6000) for _ in range(10)], 1024,200),
        # ("列表 (10x7000)",[generate_text(7000) for _ in range(10)],1024,200),
        # ("列表 (10x7200)",[generate_text(6000) for _ in range(10)],1024,200),
        # ("列表 (10x7400)",[generate_text(6000) for _ in range(10)],1024,200),
        # ("列表 (10x7500)",[generate_text(8000) for _ in range(10)],1024,200),
        # ("列表 (10x7600)",[generate_text(8000) for _ in range(10)],1024,200),
        # ("列表 (10x7700)",[generate_text(8000) for _ in range(10)],1024,200),
        # ("列表 (10x7800)",[generate_text(9000) for _ in range(10)],1024,200),
    ]

    test_cases = [
        ([generate_text(10) for _ in range(10)], "正常列表 (10x10)"),
        ([generate_text(1)] * 9 + [generate_text(8191)], "含超长项列表"),
        ([generate_text(10)] * 11, "超数量列表 (11项)")
    ]

    for desc, input_list, dimension, exp_status in test_cases_all:
        data = {
            "model": "Qwen3-Embedding-8B",
            "input": input_list,
            "dimension": dimension,
            "encoding_format": "float"
        }
        response = requests.post(API_URL, headers=headers, json=data)
        # vector = response.json()["data"][0]["embedding"]
        # dimension_len = len(vector) / len(data["input"])
        print(f"\nCase: {desc}")
        print(f"Status: {response.status_code}")


        if response.status_code == 200:
            # if dimension != "1024":
            #     print(f"Dimension: {dimension_len}")
            #     assert dimension_len == dimension
            #     continue
            # assert response.status_code == exp_status
            data = response.json().get("data", [])
            usage = response.json()["usage"]["total_tokens"]
            print(f"Total token usage:{usage}")
            print(f"Returned {len(data)} embeddings\n")
        elif response.status_code == 422:
            # assert response.status_code == exp_status
            error = response.json().get("error", {})
            print(f"Param Error: {error.get('message')}\n")


max_string_list()