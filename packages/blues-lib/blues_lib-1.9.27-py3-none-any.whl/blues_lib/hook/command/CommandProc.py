from blues_lib.hook.HookProc import HookProc
from blues_lib.type.output.STDOut import STDOut

class CommandProc(HookProc):
  
  def __init__(self,proc_def:dict,options:dict) -> None:
    super().__init__()

    self._proc_conf:dict = proc_def
    self._ti:any = options.get('ti')
    self._stdout:STDOut = options.get('stdout')