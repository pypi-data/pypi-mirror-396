from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.validator.Validator import Validator as ValidatorHandler

class Validator(NodeCommand):
  NAME = CommandName.Material.VALIDATOR

  def _invoke(self)->STDOut:
    '''
    验证字段是否合法，长度要比llm要求更宽一些
    '''
    rule:dict = self._summary.get('rule',{})
    entities:list[dict] = self._summary.get('entities',[])
    if not entities:
      raise ValueError(f'{self.NAME} : no input entities')
    
    request = {
      'rule':rule,
      'entities':entities, # must be a list
    } 
    handler = ValidatorHandler(request)
    return handler.handle()