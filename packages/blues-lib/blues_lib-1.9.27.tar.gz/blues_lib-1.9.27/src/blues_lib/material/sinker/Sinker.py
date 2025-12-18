import re
from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.dao.material.MatMutator import MatMutator 

class Sinker(MatHandler):

  def resolve(self)->STDOut:
    self._setup()

    if not self._rule:
      return STDOut(200,'skip this sinker')

    if not self._entities:
      raise Exception(f'{self.__class__.__name__} entities is empty')
    
    self._method = self._rule.get('method','insert')
    conditions:list[dict] = self._rule.get('conditions',[])
    
    sink_entities:list[dict] = self._get_sink_entities()
    
    # insert to the db
    if self._method == 'insert':
      return MatMutator().insert(sink_entities)
    elif self._method == 'update':
      # only update the first entity
      return MatMutator().update(sink_entities[0],conditions)
    elif self._method == 'delete':
      return MatMutator().delete(conditions)
    else:
      return STDOut(500,f'{self.__class__.__name__} no support method: {self._method}')
    
  def _get_sink_entities(self)->list[dict]:
    
    extend_entity:dict = self._rule.get('entity') # the merged fields
    inc_fields:list[str] = self._rule.get('inc_fields',[])
    inc_pattern:str = self._rule.get('inc_pattern','')
    exc_fields:list[str] = self._rule.get('dec_fields',[])
    exc_pattern:str = self._rule.get('dec_pattern','')

    sink_entities:list[dict] = []
    
    for entity in self._entities:
      sink_entity:dict = entity.copy()
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
    

