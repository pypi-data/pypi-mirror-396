from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.SQLCommand import SQLCommand
from blues_lib.dao.sql.TableMutator import TableMutator
from blues_lib.type.output.STDOut import STDOut

class Deleter(SQLCommand):

  NAME = CommandName.SQL.DELETER

  def _invoke(self)->STDOut:
    table = self._summary.get('table')
    conditions = self._summary.get('conditions')
    mutator = TableMutator(table)
    return mutator.delete(conditions)
