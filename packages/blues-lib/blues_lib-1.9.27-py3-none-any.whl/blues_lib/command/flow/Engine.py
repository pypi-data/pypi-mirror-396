from blues_lib.command.FlowCommand import FlowCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut

class Engine(FlowCommand):

  NAME = CommandName.Flow.ENGINE

  def _run(self)->STDOut: 
    dag_biz:list[dict] = self._bizdata.get('tasks')
    return self._run_flow(self._dag_def,dag_biz)
  