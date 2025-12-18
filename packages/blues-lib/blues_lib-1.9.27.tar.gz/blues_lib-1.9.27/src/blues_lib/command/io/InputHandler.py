from blues_lib.command.io.InputMapper import InputMapper
from blues_lib.hocon.replacer.HoconReplacer import HoconReplacer
from blues_lib.command.io.IOExcept import IOExcept

class InputHandler:
  
  def __init__(self,task_def:dict,task_biz:dict,ti:any) -> None:
    self._task_def = task_def
    self._task_biz = task_biz
    self._ti = ti

  def handle(self)->tuple[dict,dict]:
    task_biz = self._get_biz(self._task_def,self._task_biz)
    task_def = self._get_def(self._task_def,task_biz)
    return task_def,task_biz

  def _get_biz(self,task_def:dict,task_biz:dict)->dict:
    # Step1: replace the input mapping placeholder with bizdata
    mapping_def:dict = {
      "input":task_def.get('input')
    }
    mapping_def = HoconReplacer(mapping_def,task_biz).format()

    # Step2: add upstream's output to the bizdata 
    InputMapper(mapping_def,task_biz,self._ti).handle()
    
    # Step3: replace the bizdata placeholder (include and function) with the actual value
    return HoconReplacer(task_biz).replace()

  def _get_def(self,task_def:dict,task_biz:dict)->dict:

    # Step1: replace the placeholder in the task_def
    definition:dict = HoconReplacer(task_def).replace()

    # Step2: replace the variable placeholder in the definition, exclude dag and meta
    if definition.get('dag'):
      definition = self._get_format_def(definition,task_biz,'dag')
    elif definition.get('meta'):
      definition = self._get_format_def(definition,task_biz,'meta')
    else:
      definition = self._get_format_def(definition,task_biz)

    # Step3: validate the task def
    IOExcept.validate_task(definition)
    return definition
  
  def _get_format_def(self,task_def:dict,task_biz:dict,key:str='')->dict:
    if key:
      value:dict = task_def.pop(key)
    definition:dict = HoconReplacer(task_def,task_biz).format()
    if key:
      definition[key] = value
    return definition
