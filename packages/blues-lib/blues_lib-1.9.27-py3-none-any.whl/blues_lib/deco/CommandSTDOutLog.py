from functools import wraps
from blues_lib.type.output.STDOut import STDOut
from blues_lib.deco.LogDeco import LogDeco

class CommandSTDOutLog(LogDeco):
  def __init__(self,title:str='node',max_chars:int=-1):
    super().__init__(title,max_chars)

  def __call__(self,func):
    @wraps(func) 
    def wrapper(instance,*args,**kwargs):
      # this is the decoed class instance
      stdout:STDOut = func(instance,*args,**kwargs)
      prefix:str = self._get_prefix(instance)
      self._log(prefix,stdout)
      return stdout

    return wrapper
  
  def _get_prefix(self,instance)->str:
    module_name:str = instance.__class__.__module__  # 模块路径（如 my_project.tasks.loop）
    task_id:str = instance._ti.task_id
    round:int = 0
    if self._title == 'loop' and hasattr(instance, "_round"):
      round = instance._round
    round_str:str = ''
    if round>0:
      round_str = f'round {round}'
    return f'{module_name} {task_id} [{self._title}] {round_str}'
