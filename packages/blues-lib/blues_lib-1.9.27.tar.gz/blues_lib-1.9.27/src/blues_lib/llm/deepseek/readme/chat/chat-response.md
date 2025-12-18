## Response
OK, 返回一个 chat completion 对象。

### id
{str}
该对话的唯一标识符。

### choices
{list[dict]}
模型生成的 completion 的选择列表。
- `index` : int 该 completion 在选择列表中的索引。
- `finish_reason` : 模型停止生成 token 的原因。
  - `stop` : 模型自然停止生成，或遇到 stop 序列中列出的字符串。
  - `length` : 输出长度达到了模型上下文长度限制，或达到了 max_tokens 的限制。
  - `content_filter` : 输出内容因触发过滤策略而被过滤。
  - `insufficient_system_resource` : 系统推理资源不足，生成被打断。
  
#### message
{dict} 模型生成的 completion 消息。
- `role` : str 消息的角色，其值为 `assistant`。
- `content` : str 模型生成的 completion 内容。
- `reasoning_content` : 仅适用于 deepseek-reasoner 模型。内容为 assistant 消息中在最终答案之前的推理内容。
- `tool_calls` : 模型生成的 tool 调用，例如 function 调用。
  - `id` : str tool 调用的唯一标识符。
  - `type` : str tool 调用的类型，其值为 `function`。
  - `function` : dict 包含 tool 调用的函数信息，包含以下字段：
    - `name` : str 模型调用的 function 名。
    - `arguments` : str 要调用的 function 的参数，由模型生成，格式为 JSON。

> 请注意 tool_calls，模型并不总是生成有效的 JSON，并且可能会臆造出你函数模式中未定义的参数。在调用函数之前，请在代码中验证这些参数。

#### logprobs
dict 该 choice 的对数概率信息。
- `content` : list[dict] 输出 token 的对数概率信息列表。每个元素包含以下字段：
  - `token` : str 输出的 token 字符串。
  - `logprob` : float 该 token 的对数概率值。-9999.0 代表该 token 的输出概率极小，不在 top 20 最可能输出的 token 中。
  - `bytes` : list[int] 该 token 的 UTF-8 字节表示的整数列表。
  - `top_logprobs` : list[dict] 一个包含在该输出位置上，输出概率 top N 的 token 的列表，以及它们的对数概率。
- `reasoning_content` : list[dict] 一个包含输出 token 对数概率信息的列表。每个元素包含以下字段：
  - `token` : str 输出的 token 字符串。
  - `logprob` : float 该 token 的对数概率值。-9999.0 代表该 token 的输出概率极小，不在 top 20 最可能输出的 token 中。
  - `bytes` : list[int] 该 token 的 UTF-8 字节表示的整数列表。
  - `top_logprobs` : list[dict] 一个包含在该输出位置上，输出概率 top N 的 token 的列表，以及它们的对数概率。


### created
{int}
该对话的创建时间，Unix 时间戳。

### model
{str}
生成该 completion 的模型名。

### system_fingerprint
{str}
该对话的系统指纹，用于标识模型的运行环境。

### object
{str}
对象的类型, 其值为 `chat.completion`。

### usage
{dict}
该对话的使用统计信息，包含以下字段：
- `prompt_tokens` : int 用户 prompt 所包含的 token 数。该值等于 prompt_cache_hit_tokens + prompt_cache_miss_tokens
- `prompt_cache_hit_tokens` : int 从缓存中命中的 prompt token 数。
- `prompt_cache_miss_tokens` : int 未命中缓存的 prompt token 数。
- `completion_tokens` : int 模型 completion 产生的 token 数。
- `total_tokens` : int 该请求中，所有 token 的数量（prompt + completion）。
- `completion_tokens_details` : dict 模型 completion 产生的 token 数的详细信息，包含以下字段：
  - `reasoning_tokens` : int 推理模型所产生的思维链 token 数量

## success demo
```json
{
  "id": "930c60df-bf64-41c9-a88e-3ec75f81e00e",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "Hello! How can I help you today?",
        "role": "assistant"
      }
    }
  ],
  "created": 1705651092,
  "model": "deepseek-chat",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 10,
    "prompt_tokens": 16,
    "total_tokens": 26
  }
}
```
## failed demo
```json
{
  "error": {
    "message": "Authentication Fails, Your api key: ****KEN> is invalid",
    "type": "authentication_error",
    "param": null,
    "code": "invalid_request_error"
  }
}
```

