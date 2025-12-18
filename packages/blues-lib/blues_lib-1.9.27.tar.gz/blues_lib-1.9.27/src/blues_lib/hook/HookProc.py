from abc import abstractmethod
from blues_lib.type.executor.Executor import Executor

class HookProc(Executor):
  
  @abstractmethod
  def execute(self)->None:
    pass