from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.SQLCommand import SQLCommand
from blues_lib.dao.sql.TableQuerier import TableQuerier
from blues_lib.type.output.STDOut import STDOut

class Querier(SQLCommand):

  NAME = CommandName.SQL.QUERIER

  def _invoke(self)->STDOut:
    table = self._summary.get('table')
    conditions = self._summary.get('conditions')
    fields = self._summary.get('fields') or '*'
    pagination = self._summary.get('pagination') or {
      'no':1,
      'size':1
    }
    orders = self._summary.get('orders')
    querier = TableQuerier(table)
    return querier.get(fields,conditions,orders,pagination)



     