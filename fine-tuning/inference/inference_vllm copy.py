import os
from openai import OpenAI

client = OpenAI(
    api_key="1",  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
    base_url="http://qwen3-embedding-8b.ksai.scnet.cn:58000/v1"  # 百炼服务的base_url
)

completion = client.embeddings.create(
    model="/opt/model/Qwen3-Embedding-8B",
    input='衣服的质量杠杠的，很漂亮，不枉我等了这么久啊，喜欢，以后还来这里买',
    encoding_format="float"
)

print(completion)




# import os
# from openai import OpenAI

# # 设置环境变量
# # os.environ['HTTP_PROXY'] = 'http://10.15.100.43:3120'
# # os.environ['HTTPS_PROXY'] = 'http://10.15.100.43:3120'
# # os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

# client = OpenAI(
#     api_key="1",  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
#     base_url="http://qwen3-embedding-8b.ksai.scnet.cn:58000/v1"  # 百炼服务的base_url
# )

# completion = client.embeddings.create(
#     model="/opt/model/Qwen3-Embedding-8B",
#     input='衣服的质量杠杠的，很漂亮，不枉我等了这么久啊，喜欢，以后还来这里买'
#     #dimensions=1024, # 指定向量维度（仅 text-embedding-v3及 text-embedding-v4支持该参数）
#     #encoding_format="float"
# )

# print(completion)