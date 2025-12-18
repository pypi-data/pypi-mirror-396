from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.sinker.Sinker import Sinker as SinkerHandler

class Sinker(NodeCommand):
  
  NAME = CommandName.Material.SINKER

  def _invoke(self)->STDOut:
    rule:dict = self._summary.get('rule',{})
    entities:list[dict] = self._summary.get('entities',[])
    if not entities:
      raise ValueError(f'{self.NAME} : no input entities')
    
    request = {
      'rule':rule,
      'entities':entities, # must be a list
    } 
    # 不论是否合法都存入表，后续可以根据状态进行筛选
    handler = SinkerHandler(request)
    sql_output:STDOut = handler.handle()
    if sql_output.code != 200:
      return sql_output
    else:
      # 区分两种状态数据，非法数据单独输出
      available_entities,invalid_entities,invalid_messages = self._split_by_status(entities)
      
      # 合法数据作为标准数据
      if available_entities:
        return STDOut(200,f'Managed to sink {len(available_entities)} entities',available_entities)
      else:
        raise ValueError(f'{self.NAME} : all entities are invalid : {";".join(invalid_messages)}')
    
  def _split_by_status(self,entities:list[dict])->tuple[list[dict],list[dict]]:
    available_entities:list[dict] = []
    invalid_entities:list[dict] = []
    invalid_messages:list[str] = []
    for entity in entities:
      if entity['mat_stat'] == 'available':
        available_entities.append(entity)
      else:
        invalid_entities.append(entity)
        invalid_messages.append(f"{entity['mat_title']} - {entity['mat_remark']}")
        
    return available_entities,invalid_entities,invalid_messages
