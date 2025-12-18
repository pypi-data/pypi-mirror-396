# Anthropic API
API 新增了对 Anthropic API 格式的支持。通过简单的配置，即可将 DeepSeek 的能力，接入到 Anthropic API 生态中。

## 将 DeepSeek 模型接入 Claude Code
安装 claude code 
```
npm install -g @anthropic-ai/claude-code
```

### 配置环境变量
设置API_TIMEOUT_MS是为了防止输出过长，触发 Claude Code 客户端超时，这里设置的超时时间为 10 分钟。
```
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=${DEEPSEEK_API_KEY}
export API_TIMEOUT_MS=600000
export ANTHROPIC_MODEL=deepseek-chat
export ANTHROPIC_SMALL_FAST_MODEL=deepseek-chat
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

### 执行
进入项目目录，执行 claude 命令，即可开始使用了。
```
cd my-project
claude
```

进入claude命令行界面后，即可开始使用 DeepSeek 模型了。
![](https://cdn.deepseek.com/api-docs/cc_example.png)

## 通过 Anthropic API 调用 DeepSeek 模型
安装SDK
```
pip install anthropic
```

### 配置环境变量
```
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_API_KEY=${YOUR_API_KEY}
```

### 调用API
当您给 DeepSeek 的 Anthropic API 传入不支持的模型名时，API 后端会自动将其映射到 deepseek-chat 模型。
```
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="deepseek-chat",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hi, how are you?"
                }
            ]
        }
    ]
)
print(message.content)
```


