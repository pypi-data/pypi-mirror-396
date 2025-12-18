from blues_lib.hocon.replacer.Replacer import Replacer  
from blues_lib.hocon.replacer.IncludeReplacer import IncludeReplacer
from blues_lib.hocon.replacer.FunctionReplacer import FunctionReplacer
from blues_lib.hocon.replacer.EnvReplacer import EnvReplacer
from blues_lib.hocon.replacer.VariableReplacer import VariableReplacer

class HoconReplacer(Replacer):
  
  def replace(self)->dict:
    template:dict = self._template
    variables:dict = self._variables

    # chains
    template:dict = IncludeReplacer(template).replace()
    template:dict = FunctionReplacer(template).replace()
    template:dict = EnvReplacer(template).replace()
    template:dict = VariableReplacer(template,variables).replace()
    return template
  
  def env(self):
    return EnvReplacer(self._template).replace()
  
  def include(self):
    return IncludeReplacer(self._template).replace()
  
  def calculate(self):
    return FunctionReplacer(self._template).replace()
  
  def format(self):
    return VariableReplacer(self._template,self._variables).replace()
  