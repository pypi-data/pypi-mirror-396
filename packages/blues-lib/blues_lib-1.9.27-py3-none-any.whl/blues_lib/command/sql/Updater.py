from blues_lib.namespace.CommandName import CommandName
from blues_lib.dao.sql.TableMutator import TableMutator
from blues_lib.type.output.STDOut import STDOut
from blues_lib.command.SQLCommand import SQLCommand

class Updater(SQLCommand):

  NAME = CommandName.SQL.UPDATER

  def _invoke(self)->STDOut:
    table:str = self._summary.get('table')
    entities:list[dict] = self._summary.get('entities')
    mutator = TableMutator(table)
    
    results:list[dict] = []
    is_failed:bool = False
    for entity in entities:
      result:STDOut = self._invoke_one(mutator,entity)
      results.append(result.to_dict())
      if result.code != 200:
        is_failed = True
    
    return STDOut(200,'ok',results) if not is_failed else STDOut(500,'failed',results)

  def _invoke_one(self,mutator:TableMutator,entity:dict)->STDOut:
    conditions = self._get_conditions(entity)
    filter_rule = self._get_filter_rule()
    filtered_entities = self._filter_entities([entity],filter_rule)
    return mutator.update(filtered_entities[0],conditions)
  
  def _get_conditions(self,entity:dict)->list[dict]|None:
    if conditions := self._summary.get('conditions'):
      return conditions

    if condition_field := self._summary.get('condition_field'):
      condition_value = entity.get(condition_field)
      return [{
        'field':condition_field,
        'comparator':'=',
        'value':condition_value
      }]
    return None
  
  def _get_filter_rule(self)->dict:
    filter_rule:dict = self._summary.copy()
    if condition_field:=self._summary.get('condition_field'):
      # exclude the condition field
      filter_rule['exc_fields'] = [condition_field]
    return filter_rule
