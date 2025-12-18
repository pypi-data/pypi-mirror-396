from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.model.Model import Model
from blues_lib.command.llm.Invoker import Invoker

class Engine(NodeCommand):

  NAME = CommandName.LLM.ENGINE

  def _invoke(self)->STDOut:
    model:Model = self._model
    return Invoker.invoke(model)
