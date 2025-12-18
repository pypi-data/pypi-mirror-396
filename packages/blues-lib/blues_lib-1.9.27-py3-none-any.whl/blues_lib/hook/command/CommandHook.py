from typing import Type
from blues_lib.hook.Hook import Hook
from .CommandProcFactory import CommandProcFactory
from .CommandFuncHandler import CommandFuncHandler
from blues_lib.hook.HookExcept import HookExcept
from blues_lib.type.output.STDOut import STDOut

class CommandHook(Hook):
  
  def _get_proc_factory(self)->Type[CommandProcFactory]:
    return CommandProcFactory
  
  def _get_func_handler(self)->Type[CommandFuncHandler]:
    return CommandFuncHandler
  
  def execute(self)->None:
    if not self._hook_defs:
      return

    HookExcept.validate(self._hook_defs)

    ti = self._options.get('ti')
    for hook_def in self._hook_defs:
      # if one hook block or skip, then break
      if ti.xcom_pull(key='should_skip') or ti.xcom_pull(key='should_block'):
        break
      self._run(hook_def)

  @classmethod
  def block(cls,ti:any)->None:
    if ti.xcom_pull(key='should_block'):
      stdout:STDOut = STDOut(500,f'The task {ti.task_id} is blocked',False)
      for key,value in stdout.to_dict().items():
        ti.xcom_push(key,value)
      raise Exception(f'The task {ti.task_id} is blocked')
    
  @classmethod
  def skip(cls,ti:any)->STDOut|None:
    if ti.xcom_pull(key='should_skip'):
      stdout:STDOut = STDOut(200,f'The task {ti.task_id} is skipped',True)
      for key,value in stdout.to_dict().items():
        ti.xcom_push(key,value)
      return stdout
    return None
    
