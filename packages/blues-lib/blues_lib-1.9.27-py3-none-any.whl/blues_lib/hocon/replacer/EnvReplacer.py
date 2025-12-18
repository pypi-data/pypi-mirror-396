import re
import os
from blues_lib.hocon.replacer.BaseReplacer import BaseReplacer

class EnvReplacer(BaseReplacer):

  '''
  replace by the environment variable
  "${ENV_VAR}" 
  '''
  VAR_PATTERN = r"^\$\{([a-zA-Z0-9_]+)\}$"

  def _replace_node_var(self, value:str)->str:
    """替换单个字符串中的环境变量占位符（要求完全匹配）"""
    # 检查是否为完整的环境变量
    match = re.match(self.VAR_PATTERN, value)
    if not match:
      return value

    key:str = match.group(1) 
    return os.environ.get(key)
