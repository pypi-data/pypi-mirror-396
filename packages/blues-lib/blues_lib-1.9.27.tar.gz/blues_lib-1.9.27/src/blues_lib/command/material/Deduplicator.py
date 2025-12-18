from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.deduplicator.Deduplicator import Deduplicator as DeduplicatorHandler

class Deduplicator(NodeCommand):

  NAME = CommandName.Material.DEDUPLICATOR

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
    handler = DeduplicatorHandler(request)
    return handler.handle()
 