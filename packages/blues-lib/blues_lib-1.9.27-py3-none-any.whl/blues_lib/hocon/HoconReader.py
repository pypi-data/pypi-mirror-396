from pyhocon import ConfigFactory
from pyhocon.config_tree import ConfigTree
from pyhocon.tool import HOCONConverter

class HoconReader:

  @classmethod
  def read(cls,file_path:str)->ConfigTree:
    '''
    @description: read conf file as ConfigTree
    @param {str} file path such as 'c:/blues-lib-py/tests/mock/command/llm-loop-urls/def.conf'
    @returns {ConfigTree}
    '''
    try:
      return ConfigFactory.parse_file(file_path)
    except Exception as e:
      print(f"read hocon error: {e}")
      return ConfigTree()

  @classmethod
  def read_as_dict(cls,file_path:str)->dict:
    '''
    @description: read conf file as dict
    @param {str} file path such as 'c:/blues-lib-py/tests/mock/command/llm-loop-urls/def.conf'
    @returns {dict}
    '''
    config:ConfigTree = cls.read(file_path)
    return config.as_plain_ordered_dict()

  @classmethod
  def read_as_hocon(cls,file_path:str)->str:
    '''
    @description: read conf file as hocon string
    @param {str} file path such as 'c:/blues-lib-py/tests/mock/command/llm-loop-urls/def.conf'
    @returns {str}
    '''
    config:ConfigTree = cls.read(file_path)
    return HOCONConverter.convert(config, 'hocon')

  @classmethod
  def read_as_json(cls,file_path:str)->str:
    '''
    @description: read conf file as json string
    @param {str} file path such as 'c:/blues-lib-py/tests/mock/command/llm-loop-urls/def.conf'
    @returns {str}
    '''
    config:ConfigTree = cls.read(file_path)
    return HOCONConverter.convert(config, 'json')
  
  @classmethod
  def read_as_yaml(cls,file_path:str)->str:
    '''
    @description: read conf file as yaml string
    @param {str} file path such as 'c:/blues-lib-py/tests/mock/command/llm-loop-urls/def.conf'
    @returns {str}
    '''
    config:ConfigTree = cls.read(file_path)
    return HOCONConverter.convert(config, 'yaml')
  
  @classmethod
  def read_as_properties(cls,file_path:str)->str:
    '''
    @description: read conf file as properties string
    @param {str} file path such as 'c:/blues-lib-py/tests/mock/command/llm-loop-urls/def.conf'
    @returns {str}
    '''
    config:ConfigTree = cls.read(file_path)
    return HOCONConverter.convert(config, 'properties')
