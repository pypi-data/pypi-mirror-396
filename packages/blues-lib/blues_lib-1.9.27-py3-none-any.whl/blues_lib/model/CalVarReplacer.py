from blues_lib.util.BluesDateTime import BluesDateTime
from blues_lib.model.BaseVarReplacer import BaseVarReplacer

class CalVarReplacer(BaseVarReplacer):
  '''
  Calculated variable replacer that replaces variable placeholders with values from get_vars method.
  Uses the same format as BaseVarReplacer but gets values from a dictionary returned by get_vars.
  '''
  @classmethod
  def get_vars(cls) -> dict:
    return {
      "timestamp": BluesDateTime.get_timestamp(),
      "now": BluesDateTime.get_now(),
    }

  @classmethod
  def _get_raw_value(cls, var_name: str) -> str | None:
    '''
    Get value from calculated variables dictionary
    
    Args:
        var_name: Variable name to look up
        
    Returns:
        Variable value or None if not found
    '''
    # Create an instance to call the non-class method get_vars()
    instance = cls()
    vars_dict = instance.get_vars()
    return vars_dict.get(var_name)