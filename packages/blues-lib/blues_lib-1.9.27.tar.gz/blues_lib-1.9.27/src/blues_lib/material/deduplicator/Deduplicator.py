from blues_lib.material.MatHandler import MatHandler
from blues_lib.dao.material.MatQuerier import MatQuerier
from blues_lib.type.output.STDOut import STDOut

class Deduplicator(MatHandler):

  def _calculate(self)->STDOut:
    duplicate_entities = []
    unique_entities = []

    querier = MatQuerier()
    key = self._rule.get('key','url')
    field = self._rule.get('field','mat_url')

    for entity in self._entities:
      if entity.get(key) and querier.exist(entity[key],field):
        duplicate_entities.append(entity)
      else:
        unique_entities.append(entity)

    message:str = f"unique {len(unique_entities)} ; deduplicate {len(duplicate_entities)}" 
    return STDOut(200,message,unique_entities,duplicate_entities)

