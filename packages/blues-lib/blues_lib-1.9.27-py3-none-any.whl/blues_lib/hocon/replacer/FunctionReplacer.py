import re
from blues_lib.util.BluesDateTime import BluesDateTime
from blues_lib.hocon.replacer.BaseReplacer import BaseReplacer

class FunctionReplacer(BaseReplacer):

  '''
  Calculated variable replacer that replaces variable placeholders with values from get_vars method.
  Uses the same format as BaseVarReplacer but gets values from a dictionary returned by get_vars.
  "%{function timestamp}" 内置方法
  "%{lambda x: x.upper()}" 自定义函数 : 暂未实现
  '''
  FUNCTION_PATTERN = r"^%\{function\s+([a-zA-Z0-9_]+)\}$"
  FUNCS = {
    "timestamp": lambda: BluesDateTime.get_timestamp(),
    "now": lambda: BluesDateTime.get_now(),
  }

  def _replace_node_var(self, value:str)->str:
    """替换单个字符串中的function占位符（要求完全匹配）"""
    # 检查是否为完整的 function 变量
    match = re.match(self.FUNCTION_PATTERN, value)
    if not match:
      return value

    func_name = match.group(1)  
    if func_name in self.FUNCS:
      return self.FUNCS[func_name]()
    else:
      return value 
