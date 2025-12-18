from blues_lib.util.html.HtmlExtractor import HtmlExtractor 
from blues_lib.hook.behavior.BehaviorProc import BehaviorProc
from blues_lib.deco.BehaviorHookLog import BehaviorHookLog
from blues_lib.type.output.STDOut import STDOut

class HtmlFilter(BehaviorProc):

  @BehaviorHookLog()
  def execute(self)->STDOut:
    if value:=self._options.get('value'):
      includes:list[str] = self._proc_conf.get('includes',[]) 
      excludes:list[str] = self._proc_conf.get('excludes',[])
      result:dict = HtmlExtractor().extract(value, includes,excludes)
      self._options['value'] = result['html']
      
      return STDOut(200,'ok',result['html'],value)
    return STDOut(200,'value is None',value,value)

