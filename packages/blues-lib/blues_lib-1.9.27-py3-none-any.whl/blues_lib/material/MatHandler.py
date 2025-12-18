import re
from copy import deepcopy
from blues_lib.type.chain.AllMatchHandler import AllMatchHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.dao.material.MatMutator import MatMutator 

class MatHandler(AllMatchHandler):
  
  def resolve(self)->STDOut:
    self._entities:list[dict] = self._request.get('entities')
    self._rule:dict = self._request.get('rule') or {}
    
    if not self._entities:
      message:str = "entities 0" 
      return STDOut(200,message,None,None)
    
    return self._calculate()
    
  def _calculate(self)->STDOut:
    raise NotImplementedError

  def _insert_trash(self,rows:list[dict])->STDOut:
    stdout:STDOut = self._insert(rows)
    self._logger.info(f"\n\n{self.__class__.__name__} insert trash output : {stdout}")
    return stdout

  def _insert(self,data:list[dict]|dict)->STDOut:
    if not data:
      message:str = "data is empty" 
      return STDOut(200,message,None,None)

    rows = data if isinstance(data,list) else [data]
    rows:list[dict] = self._get_rule_entities(rows)
    return MatMutator().insert(rows)

  def _get_rule_entities(self,entities:list[dict])->list[dict]:
    extend_entity:dict = self._rule.get('entity') # the merged fields
    inc_fields:list[str] = self._rule.get('inc_fields',[])
    inc_pattern:str = self._rule.get('inc_pattern','')
    exc_fields:list[str] = self._rule.get('dec_fields',[])
    exc_pattern:str = self._rule.get('dec_pattern','')

    sink_entities:list[dict] = []
    
    for entity in entities:
      # must deepcopy to avoid modify the original item (list to string)
      sink_entity:dict = deepcopy(entity)
      # merge the entity
      if extend_entity:
        sink_entity.update(extend_entity)
        
      # include and exclude the fields
      if inc_fields:
        sink_entity = {k:v for k,v in sink_entity.items() if k in inc_fields}

      if inc_pattern:
        sink_entity = {k:v for k,v in sink_entity.items() if re.match(inc_pattern,k)}

      if exc_fields:
        sink_entity = {k:v for k,v in sink_entity.items() if k not in exc_fields}

      if exc_pattern:
        sink_entity = {k:v for k,v in sink_entity.items() if not re.match(exc_pattern,k)}

      sink_entities.append(sink_entity)
    return sink_entities
    

