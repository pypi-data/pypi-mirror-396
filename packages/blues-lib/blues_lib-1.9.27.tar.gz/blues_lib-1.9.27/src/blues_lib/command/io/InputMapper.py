from blues_lib.util.NestedDataMapping import NestedDataMapping
from blues_lib.command.io.IOExcept import IOExcept

class InputMapper:

  def __init__(self,task_def:dict,bizdata:dict,ti:any) -> None:
    self._task_def = task_def
    self._bizdata = bizdata
    self._ti = ti

  def handle(self):
    # Base on input mapping, add upsteam's output to the bizdata by xcom

    IOExcept.validate_task_input(self._task_def)
    
    input_defs:list[dict] = self._task_def.get('input')
    if not input_defs:
      return

    for input_def in input_defs:
      self._map(input_def)
      
  def _map(self,input_def:dict):
    source:str = input_def.get('source')
    target:str = input_def.get('target')
    method:str = input_def.get('method') or 'assign' # cover the node
    before_map:str = input_def.get('before_map')
    
    if not source or not target:
      return
    source_data,source_attr_chain = self._get_source_data(source)
    if not source_data:
      return
    
    target_data,target_attr_chain = self._get_target_data(target)
    if not target_data:
      return
    has_mapped = NestedDataMapping.map(source_data,source_attr_chain,target_data,target_attr_chain,method,before_map) 
    if not has_mapped:
      raise Exception(f'Failed to map source {source} to target {target}')
      
  def _get_target_data(self,target:str)->tuple[any,str]:
    target_slices:list[str] = target.split('/')
    if len(target_slices) < 1:
      return None,''
    
    target_root:str = target_slices[0]
    attr_chain:str = target_slices[1] if len(target_slices) > 1 else ''
    
    if target_root !='bizdata':
      return None,attr_chain

    bizdata = self._bizdata
    return bizdata,attr_chain
    
  def _get_source_data(self,source:str)->tuple[any,str]:
    source_slices:list[str] = source.split('/')
    if len(source_slices) < 2:
      return None,''
    
    task_id:str = source_slices[0]
    key:str = source_slices[1]
    attr_chain:str = source_slices[2] if len(source_slices) > 2 else ''
    source_root_data:any = self._ti.xcom_pull(task_ids=task_id,key=key)
    if not source_root_data:
      return None,attr_chain 
    
    return source_root_data,attr_chain
