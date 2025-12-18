from blues_lib.hook.command.processor.material.MatProc import MatProc
from blues_lib.material.validator.Validator import Validator
from blues_lib.type.output.STDOut import STDOut

class MatValidator(MatProc):
  
  def _calculate(self,request:dict)->STDOut:
    handler = Validator(request)
    return handler.resolve()
