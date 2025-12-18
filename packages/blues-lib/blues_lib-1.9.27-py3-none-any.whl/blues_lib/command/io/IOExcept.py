from blues_lib.schema.SchemaValidator import SchemaValidator
from blues_lib.type.output.STDOut import STDOut

class IOExcept():

  @classmethod
  def validate_dag(cls,def_def:dict)->None:
    prefix:str = f'{def_def.get("dag_id")} dag :: '
    cls.validate_with_template(prefix,def_def,'dag')
    
  @classmethod
  def validate_task(cls,task_def:dict)->None:
    prefix:str = f'{task_def.get("task_id")} [{task_def.get("command")}] task :: '
    cls.validate_with_template(prefix,task_def,'task')
    
  @classmethod
  def validate_task_input(cls,task_def:dict)->None:
    input_defs:list[dict]|None = task_def.get('input')
    if not input_defs:
      return

    prefix:str = f'{task_def.get("task_id")} [{task_def.get("command")}] input :: '
    cls.validate_with_template(prefix,input_defs,'input')
    
  @classmethod
  def validate_metadata(cls,metadata:dict):
    # the $id identify the metadata's schema dot path
    if not (tpl_path := metadata.get('$id')):
      return

    prefix:str = f'{tpl_path} :: '
    cls.validate_with_template(prefix,metadata,tpl_path)
    

  @classmethod
  def validate_except(cls,task_def:dict,stdout:STDOut|None)->None:
    schema = task_def.get('except')
    if not schema:
      return 

    prefix:str = f'{task_def.get("task_id")} [{task_def.get("command")}] except :: '
    if not stdout:
      raise ValueError(f'{prefix}stdout is None')

    instance = stdout.to_dict()
    if isinstance(schema,str):
      tpl_path = f'except.{schema}'
      cls.validate_with_template(prefix,instance,tpl_path)
    else:
      cls.validate(prefix,instance,schema)
    

  @classmethod
  def validate_with_template(cls,prefix:str,instance:any,tpl_path:str)->None:
    prefix =  prefix if prefix else f'{tpl_path} :: '
    stat,message = SchemaValidator.validate_with_template(instance,tpl_path)
    if not stat:
      raise ValueError(f'{prefix}{message}')
    
  @classmethod
  def validate(cls,prefix:str,instance:any,schema:dict)->None:
    prefix =  prefix if prefix else 'schema validate :: '
    stat,message = SchemaValidator.validate(instance,schema)
    if not stat:
      raise ValueError(f'{prefix}{message}')
    
  
    

    

    

    

    

    

    

    
