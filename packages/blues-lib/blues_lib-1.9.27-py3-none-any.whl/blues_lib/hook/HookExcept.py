from blues_lib.schema.SchemaValidator import SchemaValidator

class HookExcept():

  @classmethod
  def validate(cls,hook_defs:list[dict])->None:
    prefix:str = f'hook :: '
    cls.validate_with_template(hook_defs,'hook',prefix)

  @classmethod
  def validate_with_template(cls,instance:any,tpl_path:str,prefix:str='')->None:
    prefix =  prefix if prefix else f'{tpl_path} :: '
    stat,message = SchemaValidator.validate_with_template(instance,tpl_path)
    if not stat:
      raise ValueError(f'{prefix}{message}')
    
  
    

    

    

    
