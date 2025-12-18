import logging
from abc import ABC,abstractmethod

from blues_lib.type.output.STDOut import STDOut

class Handler(ABC):

  def __init__(self,request):
    self._next_handler = None
    self._request = request
    self._logger = logging.getLogger('airflow.task')
  
  def set_next(self,handler):
    self._next_handler = handler
    return handler

  @abstractmethod
  def handle(self)->STDOut:
    pass

  @abstractmethod
  def resolve(self)->STDOut:
    pass