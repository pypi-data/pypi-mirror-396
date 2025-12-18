from blues_lib.hook.command.processor.material.MatProc import MatProc
from blues_lib.material.filter.Filter import Filter
from blues_lib.type.output.STDOut import STDOut

class MatFilter(MatProc):
  
  def _calculate(self,request:dict)->STDOut:
    handler = Filter(request)
    return handler.resolve()