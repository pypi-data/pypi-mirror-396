from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.normalizer.Normalizer import Normalizer as NormalizerHandler

class Normalizer(NodeCommand):

  NAME = CommandName.Material.NORMALIZER
  

  def _invoke(self)->STDOut:
    rule:dict = self._summary.get('rule',{})
    entities:list[dict] = self._summary.get('entities',[])
    if not entities:
      raise ValueError(f'{self.NAME} : no input entities')

    request = {
      'rule':rule,
      'entities':entities, # must be a list
    } 
    handler = NormalizerHandler(request)
    return handler.handle()