# deepseek api
DeepSeek API 使用与 OpenAI 兼容的 API 格式
- base_url : `https://api.deepseek.com`
- api_key : 从 DeepSeek [控制台](https://platform.deepseek.com/sign_in)获取

[api doc](https://api-docs.deepseek.com/zh-cn/)
- deepseek-chat 对应 DeepSeek-V3.2-Exp 的非思考模式，
- deepseek-reasoner 对应 DeepSeek-V3.2-Exp 的思考模式。

## temperature
- 0.0 代码生成/数学解题
- 1.0 数据抽取/分析 (默认值)
- 1.3 通用对话 / 翻译
- 1.5 创意类写作/诗歌创作


## token用量计算
token 是模型用来表示自然语言文本的基本单位，一般情况下模型中 token 和字数的换算比例大致如下：
- 1 个英文字符 ≈ 0.3 个 token。
- 1 个中文字符 ≈ 0.6 个 token。


## 限速
DeepSeek API 不限制用户并发量。

当我们的服务器承受高流量压力时，您的请求发出后，可能需要等待一段时间才能获取服务器的响应。在这段时间里，您的 HTTP 请求会保持连接，并持续收到如下格式的返回内容：
- 非流式请求：持续返回空行
- 流式请求：持续返回 SSE keep-alive 注释（: keep-alive）

> 这些内容不影响 OpenAI SDK 对响应的 JSON body 的解析。如果您在自己解析 HTTP 响应，请注意处理这些空行或注释。

## 错误码
[错误码解释](https://api-docs.deepseek.com/zh-cn/quick_start/error_codes)
- 400 Bad Request：请求参数错误，例如缺失必填参数、参数值格式错误等。
- 401 Unauthorized：认证失败，例如 API Key 错误、权限不足等。
- 402 Payment Required：余额不足，需要充值后才能继续使用。
- 422 请求体参数错误
- 429 Too Many Requests：请求频率超过配额，需要等待一段时间后重试。
- 500 Internal Server Error：服务器内部错误，例如模型运行时出错、数据库异常等。
- 503 服务器繁忙




