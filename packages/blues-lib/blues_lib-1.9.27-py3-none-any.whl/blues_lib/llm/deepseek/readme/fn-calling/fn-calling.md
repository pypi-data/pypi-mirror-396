# function calling
Function Calling 让模型能够调用外部工具，来增强自身能力。

## sample
以获取用户当前位置的天气信息为例，展示了使用 Function Calling 的完整 Python 代码。

这个例子的执行流程如下：

1. 用户：询问现在的天气
2. 模型：返回 function get_weather({location: 'Hangzhou'})
3. 用户：调用 function get_weather({location: 'Hangzhou'})，并传给模型。
4. 模型：返回自然语言，"The current temperature in Hangzhou is 24°C."
```py
from openai import OpenAI

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

messages = [{"role": "user", "content": "How's the weather in Hangzhou, Zhejiang?"}]
message = send_messages(messages)
print(f"User>\t {messages[0]['content']}")

tool = message.tool_calls[0]
messages.append(message)

messages.append({"role": "tool", "tool_call_id": tool.id, "content": "24℃"})
message = send_messages(messages)
print(f"Model>\t {message.content}")
```

上述代码中 get_weather 函数功能需由用户提供，模型本身不执行具体函数。