from blues_lib.type.executor.Executor import Executor
from blues_lib.type.output.STDOut import STDOut
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.command.io.IOExcept import IOExcept
from blues_lib.flow.MockTI import MockTI

class Flow(Executor):
  
  def __init__(self,dag_def:dict,dag_biz:list[dict]): 
    super().__init__()
    self._executors:list[Executor] = []
    self._task_ids:list[str] = []
    self._dag_def:dict = dag_def
    self._dag_biz:list[dict] = dag_biz

    # validate input: only validate the outer struct of the input
    IOExcept.validate_dag(self._dag_def)
    
  @property
  def dag_id(self)->str:
    return self._dag_def.get('dag_id') or 'anonymous dag'

  @property
  def dag_def(self)->dict:
    return self._dag_def

  @property
  def dag_biz(self)->list[dict]:
    return self._dag_biz
  
  @property
  def last_task_result(self)->dict:
    return self.get_task_result(self.task_ids[-1])
  
  @property
  def last_task_stdout(self)->STDOut:
    result:dict = self.last_task_result
    code:int = result.get('code') or 200
    message:str = result.get('message') or 'last task output'
    data:any = result.get('data')
    detail:any = result.get('detail')
    return STDOut(code,message,data,detail)
    
  @property
  def size(self)->int:
    return len(self._executors)

  @property
  def task_ids(self)->list[str]:
    return self._task_ids
    
  def get_task_result(self,task_id:str)->dict:
    return MockTI.store.get(task_id) or {}
  
  def _create_executors(self)->None:
    task_defs:list[dict] = self._dag_def.get('tasks') or []
    index:int = 0
    for task_def in task_defs:
      self._add_task(task_def,self._dag_biz[index])
      index += 1
    
  def _add_task(self,task_def:dict,task_biz:dict):
    # avoid circular dependency
    from blues_lib.command.CommandFactory import CommandFactory

    ti = MockTI(task_def.get('task_id'))
    executor:NodeCommand|None = CommandFactory().create(task_def,task_biz,ti)
    if not executor:
      raise RuntimeError(f'Factory failed to create object of type {task_def.get("command")}')
    self._executors.append(executor)

  def execute(self)->STDOut:

    self._create_executors()
    for executor in self._executors:
      self._logger.info(f'Task {executor.task_id} started')
      self._task_ids.append(executor.task_id)
      executor.execute()

    return STDOut(200,f'flow success : {"->".join(self._task_ids)}')
        