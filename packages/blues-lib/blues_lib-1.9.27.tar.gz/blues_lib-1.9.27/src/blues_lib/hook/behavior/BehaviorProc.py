from blues_lib.hook.HookProc import HookProc

class BehaviorProc(HookProc):
  
  def __init__(self,proc_def:dict,options:dict) -> None:
    super().__init__()

    self._proc_conf = proc_def
    # options's value will be rewrite
    self._options = options
