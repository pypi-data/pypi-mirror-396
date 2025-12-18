from abc import abstractmethod
from typing import Any
from blues_lib.hocon.replacer.Replacer import Replacer

class BaseReplacer(Replacer):
  ### macro statement replacer 

  IS_VARIABLES_REQUIRED = False
  
  def replace(self)->dict:
    """递归替换所有占位符"""
    if not self._template:
      return self._template
    
    if self.IS_VARIABLES_REQUIRED and not self._variables:
      return self._template

    return self._replace_node(self._template)
  
  def _replace_node(self, node:Any)->Any:
    """递归遍历并替换占位符"""
    if isinstance(node, str):
      return self._replace_node_var(node)
    elif isinstance(node, dict):
      # 创建新字典，不修改原对象
      return {key: self._replace_node(value) for key, value in node.items()}
    elif isinstance(node, list):
      # 处理列表
      return [self._replace_node(item) for item in node]
    else:
      # 其他类型直接返回
      return node
  
  @classmethod
  @abstractmethod
  def _replace_node_var(cls, value:str)->str:
    """替换单个字符串中的占位符（要求完全匹配）"""
    pass