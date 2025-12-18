import re

class BaseVarReplacer:
  '''
  Base class for variable replacement that handles common replacement logic.
  Subclasses should implement the _get_raw_value method to provide variable values.
  
  The format supports:
  - Without default value: "${VAR}"
  - With default value: "${VAR:-default_value}"
  
  Variables can be substrings within a string.
  - Example: "The ${VAR} is ${VAR:-default_value}."
  
  For pure variable strings, the original data type is preserved if possible.
  If the variable doesn't exist, None is returned for pure strings.
  For substrings within a string, the replacement is always treated as a string.
  '''

  # Regular expression pattern to match variable placeholders
  _VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')
  
  @classmethod
  def replace(cls, data) -> dict | list | str | None:
    '''
    Perform variable replacement:
    - Recursively process dictionaries, lists, and strings
    - Replace variables in strings
    
    Args:
        data: Data to process, can be dict, list, string, or other basic types
        
    Returns:
        Processed data with variables replaced, maintaining original structure
    '''
    if isinstance(data, dict):
      return cls._replace_dict(data)
    elif isinstance(data, list):
      return cls._replace_list(data)
    elif isinstance(data, str):
      return cls._replace_string(data)
    else:
      # Return other basic types as-is
      return data
  
  @classmethod
  def _replace_dict(cls, data: dict) -> dict:
    '''
    Replace variables in a dictionary
    
    Args:
        data: Dictionary to process
        
    Returns:
        Processed dictionary
    '''
    return {key: cls.replace(value) for key, value in data.items()}
  
  @classmethod
  def _replace_list(cls, data: list) -> list:
    '''
    Replace variables in a list
    
    Args:
        data: List to process
        
    Returns:
        Processed list
    '''
    return [cls.replace(item) for item in data]
  
  @classmethod
  def _replace_string(cls, data: str) -> any:
    '''
    Replace variables in a string
    
    Args:
        data: String to process
        
    Returns:
        Processed result, attempts to preserve original type for pure vars,
        otherwise returns a string
    '''
    # Check if the entire string is a single variable reference
    pure_var_match = cls._VAR_PATTERN.fullmatch(data)
    if pure_var_match:
      # Pure variable, try to get value and preserve type
      var_spec = pure_var_match.group(1)
      var_value = cls._get_var_value(var_spec)
      if var_value is not None:
        # Convert to string if it's not already a string
        if not isinstance(var_value, str):
          return var_value
        # Attempt type conversion for string values
        return cls._convert_type(var_value)
      return None
    
    # Not a pure variable, process all matches as strings
    def replacer(match):
      var_spec = match.group(1)
      var_value = cls._get_var_value(var_spec)
      return str(var_value) if var_value is not None else ''
    
    return cls._VAR_PATTERN.sub(replacer, data)
  
  @classmethod
  def _get_var_value(cls, var_spec: str) -> str | None:
    '''
    Get value from variable specification
    
    Args:
        var_spec: Variable specification, may contain default value,
                  format like "VAR" or "VAR:-default"
        
    Returns:
        Variable value or default value, None if both don't exist
    '''
    # Check if default value separator exists
    if ':-' in var_spec:
      var_name, default_value = var_spec.split(':-', 1)
      value = cls._get_raw_value(var_name)
      return value if value is not None else default_value
    else:
      # No default value, get directly
      return cls._get_raw_value(var_spec)
  
  @classmethod
  def _get_raw_value(cls, var_name: str) -> str | None:
    '''
    Get raw value for a variable name
    To be implemented by subclasses
    
    Args:
        var_name: Variable name
        
    Returns:
        Variable value or None if not found
    '''
    raise NotImplementedError("Subclasses must implement _get_raw_value method")
  
  @classmethod
  def _convert_type(cls, value: str) -> any:
    '''
    Attempt to convert string to appropriate data type
    
    Args:
        value: String value to convert
        
    Returns:
        Converted value
    '''
    # Try boolean conversion
    if value.lower() == 'true':
      return True
    elif value.lower() == 'false':
      return False
    
    # Try integer conversion
    try:
      return int(value)
    except ValueError:
      pass
    
    # Try float conversion
    try:
      return float(value)
    except ValueError:
      pass
    
    # Default to string
    return value