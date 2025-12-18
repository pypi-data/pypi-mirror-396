from blues_lib.type.output.STDOut import STDOut
from blues_lib.behavior.Behavior import Behavior
from blues_lib.deco.BehaviorSTDOutLog import BehaviorSTDOutLog

class Bean(Behavior):

  @BehaviorSTDOutLog()
  def _invoke(self)->STDOut:
    value = None
    try:
      if self._action()=='setter':
        value = self._set()
      else:
        value = self._get()
        value = self._after_invoked(value)
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  def _get(self)->any:
    # optional
    pass

  def _set(self)->any:
    # optional
    pass

  def _action(self)->str:
    action = 'getter'
    if 'value' in self._config:
      action = 'setter'
    return action
  
  def _get_value_entity(self)->dict|None:

    key:str|None = self._config.get('key')
    value:any = self._config.get('value')

    if key:
      return {
        key:value
      }

    if isinstance(value,dict):
      return value
    
    return None
      