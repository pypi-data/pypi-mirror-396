# 多轮对话
DeepSeek /chat/completions API 是一个“无状态” API，即服务端不记录用户请求的上下文，用户在每次请求时，需将之前所有对话历史拼接好后，传递给对话 API。

## python展示
创建client
```py
from openai import OpenAI
client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")
```

第一轮
```py
# Round 1
messages = [{"role": "user", "content": "What's the highest mountain in the world?"}]
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

# 将第一轮的回复添加到messages中
messages.append(response.choices[0].message)
print(f"Messages Round 1: {messages}")
```

第二轮
- 要将第一轮中模型的输出添加到 messages 末尾
- 将新的提问添加到 messages 末尾
```py
# Round 2 : messages 追加新的用户消息
messages.append({"role": "user", "content": "What is the second?"})
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

# 将第二轮的回复添加到messages中
messages.append(response.choices[0].message)
print(f"Messages Round 2: {messages}")
```