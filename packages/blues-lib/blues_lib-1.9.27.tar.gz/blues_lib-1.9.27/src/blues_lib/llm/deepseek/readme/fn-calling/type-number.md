## number/integer

支持的参数
- const：固定数字为常数
- default：数字的默认值
- minimum：最小值
- maximum：最大值
- exclusiveMinimum：不小于
- exclusiveMaximum：不大于
- multipleOf：数字输出为这个值的倍数

```json
{
    "type": "object",
    "properties": {
        "score": {
            "type": "integer",
            "description": "A number from 1-5, which represents your rating, the higher, the better",
            "minimum": 1,
            "maximum": 5
        }
    },
    "required": ["score"],
    "additionalProperties": false
}
```
