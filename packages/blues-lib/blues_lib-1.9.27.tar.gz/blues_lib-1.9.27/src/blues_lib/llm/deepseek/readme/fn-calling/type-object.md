## object
object 定义一个包含键值对的深层结构，其中 properties 定义了对象中每个键（属性）的 schema。每个 object 的所有属性均需设置为 required，且 object 中 additionalProperties 属性必须为 false。

```json
{
    "type": "object",
    "properties": {
        "name": { "type": "string" },
        "age": { "type": "integer" }
    },
    "required": ["name", "age"],
    "additionalProperties": false
}
```