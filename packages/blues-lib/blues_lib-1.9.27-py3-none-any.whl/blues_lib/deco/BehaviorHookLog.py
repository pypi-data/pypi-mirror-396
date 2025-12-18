from functools import wraps
from blues_lib.type.output.STDOut import STDOut
from blues_lib.deco.LogDeco import LogDeco

class BehaviorHookLog(LogDeco):

  def __init__(self,title:str='hook',max_chars:int=100):
    super().__init__(title,max_chars)

  def __call__(self,func):
    @wraps(func) 
    def wrapper(instance,*args,**kwargs):
      prefix:str = self._get_prefix(instance)
      stdout:STDOut = func(instance,*args,**kwargs)
      self._log(prefix,stdout)
      return stdout
    return wrapper

  def _get_prefix(self,instance)->str:
    module_name:str = instance.__class__.__module__  # 模块路径（如 my_project.tasks.loop）
    return f'{module_name} [{self._title}]'