from abc import ABC, abstractmethod
class FuncHandler(ABC):
  def __init__(self,hook_def:dict[str,any],options:dict) -> None:
    '''
    @param {dict} hook_def : hook definition
    @param {dict} options: 可选参数，支持：
        - 其他未来可能扩展的参数（如 context、config 等）
    '''
    super().__init__()
    self._hook_def = hook_def
    self._options = options # 可变的扩展参数
    self._func = eval(self._hook_def.get('value') or 'lambda x:x')

  @abstractmethod
  def execute(self):
    pass
