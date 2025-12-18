from blues_lib.hook.ProcFactory import ProcFactory
from .processor.HtmlFilter import HtmlFilter

class BehaviorFactory(ProcFactory):
  
  _PROC_CLASSES = {
    HtmlFilter.__name__: HtmlFilter,
  }