# strict mode
在 strict 模式下，模型在输出 Function 调用时会严格遵循 Function 的 JSON Schema 的格式要求，以确保模型输出的 Function 符合用户的定义。
要使用 strict 模式，需要：
- 用户需要设置base_url="https://api.deepseek.com/beta" 来开启 Beta 功能
- 在传入的 tools 列表中，所有 function 均需设置 strict 属性为 true
- 服务端会对用户传入的 Function 的 JSON Schema 进行校验，如不符合规范，或遇到服务端不支持的 JSON Schema 类型，将返回错误信息


## demo
```py
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "strict": true,
        "description": "Get weather of a location, the user should supply a location first.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                }
            },
            "required": ["location"],
            "additionalProperties": false
        }
    }
}
```

## strict 模式支持的 JSON Schema 类型
- string
- number
- integer
- boolean
- array
- object
- enum
- anyOf


