from blues_lib.hook.FuncHandler import FuncHandler
from blues_lib.type.output.STDOut import STDOut

class CommandFuncHandler(FuncHandler):
  
  def execute(self)->any:
    ti:any = self._options.get('ti')
    stdout:STDOut = self._options.get('stdout')
    self._func(ti,stdout)
