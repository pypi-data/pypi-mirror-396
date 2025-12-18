import os
from blues_lib.model.BaseVarReplacer import BaseVarReplacer


class EnvVarReplacer(BaseVarReplacer):
  '''
  Environment variable replacer that replaces variable placeholders with environment variable values.
  Uses the same format as BaseVarReplacer but gets values from system environment variables.
  '''
  
  @classmethod
  def _get_raw_value(cls, var_name: str) -> str | None:
    '''
    Get value from system environment variables
    
    Args:
        var_name: Environment variable name
        
    Returns:
        Environment variable value or None if not found
    '''
    return os.environ.get(var_name)