from blues_lib.type.output.STDOut import STDOut
from blues_lib.model.Model import Model
from blues_lib.behavior.factory.BhvFactory import BhvFactory

class BhvExecutor():

  def __init__(self,model:Model,browser=None):
    self._model = model
    self._browser = browser
    
  def execute(self)->STDOut: 
    try:
      value = self._execute(self._model.config,self._model.meta)
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),None)

  def _execute(self,config:any,meta:any)->any:
    
    if isinstance(config,dict):
      kind = config.get('_kind')
      if kind:
        # skip the optional behavior
        if config.get('_skip'):
          return None
        return self._execute_bhv(meta,kind)

      return self._execute_map(config,meta)

    if isinstance(config,list):
      return self._execute_list(config,meta)

    return config
    
  def _execute_bhv(self,meta:dict,kind:str)->any:
    # must pass the meta and bizdata
    model = Model(meta,self._model.bizdata)
    bhv = BhvFactory(model,self._browser).create(kind)
    if not bhv:
      # lazy to load the class
      from blues_lib.behavior.factory.BhvUnitFactory import BhvUnitFactory
      bhv = BhvUnitFactory(model,self._browser).create(kind)
      if not bhv:
        return None

    stdout = bhv.execute()
    if stdout.code != 200:
      raise Exception(stdout.message)
    return stdout.data
  
  def _execute_list(self,configs:list[dict],meta:list[dict])->list[any]:
    values:list[any] = []
    for idx,config in enumerate(configs):
      value = self._execute(config,meta[idx])
      values.append(value)
    return values

  def _execute_map(self,configs:dict[str,dict],meta:dict[str,dict])->dict[str,any]:
    values:dict[str,any] = {}
    for key,config in configs.items():
      value = self._execute(config,meta[key])
      values[key] = value
    return values
