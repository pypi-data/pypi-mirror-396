from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.privatizer.image.Downloader import Downloader
from blues_lib.material.privatizer.image.Formatter import Formatter

class Localizer(MatHandler):

  def _calculate(self)->STDOut:
    valid_entities = []
    invalid_entities = []

    for entity in self._entities:
      request = {
        'rule':self._rule,
        'entity':entity,
      }
      error:str = self._handle(request)
      if error:
        entity['mat_stat'] = 'invalid'
        entity['mat_remark'] = error
        invalid_entities.append(entity)
      else:
        valid_entities.append(entity)
        
    # insert invalid entities to db
    self._insert_trash(invalid_entities)

    message:str = f"valid {len(valid_entities)} ; invalid {len(invalid_entities)}" 
    return STDOut(200,message,valid_entities,invalid_entities)

  def _handle(self,request:dict)->str:
    try:
      downloader = Downloader(request)
      formatter = Formatter(request)
      downloader.set_next(formatter)
      downloader.handle()
      return ''
    except Exception as e:
      return str(e)
