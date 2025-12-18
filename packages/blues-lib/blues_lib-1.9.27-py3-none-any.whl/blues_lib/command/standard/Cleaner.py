from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.cleaner.file.FileCleanerChain import FileCleanerChain   
from blues_lib.cleaner.db.DBCleanerChain import DBCleanerChain

class Cleaner(NodeCommand):

  NAME = CommandName.Standard.CLEANER

  def _invoke(self)->STDOut:

    db_request:dict = {
      'rule':self._summary.get('db_rule'),
      'messages':[],
    }
    file_request:dict = {
      'rule':self._summary.get('file_rule'),
      'messages':[],
    }
    DBCleanerChain().handle(db_request)
    FileCleanerChain().handle(file_request)
    return self._get_output(db_request.get('messages'),file_request.get('messages'))
    
  def _get_output(self,db_messages:list[str],file_messages:list[str])->STDOut:
    return STDOut(200,'ok',db_messages+file_messages)
