from blues_lib.behavior.event.Click import Click

class ClickQueue(Click):

  def _trigger(self)->int:
    loc_or_elems:list = self._config.get('target_CS_WEs',[]) 
    count = 0
    if not loc_or_elems:
      return count
    
    for loc_or_elem in loc_or_elems:
      self._config['target_CS_WE'] = loc_or_elem
      super()._trigger()
      count += 1

    return count