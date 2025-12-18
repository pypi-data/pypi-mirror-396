from abc import ABC,abstractmethod
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.model.Model import Model
from blues_lib.type.output.STDOut import STDOut
from blues_lib.hook.command.CommandHook import CommandHook
from blues_lib.deco.CommandSTDOutLog import CommandSTDOutLog

class LoopCommand(NodeCommand,ABC):

  NAME = None

  def _setup(self)->bool: 
    super()._setup()
    self._loop:dict = self._task_def.get('loop') or {}
    self._entities:list[dict] = self._loop.get('entities') or []
    self._map:dict = self._loop.get('map') or {}
    self._count:int = int(self._loop.get('count') or -1)
    self._round:int = 0
  
  def _invoke(self)->STDOut:
    if self._entities:
      return self._run()
    else:
      return self._run_once(self._model)
  
  def _run(self)->STDOut:
    items:list[dict] = []
    for entity in self._entities:
      model = self._get_loop_model(entity)
      stdout:STDOut = self._run_once(model,entity)
      if not stdout.data:
        continue

      items.extend(stdout.data)
      if self._count > 0 and len(items) >= self._count:
        break
    items = items[:self._count] if self._count > 0 else items
    return STDOut(200,'loop success',items)

  @CommandSTDOutLog('loop',max_chars=100)
  def _run_once(self,model:Model,entity:dict|None=None)->STDOut:
    self._round += 1
    
    self._before_each_invoked()
    output:STDOut = self._run_once_cal(model)
    self._merge(output,entity)
    
    self._after_each_invoked(output)
    return output
  
  @abstractmethod
  def _run_once_cal(self,model:Model)->STDOut:
    pass

  def _get_loop_model(self,entity:dict)->Model:
    # don't update the original bizdata
    bizdata:dict = self._model.bizdata.copy() 
    meta:dict = self._model.meta.copy()

    if self._map:    
      for entity_key,bizdata_key in self._map.items():
        bizdata[bizdata_key] = entity.get(entity_key)
    else:
      # bizdata and entity has the same field names
      for key,value in entity.items():
        bizdata[key] = value
    
    return Model(meta,bizdata)
  
  def _get_loop_items(self,items:list[dict],entity:dict)->list[dict]:
    filter_entity = {k:v for k,v in entity.items() if k not in self._map.keys()}
    merged_items:list[dict] = []
    for item in items:
      # llm输出优先
      merged = {**filter_entity,**item}
      merged_items.append(merged)
    return merged_items
  
  def _merge(self,output:STDOut,entity:dict|None=None)->None:
    code:int = output.code
    data:any = output.data
    if code == 200 and data:
      items:list[dict] = data if isinstance(data,list) else [data]
      merged_items = self._get_loop_items(items,entity) if entity else items
      output.data = merged_items
    else:
      output.data = []

  def _before_each_invoked(self)->None:
    hook_defs:list[dict] = self._task_def.get('before_each_invoked')
    options:dict = {'ti':self._ti}
    CommandHook(hook_defs,options).execute()

  def _after_each_invoked(self,output:STDOut)->None:
    # update the items directly 
    hook_defs:list[dict] = self._task_def.get('after_each_invoked')
    options:dict = {'ti':self._ti,'stdout':output}
    CommandHook(hook_defs,options).execute()
