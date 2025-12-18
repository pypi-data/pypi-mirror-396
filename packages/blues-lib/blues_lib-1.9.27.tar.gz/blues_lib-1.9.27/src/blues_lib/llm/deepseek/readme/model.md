# list models
```
get https://api.deepseek.com/models
```
列出可用的模型列表，并提供相关模型的基本信息。

## response
```json
{
  "object": "list",
  "data": [
    {
      "id": "deepseek-chat",
      "object": "model",
      "owned_by": "deepseek"
    },
    {
      "id": "deepseek-reasoner",
      "object": "model",
      "owned_by": "deepseek"
    }
  ]
}
```