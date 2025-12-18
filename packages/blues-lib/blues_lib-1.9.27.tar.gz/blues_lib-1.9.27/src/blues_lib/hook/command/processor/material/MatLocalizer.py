from blues_lib.hook.command.processor.material.MatProc import MatProc
from blues_lib.material.privatizer.Localizer import Localizer
from blues_lib.type.output.STDOut import STDOut

class MatLocalizer(MatProc):

  def _calculate(self,request:dict)->STDOut:
    handler = Localizer(request)
    return handler.resolve()