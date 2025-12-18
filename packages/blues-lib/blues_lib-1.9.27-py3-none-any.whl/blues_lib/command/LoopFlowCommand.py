from copy import deepcopy
from blues_lib.command.FlowCommand import FlowCommand
from blues_lib.type.output.STDOut import STDOut

class LoopFlowCommand(FlowCommand):

  NAME = None

  def _run(self)->STDOut:

    loop:dict = self._task_def.get('loop') or {}
    entities:list[dict] = loop.get('entities') or []
    count:int = int(loop.get('count') or -1)
    
    if not entities:
      raise Exception(f'{self.NAME} must have loop entities')

    # one by one
    items:list[dict] = []
    for entity in entities:
      # must pass a list
      if not entity:
        continue

      stdout:STDOut = self._run_one([entity])
      sub_items:list[dict] = stdout.data or []
      items.extend(sub_items)
      if count > 0 and len(items) >= count:
        break
    items = items[:count] if count > 0 else items
    return STDOut(200,'flow loop success',items)

  def _run_one(self,start_data:list[dict])->STDOut:
    dag_def:dict = self._get_def_with_start()
    dag_biz:list[dict] = self._get_biz_with_start(start_data)
    return self._run_flow(dag_def,dag_biz)
  
  def _get_biz_with_start(self,start_data:list[dict])->list[dict]:
    start_biz = {"data":start_data}
    dag_biz:list[dict] = self._bizdata.get('tasks')
    return [start_biz]+dag_biz

  def _get_def_with_start(self)->dict:
    dag_def:dict = deepcopy(self._dag_def)
    start_def:dict = self._get_start_task()
    tasks:list[dict] = dag_def.get('tasks') or []

    dag_def['tasks'] = [start_def] + tasks
    return dag_def
    
  def _get_start_task(self)->dict:
    return {
      "task_id":"start",
      "command":"command.standard.dummy",
      "meta":{
        "summary":{
          "code":200,
          "message":"dummy start",
          "data":"{{data}}",
          "detail":None
        }
      },
    }
