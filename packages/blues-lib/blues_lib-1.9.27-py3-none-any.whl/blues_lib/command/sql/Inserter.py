from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.SQLCommand import SQLCommand
from blues_lib.dao.sql.TableMutator import TableMutator
from blues_lib.type.output.STDOut import STDOut

class Inserter(SQLCommand):

  NAME = CommandName.SQL.INSERTER

  def _invoke(self)->STDOut:
    table = self._summary.get('table')
    entities = self._summary.get('entities')

    filter_rule:dict = self._summary.copy()
    filtered_entities = self._filter_entities(entities,filter_rule)

    mutator = TableMutator(table)
    return mutator.insert(filtered_entities)
