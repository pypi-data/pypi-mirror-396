from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut

class Filter(MatHandler):

  def _calculate(self)->STDOut:
    valid_entities = []
    invalid_entities = []

    for item in self._entities:
      output:STDOut = self._insert(item)
      if output.code !=200:
        item['mat_stat'] = 'invalid'
        item['mat_remark'] = output.message
        invalid_entities.append(item)
      else:
        valid_entities.append(item)

    message:str = f"valid {len(valid_entities)} ; invalid {len(invalid_entities)}" 
    return STDOut(200,message,valid_entities,invalid_entities)

