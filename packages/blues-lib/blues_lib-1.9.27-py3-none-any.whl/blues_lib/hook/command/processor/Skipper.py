from blues_lib.hook.command.CommandProc import CommandProc

class Skipper(CommandProc):
  
  def execute(self)->None:
    '''
    @description: skip the command
    @return: None
    '''
    should_skip:bool = self._proc_conf.get('should_skip',False)
    if should_skip:
      self._ti.xcom_push('should_skip',True)
