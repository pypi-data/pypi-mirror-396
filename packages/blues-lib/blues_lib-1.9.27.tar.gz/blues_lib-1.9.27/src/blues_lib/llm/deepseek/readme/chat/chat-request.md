# Chat
根据输入的上下文，来让模型补全对话内容

```
POST https://api.deepseek.com/chat/completions
```
[request and respone](https://api-docs.deepseek.com/zh-cn/api/create-chat-completion)

## Request

### model
{str} required
使用的模型的 ID
- `deepseek-chat` : DeepSeek-V3.2-Exp 的非思考模式，
- `deepseek-reasoner` : DeepSeek-V3.2-Exp 的思考模式。

### stream 
{boolean} optional
- 默认值：False
如果设置为 True，将会以 SSE（server-sent events）的形式以流式发送消息增量。消息流以 `data: [DONE]` 结尾。

### response_format
{dict} optional
一个 object，指定模型必须输出的格式，
- `{"type": "text"}` : 文本，默认值
- `{ "type": "json_object" }` ：启用 JSON 模式，该模式保证模型生成的消息是有效的 JSON。
  - 必须通过系统或用户消息指示模型生成 JSON。否则，模型可能会生成不断的空白字符，直到生成达到令牌限制，从而导致请求长时间运行并显得“卡住”。
  - 如果 `finish_reason="length"`，这表示生成超过了 max_tokens 或对话超过了最大上下文长度，消息内容可能会被部分截断。

### messages
{list[dict]} required
对话的消息列表。

#### system message
用于输入系统提示，典型的是告诉系统当前角色，例如：
- 你是一个专业的历史老师
- 你是一个专业的数学老师

对象结构
- role : required 该消息的发起角色，其值为"system"
- content :  required 系统消息的内容。
- name : optional 可以选填的参与者的名称，为模型提供信息以区分相同角色的参与者

#### user message
用户输入的消息，用于模型补全对话内容。

对象结构
- role : required 该消息的发起角色，其值为"user"
- content :  required 用户消息的内容。
- name : optional 可以选填的参与者的名称，为模型提供信息以区分相同角色的参与者

#### assistant message
助手消息，用于模型补全对话内容。模拟助手的回答，可用于few-shot学习。

对象结构
- role : required 该消息的发起角色，其值为"assistant"
- content :  required 助手消息的内容。
- name : optional 可以选填的参与者的名称，为模型提供信息以区分相同角色的参与者
- prefix : optional 强制模型在其回答中以此 assistant 消息中提供的前缀内容开始。
  - 必须设置 base_url="https://api.deepseek.com/beta" 来使用此功能。
  - 例如：`{"role": "assistant", "content": "你好", "prefix": "你好，我是 DeepSeek"}`
  
#### tool message
当前与function call 相关的消息，用于模型补全对话内容。

对象结构
- role : required 该消息的发起角色，其值为"tool"
- content :  required 工具调用的结果。
- tool_call_id : required 此消息所响应的 tool call 的 ID。

### temperature
{float} optional
- 范围：[0.0, 2.0]
- 默认值：1.0

采样温度，介于 0 和 2 之间。更高的值，如 0.8，会使输出更随机，而更低的值，如 0.2，会使其更加集中和确定。 我们通常建议可以更改这个值或者更改 top_p，但不建议同时对两者进行修改。

### top_p 
{float} optional
- 范围：[0.0, 1.0]
- 默认值：1.0

作为调节采样温度的替代方案，模型会考虑前 top_p 概率的 token 的结果。所以 0.1 就意味着只有包括在最高 10% 概率中的 token 会被考虑。 

### stop
{list[str]|str}
一个 string 或最多包含 16 个 string 的 list，在遇到这些词时，API 将停止生成更多的 token。
- 比如用在前缀续写时设置结尾字符串

### tools
模型可能会调用的 tool 的列表。目前，仅支持 function 作为工具。使用此参数来提供以 JSON 作为输入参数的 function 列表。最多支持 128 个 function。
具体参考 function calling 文档。
```py
{
  "type": "function",
  "function": {
    "name": "get_current_weather",
    "description": "获取当前天气",
    # 如果设置为 true，API 将在函数调用中使用 strict 模式，以确保输出始终符合函数的 JSON schema 定义。
    "strict": false,
    # function 的输入参数，以 JSON Schema 对象描述。
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "城市和国家，例如：旧金山，美国"
        },
        "unit": {
          "type": "string",
          "enum": ["摄氏度", "华氏度"]
        }
      },
      "required": ["location"]
    }
  }
}
```

### tool_choice
{dict|str}
控制模型调用 tool 的行为。
- none 意味着模型不会调用任何 tool，而是生成一条消息。
- auto 意味着模型可以选择生成一条消息或调用一个或多个 tool。
- required 意味着模型必须调用一个或多个 tool。
- 通过 `{"type": "function", "function": {"name": "my_function"}}` 指定特定 tool，会强制模型调用该 tool。

### stream_object
{dict}
流式输出相关选项。只有在 stream 参数为 true 时，才可设置此参数。
- `include_usage` : 如果设置为 true，在流式消息最后的 data: [DONE] 之前将会传输一个额外的块。此块上的 usage 字段显示整个请求的 token 使用统计信息，而 choices 字段将始终是一个空数组。所有其他块也将包含一个 usage 字段，但其值为 null。

### max_tokens
{int}
限制一次请求中模型生成 completion 的最大 token 数。输入 token 和输出 token 的总长度受模型的上下文长度的限制。

当前上下文长度是128K，大约4000个中文字符或8000个英文字符。

### presence_penalty
{float}
- 范围：[-2.0, 2.0]
- 默认值：0.0

 presence_penalty 用于调整模型生成文本时对已出现过的 token 的惩罚。较高的 presence_penalty 值会使模型更倾向于生成新的 token，而不是重复出现过的 token。

### frequency_penalty
{float}
- 范围：[-2.0, 2.0]
- 默认值：0.0
frequency_penalty 用于调整模型生成文本时对已出现过的 token 的惩罚。较高的 frequency_penalty 值会使模型更倾向于生成出现频率较低的 token。

### frequency_penalty
{float}
- 范围：[-2.0, 2.0]
- 默认值：0.0
介于 -2.0 和 2.0 之间的数字。如果该值为正，那么新 token 会根据其在已有文本中的出现频率受到相应的惩罚，降低模型重复相同内容的可能性。

### logprobs
{bool}
是否返回所输出 token 的对数概率。如果为 true，则在 message 的 content 中返回每个输出 token 的对数概率。

### top_logprobs
{int}
一个介于 0 到 20 之间的整数 N，指定每个输出位置返回输出概率 top N 的 token，且返回这些 token 的对数概率。指定此参数时，logprobs 必须为 true。

### request demo
```json
{
  "messages": [
    {
      "content": "You are a helpful assistant",
      "role": "system"
    },
    {
      "content": "Hi",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",
  "frequency_penalty": 0,
  "max_tokens": 4096,
  "presence_penalty": 0,
  "response_format": {
    "type": "text"
  },
  "stop": null,
  "stream": false,
  "stream_options": null,
  "temperature": 1,
  "top_p": 1,
  "tools": null,
  "tool_choice": "none",
  "logprobs": false,
  "top_logprobs": null
}
```
