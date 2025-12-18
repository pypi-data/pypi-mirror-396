import os
from blues_lib.util.BluesFiler import BluesFiler
from blues_lib.util.FileReader import FileReader

class DotFileReader:

  @classmethod
  def read_hocon(cls,project_dir:str,dot_path:str):
    '''
    @description: read conf file 
    @param {str} project_dir project root dir
    @param {str} dot_path dot path such as 'tests.mock.command.llm-loop-urls.def'
    @returns {dict|None}
    '''
    file_path = cls.get_file_path(project_dir,dot_path,'conf')
    return FileReader.read_hocon(file_path)

  @classmethod
  def read_text(cls,project_dir:str,dot_path:str):
    file_path = cls.get_file_path(project_dir,dot_path,'txt')
    return FileReader.read_text(file_path)
  
  @classmethod
  def read_json(cls,project_dir:str,dot_path:str):
    file_path = cls.get_file_path(project_dir,dot_path,'json')
    return FileReader.read_json(file_path)
  
  @classmethod
  def read_json(cls,project_dir:str,dot_path:str):
    file_path = cls.get_file_path(project_dir,dot_path,'json')
    return FileReader.read_json(file_path)
  
  @classmethod
  def read_json5(cls,project_dir:str,dot_path:str):
    file_path = cls.get_file_path(project_dir,dot_path,'json5')
    return FileReader.read_json5(file_path)
  
  @classmethod
  def read_yaml(cls,project_dir:str,dot_path:str):
    file_path = cls.get_file_path(project_dir,dot_path,'yaml')
    return FileReader.read_yaml(file_path)
  
  @classmethod
  def read_csv(cls,project_dir:str,dot_path:str):
    file_path = cls.get_file_path(project_dir,dot_path,'csv')
    return FileReader.read_csv(file_path)
  
  @classmethod
  def get_file_path(cls,project_dir:str,dot_path:str,extension:str='')->str:
    file_path = cls.get_slash_path(dot_path,extension)
    return BluesFiler.get_abs_path(project_dir,file_path)

  @classmethod
  def get_slash_path(cls, dot_path: str, extension: str = '') -> str:
    '''
    Convert dot-separated string to file path with optional extension.
    @param dot_path: Dot-separated path (e.g. 'blues_lib.util.BluesFiler' or 'config')
    @param extension: Optional file extension (e.g. 'json' or '.json', both are acceptable)
    @return: File path (e.g. 'blues_lib/util/BluesFiler.json' or 'config.yaml')
    '''
    # Handle empty dot_path
    if not dot_path:
      raise ValueError("dot_path cannot be empty")
    
    # Process extension: unify to ".ext" format (handle with/without leading dot)
    if extension:
      ext = extension if extension.startswith('.') else f'.{extension}'

    if '/' in dot_path or '\\' in dot_path:
      if not dot_path.endswith(ext) and ext:
        dot_path += ext
      return dot_path
     
    # Split dot-separated string into nodes
    path_nodes = dot_path.split('.')
    
    # Append extension to the last node (avoid duplicate extension)
    if not path_nodes[-1].endswith(ext) and ext:
      path_nodes[-1] += ext
    
    # Join nodes with OS-specific path separator
    return os.path.join(*path_nodes)