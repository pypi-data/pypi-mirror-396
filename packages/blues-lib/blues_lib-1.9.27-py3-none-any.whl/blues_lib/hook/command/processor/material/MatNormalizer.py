from blues_lib.hook.command.processor.material.MatProc import MatProc
from blues_lib.material.normalizer.Normalizer import Normalizer
from blues_lib.type.output.STDOut import STDOut

class MatNormalizer(MatProc):
  
  def _calculate(self,request:dict)->STDOut:
    handler = Normalizer(request)
    return handler.resolve()