from typing import Type
from abc import abstractmethod
from blues_lib.type.executor.Executor import Executor
from .ProcFactory import ProcFactory
from .FuncHandler import FuncHandler

class Hook(Executor):

  def __init__(self,hook_defs:list[dict[str,any]],options:dict) -> None:
    '''
    @param {list[dict]} hook_defs : the task hook definition
    @param {dict} options: 可选参数，支持：
        - 其他未来可能扩展的参数（如 context、config 等）
    '''
    super().__init__()
    self._hook_defs = hook_defs
    self._options = options # 可变的扩展参数
    
  def _run(self,hook_def:dict)->any:
    kind:str = hook_def.get('kind') or ''
    value:str = hook_def.get('value') or ''
    if not kind or not value:
      return

    if kind == 'class':
      self._handle_by_class(hook_def)
    elif kind == 'func':
      self._handle_by_func(hook_def)
    else:
      raise ValueError(f'Unknown hook kind: {kind}')
    
  def _handle_by_class(self,hook_def:dict)->any:
    factory = self._get_proc_factory()
    if processor := factory.create(hook_def,self._options):
      processor.execute()
    else:
      raise Exception(f'processor {hook_def.get("value")} not found')
    
  def _handle_by_func(self,hook_def:dict)->any:
    handler = self._get_func_handler()
    handler(hook_def,self._options).execute()
  
  @abstractmethod
  def _get_proc_factory(self)->Type[ProcFactory]:
    pass
  
  @abstractmethod
  def _get_func_handler(self)->Type[FuncHandler]:
    pass