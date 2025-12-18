from blues_lib.hook.command.CommandProc import CommandProc
from blues_lib.deco.CommandHookLog import CommandHookLog
from blues_lib.type.output.STDOut import STDOut

class MatProc(CommandProc):
  
  @CommandHookLog()
  def execute(self)->None:
    rule:dict = self._proc_conf.get('rule',{})
    entities:list[dict] = self._stdout.data or []

    request = {
      'rule':rule,
      'entities':entities, # must be a list
    } 
    stdout:STDOut = self._calculate(request)

    self._stdout.message = stdout.message
    self._stdout.data = stdout.data
    self._stdout.trash = stdout.trash

  def _calculate(self,request:dict)->STDOut:
    raise NotImplementedError
