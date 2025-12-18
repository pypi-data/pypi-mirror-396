from blues_lib.hocon.replacer.HoconReplacer import HoconReplacer

class Model:

  def __init__(self, meta: dict, bizdata: dict|None = None) -> None:
    self.meta = self._get_meta(meta)
    self.bizdata = self._get_bizdata(bizdata)
    self.config = self._get_config()
    
  def _get_meta(self,meta:dict)->dict:
    '''
    complete the macro calculation in the meta (include and function)
    - doesn't pass the vars, wouldn't replace the vars
    '''
    return HoconReplacer(meta).replace()
    
  def _get_bizdata(self,bizdata:dict|None)->dict:
    '''
    complete the macro calculation in the bizdata (include and function)
    - doesn't pass the vars, wouldn't replace the vars
    '''
    return HoconReplacer(bizdata).replace()
    
  def refresh(self):
    '''
    recalculate the config, when the meta or bizdata is updated
    '''
    self.config = self._get_config()

  def _get_config(self) -> dict:
    """
    replace the placeholder in the meta with the bizdata ("{}")
    Args:
      meta {dict}: the meta template
      bizdata {dict}: the meta variables
    Returns:
      {dict}: the config
    """
    return HoconReplacer(self.meta,self.bizdata).replace()



