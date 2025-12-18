from blues_lib.type.output.STDOut import STDOut
from .Completion import Completion

class ChatStream(Completion):
  _STREAM = True
  
  def _get_content(self,response)->STDOut:
    pass
