# FIM
在 FIM (Fill In the Middle) 补全中，用户可以提供前缀和后缀（可选），模型来补全中间的内容。FIM 常用于内容续写、代码补全等场景。
- 模型的最大补全长度为 4K。
- 用户需要设置 base_url="https://api.deepseek.com/beta" 来开启 Beta 功能。

## 示例
给出了计算斐波那契数列函数的开头和结尾，来让模型补全中间的内容。
```py
from openai import OpenAI

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com/beta",
)

response = client.completions.create(
    model="deepseek-chat",
    prompt="def fib(a):",
    suffix="    return fib(a-1) + fib(a-2)",
    max_tokens=128
)
print(response.choices[0].text)
```

