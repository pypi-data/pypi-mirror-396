from blues_lib.hook.command.processor.material.MatProc import MatProc
from blues_lib.material.deduplicator.Deduplicator import Deduplicator
from blues_lib.type.output.STDOut import STDOut

class MatDeduplicator(MatProc):
  
  def _calculate(self,request:dict)->STDOut:
    handler = Deduplicator(request)
    return handler.resolve()
