import re
from typing import Any
from blues_lib.hocon.replacer.BaseReplacer import BaseReplacer

class VariableReplacer(BaseReplacer):
 
  IS_VARIABLES_REQUIRED = True

  '''
  replace the variable replace with the given values
  - single variable "{{var}}"
  - interpolate variable "name is {{name}}, age is {{age}}"
  '''  
  VAR_PATTERN = r"\{\{([a-zA-Z0-9_:\-.]+)\}\}"
  
  def _replace_node_var(self, value:str)->str:
    match = re.fullmatch(self.VAR_PATTERN, value)
    if match:
      # single variable replace, use the original value or None
      expr = match.group(1) 
      key, default = self._get_key_default(expr)
      return self._variables.get(key, default)
    else:
      return self._interpolate(value)
    
  def _interpolate(self, value:str)->str:
    # 处理包含多个占位符或其他文本的字符串
    def replace_match(match):
      expr = match.group(1)
      # 处理带默认值的情况: ${key:-default}
      key, default = self._get_key_default(expr)
      return str(self._variables.get(key, default))
     
    return re.sub(self.VAR_PATTERN, replace_match, value)
  
  def _get_key_default(self, expr:str,as_string:bool=False)->tuple:
    # 处理带默认值的情况: {{key:-default}}
    if ':-' in expr:
      key, default = expr.split(':-', 1)
      value = default if as_string else self._get_raw_value(default)
      return key, value
    return expr, None

  def _get_raw_value(self, value_str: str) -> Any|None:
    """
    将字符串转换为原始类型
    now ,don't support list and dict
    """
    # 处理布尔值
    if value_str.lower() == 'true':
      return True
    if value_str.lower() == 'false':
      return False
    
    # 处理None
    if value_str.lower() == 'none':
      return None
    
    # 处理数字
    try:
      num = int(value_str)
      return num
    except ValueError:
      try:
        num = float(value_str)
        return num
      except ValueError:
        pass
    # 默认返回字符串
    return value_str
