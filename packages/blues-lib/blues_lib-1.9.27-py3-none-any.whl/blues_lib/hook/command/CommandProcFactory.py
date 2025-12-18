from blues_lib.hook.ProcFactory import ProcFactory
from .processor.Dummy import Dummy
from .processor.Skipper import Skipper
from .processor.Blocker import Blocker
from .processor.material.MatDeduplicator import MatDeduplicator
from .processor.material.MatValidator import MatValidator
from .processor.material.MatNormalizer import MatNormalizer
from .processor.material.MatLocalizer import MatLocalizer
from .processor.material.MatFilter import MatFilter

class CommandProcFactory(ProcFactory):
  
  _PROC_CLASSES = {
    Dummy.__name__: Dummy,
      
    Skipper.__name__: Skipper,
    Blocker.__name__: Blocker,

    MatDeduplicator.__name__: MatDeduplicator,
    MatValidator.__name__: MatValidator,
    MatNormalizer.__name__: MatNormalizer,
    MatLocalizer.__name__: MatLocalizer,
    MatFilter.__name__: MatFilter,
  }