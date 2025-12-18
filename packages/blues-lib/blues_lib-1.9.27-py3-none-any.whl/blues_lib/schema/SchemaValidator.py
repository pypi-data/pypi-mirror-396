import jsonschema
from blues_lib.schema.SchemaReader import SchemaReader

class SchemaValidator:
  """
  Class for validating metadata against JSON Schema templates
  """
  @classmethod
  def validate(cls, instance:any, schema:dict)->tuple[bool,str]:
    stat,message = SchemaValidator.validate_schema(schema)
    if not stat:
      return False, message

    try:
      jsonschema.validate(instance, schema)
      return True, 'validated'
    except jsonschema.exceptions.ValidationError as e:
      message:str = cls._get_message(e)
      return False, message
    except Exception as e:
      return False, str(e)

  @classmethod
  def validate_as_metadta(cls, instance:any, )->tuple[bool,str]:
    '''
    validate the metadata with a schema template
    - every metadata must has a 'tpl_id' field
    '''
    tpl_path:str = instance.get('tpl_id')
    if not tpl_path:
      return False, "metadata must has a 'tpl_id' field"
    return cls.validate_with_template(instance, tpl_path)

  @classmethod
  def validate_with_template(cls, instance:any, tpl_path:str)->tuple[bool,str]:
    '''
    Validate instance against JSON Schema template
    Args:
      instance: Instance to validate
      tpl_path: Path to JSON Schema template, such as 
        - 'dag' in root dir
        - 'metadata.llm' in sub dir
        - 'dag.json' with extension
    Returns:
      tuple[bool,str]: Validation result and message
    '''
    schema = SchemaReader.read(tpl_path)
    if not schema:
      return False, f"Schema template {tpl_path} not found"
    return cls.validate(instance, schema)
    
  @classmethod
  def _get_message(cls, validation_error):
    """
    Get validation error message
    Args:
        validation_error: jsonschema ValidationError object
    Returns:
        str: Formatted error message
    """
    # Get error path
    path = '/'.join(map(str, validation_error.path))
    return f"{validation_error.message} - at {path}"
    
  @classmethod
  def validate_schema(cls, schema)->tuple[bool,str]:
    """
    Validate if a schema is a valid JSON Schema
    Args:
      schema: Schema to validate
    Returns:
      bool: True if valid
    """
    try:
      jsonschema.validators.validator_for(schema).check_schema(schema)
      return True,''
    except Exception as e:
      return False, str(e)
    