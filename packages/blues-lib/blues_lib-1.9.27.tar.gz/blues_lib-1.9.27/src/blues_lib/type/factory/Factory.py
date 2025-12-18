import logging
from abc import ABC

class Factory(ABC):
  
  def __init__(self):
    self._logger = logging.getLogger('airflow.task')

  def create(self, mode: str, **kwargs):
    method_name = f"create_{mode.lower()}"
    if not hasattr(self, method_name):
      return None
    method = getattr(self, method_name)
    return method(**kwargs)

  