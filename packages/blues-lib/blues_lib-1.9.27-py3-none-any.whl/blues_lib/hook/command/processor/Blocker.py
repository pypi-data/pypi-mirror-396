from blues_lib.hook.command.CommandProc import CommandProc
class Blocker(CommandProc):
  
  def execute(self)->None:
    '''
    @description: block the flow
    @return: None
    '''
    should_block:bool = self._proc_conf.get('should_block',False)
    if should_block:
      self._ti.xcom_push('should_block',True)
