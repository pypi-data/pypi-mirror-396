from blues_lib.hook.command.CommandProc import CommandProc
from blues_lib.type.output.STDOut import STDOut

class Dummy(CommandProc):
  
  def execute(self)->None:
    '''
    @description: block the flow
    @return: None
    '''
    message:str = self._proc_conf.get('message','dummy')
    stdout:STDOut = self._stdout

    if message:
      print(f'[{self.__class__.__name__}] {message}')
    print(f'[{self.__class__.__name__}] {stdout}')
