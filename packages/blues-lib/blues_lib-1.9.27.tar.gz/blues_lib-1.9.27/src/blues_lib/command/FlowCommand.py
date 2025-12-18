from copy import deepcopy
from abc import ABC,abstractmethod
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.flow.Flow import Flow
from blues_lib.deco.CommandSTDOutLog import CommandSTDOutLog

class FlowCommand(NodeCommand,ABC):

  NAME = None

  def _invoke(self)->STDOut:
    return self._run()

  @abstractmethod
  def _run(self)->STDOut: 
    pass
    
  @CommandSTDOutLog('flow',max_chars=100)
  def _run_flow(self,dag_def:dict,dag_biz:list[dict])->STDOut:
    flow = self._get_flow(dag_def,dag_biz)
    stdout:STDOut = flow.execute() 
    if stdout.code == 200:
      return flow.last_task_stdout
    else:
      return stdout

  def _get_flow(self,dag_def:dict,dag_biz:list[dict])->Flow:
    # avoid circular import
    from blues_lib.flow.Flow import Flow
    flow = Flow(dag_def,dag_biz)
    if not flow:
      raise Exception(f'{self.NAME} Failed to create flow')
    return flow
