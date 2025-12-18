from copy import deepcopy
import logging
from blues_lib.type.output.STDOut import STDOut

class LogDeco():
  def __init__(self,title:str='',max_chars:int=-1):
    self._logger = logging.getLogger('airflow.task')
    self._title = title
    self._max_chars = max_chars

  def _log(self,prefix:str,stdout:STDOut):
      result:dict = self._get_result(stdout)
      self._logger.info(f'\n\n{prefix} :: {result}')

  def _get_result(self,stdout:STDOut)->dict:
    result:dict = deepcopy(stdout.to_dict())
    if self._max_chars>0:
      if result.get('data'):
        result['data'] = self._get_ellipsis_data(result['data'])
      if result.get('trash'):
        result['trash'] = self._get_ellipsis_data(result['trash'])
    return result
  
  def _get_ellipsis_data(self,data:any)->any:
    if not data:
      return data

    if isinstance(data,dict):
      self._set_ellipsis_dict(data)
    elif isinstance(data,list):
      for item in data:
        self._set_ellipsis_dict(item)
    elif isinstance(data,str):
      data = data[:self._max_chars]+' ...'
    return data
  
  def _set_ellipsis_dict(self,entity:dict)->None:
    if entity and isinstance(entity,dict):
      for key,value in entity.items():
        if len(str(value)) > self._max_chars:
          entity[key] = str(value)[:self._max_chars]+' ...'

