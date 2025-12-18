from abc import abstractmethod
from blues_lib.type.output.STDOut import STDOut
from blues_lib.behavior.Behavior import Behavior
from blues_lib.deco.BehaviorSTDOutLog import BehaviorSTDOutLog

class Trigger(Behavior):

  @BehaviorSTDOutLog()
  def _invoke(self)->STDOut:
    value = None
    try:
      value = self._trigger()
      value = self._after_invoked(value)
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  @abstractmethod
  def _trigger(self)->any:
    pass
  