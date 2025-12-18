from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut

class Dummy(NodeCommand):
  
  NAME = CommandName.Standard.DUMMY

  def _invoke(self)->STDOut:
    code:int = self._summary.get('code') or 200
    message:str = self._summary.get('message') or 'dummy ok'
    data:any = self._summary.get('data')
    detail:any = self._summary.get('detail')

    # just return the input params
    return STDOut(code,message,data,detail)
