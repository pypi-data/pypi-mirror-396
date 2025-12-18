from blues_lib.command.LoopCommand import LoopCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.model.Model import Model
from blues_lib.command.crawler.Invoker import Invoker

class Loop(LoopCommand):

  NAME = CommandName.Crawler.LOOP

  def _run_once_cal(self,model:Model)->STDOut:
    return Invoker.invoke(model)
  