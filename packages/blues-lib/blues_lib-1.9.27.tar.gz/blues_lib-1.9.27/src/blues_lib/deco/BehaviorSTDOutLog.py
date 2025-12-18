from functools import wraps
from blues_lib.type.output.STDOut import STDOut
from blues_lib.deco.LogDeco import LogDeco

class BehaviorSTDOutLog(LogDeco):

  def __init__(self,title:str='behavior',max_chars:int=50):
    super().__init__(title,max_chars)

  def __call__(self,func):
    @wraps(func) 
    def wrapper(instance,*args,**kwargs):
      module_name:str = instance.__class__.__module__  # 模块路径（如 my_project.tasks.loop）
      self._log_config(module_name,instance)

      prefix:str = self._get_prefix(instance)
      stdout:STDOut = func(instance,*args,**kwargs)
      self._log(prefix,stdout)
      return stdout
    return wrapper
  
  def _get_prefix(self,instance)->str:
    module_name:str = instance.__class__.__module__  # 模块路径（如 my_project.tasks.loop）
    return f'{module_name} [{self._title}]'

  def _log_config(self,module_name:str,instance):
    ellipsis_config:dict = self._get_ellipsis_config(instance._config)
    self._logger.info(f"\n\n{module_name} config :: {ellipsis_config}")
    
  def _get_ellipsis_config(self,config:dict)->dict:
    ellipsis_config:dict = {}
    for key,value in config.items():
      if key == 'value' and self._max_chars>0 and len(str(value)) > self._max_chars:
        ellipsis_config[key] = str(value)[:self._max_chars]+' ...'
      else:
        ellipsis_config[key] = value
    return ellipsis_config