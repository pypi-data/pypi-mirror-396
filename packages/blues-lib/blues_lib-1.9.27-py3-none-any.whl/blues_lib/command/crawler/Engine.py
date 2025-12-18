from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.model.Model import Model
from blues_lib.command.crawler.Invoker import Invoker

class Engine(NodeCommand):

  NAME = CommandName.Crawler.ENGINE

  def _invoke(self)->STDOut:
    model:Model = self._model
    return Invoker.invoke(model)