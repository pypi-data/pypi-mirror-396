# 查询余额
```
get https://api.deepseek.com/user/balance
```
查询账号余额

## response
```json
{
  "is_available": true,
  "balance_infos": [
    {
      "currency": "CNY",
      "total_balance": "110.00",
      "granted_balance": "10.00",
      "topped_up_balance": "100.00"
    }
  ]
}
```
