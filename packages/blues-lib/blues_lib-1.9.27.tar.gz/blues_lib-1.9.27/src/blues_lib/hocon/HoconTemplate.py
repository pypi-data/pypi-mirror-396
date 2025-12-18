class HoconTemplate:
  
  @classmethod
  def include(cls,template:dict)->None:
    '''
    @description: replace the node value with the include file value
    @syntax: "%{include schema.except.stdout.200_list}"
      - update the dict directly
      - only support built-in file path
    @param {dict} config template dict
    @returns {None}
    '''
    return cls(**template)
