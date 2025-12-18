## string
支持的参数：
- pattern：使用正则表达式来约束字符串的格式
- format：使用预定义的常见格式进行校验，目前支持：
  - email：电子邮件地址
  - hostname：主机名
  - ipv4：IPv4 地址
  - ipv6：IPv6 地址
  - uuid：uuid
不支持的参数
- minLength
- maxLength

```json
{
    "type": "object",
    "properties": {
        "user_email": {
            "type": "string",
            "description": "The user's email address",
            "format": "email" 
        },
        "zip_code": {
            "type": "string",
            "description": "Six digit postal code",
            "pattern": "^\\d{6}$"
        }
    }
}
```