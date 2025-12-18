from blues_lib.hook.FuncHandler import FuncHandler

class BehaviorFuncHandler(FuncHandler):
  
  def execute(self):
    value = self._options.get('value')
    # lambda must return a value
    self._options['value'] = self._func(value) 
