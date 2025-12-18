import logging
from abc import ABC,abstractmethod
from blues_lib.type.output.STDOut import STDOut

class Executor(ABC):

  def __init__(self):
    self._logger = logging.getLogger('airflow.task')

  @abstractmethod  
  def execute(self)->STDOut:
    pass

