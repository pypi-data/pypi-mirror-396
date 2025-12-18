import re
from abc import ABC
from blues_lib.command.NodeCommand import NodeCommand

class SQLCommand(NodeCommand,ABC):
  
  NAME = None

  def _filter_entities(self,entities:list[dict],rule:dict)->list[dict]:

    extend_entity:dict = rule.get('entity') # the merged fields
    inc_fields:list[str] = rule.get('inc_fields',[])
    inc_pattern:str = rule.get('inc_pattern','')
    exc_fields:list[str] = rule.get('dec_fields',[])
    exc_pattern:str = rule.get('dec_pattern','')

    filtered_entities:list[dict] = []

    for entity in entities:
      filtered_entity:dict = entity.copy()
      # merge the entity
      if extend_entity:
        filtered_entity.update(extend_entity)
        
      # include and exclude the fields
      if inc_fields:
        filtered_entity = {k:v for k,v in filtered_entity.items() if k in inc_fields}

      if inc_pattern:
        filtered_entity = {k:v for k,v in filtered_entity.items() if re.match(inc_pattern,k)}  

      if exc_fields:
        filtered_entity = {k:v for k,v in filtered_entity.items() if k not in exc_fields}

      if exc_pattern:
        filtered_entity = {k:v for k,v in filtered_entity.items() if not re.match(exc_pattern,k)}

      filtered_entities.append(filtered_entity)

    return filtered_entities
    

