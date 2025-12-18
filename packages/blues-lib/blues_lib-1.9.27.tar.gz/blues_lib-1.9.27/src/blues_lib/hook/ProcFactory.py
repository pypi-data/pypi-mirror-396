class ProcFactory():
  
  _PROC_CLASSES = None

  @classmethod
  def create(cls,hook_def:dict,options:dict):
    class_name:str = hook_def.get('value') or ''
    proc_def:dict = hook_def.get('proc') or {}
    if not class_name:
      return None

    if proc_class := cls._PROC_CLASSES.get(class_name):
      return proc_class(proc_def,options)
    
    return None