from abc import ABC, abstractmethod

class Replacer(ABC):
  
  def __init__(self,template:dict, variables:dict|None=None):
    self._template = template
    self._variables = variables

  @abstractmethod
  def replace(self)->dict:
    pass
  