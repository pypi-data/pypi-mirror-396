from blues_lib.util.ResourceReader import ResourceReader
from blues_lib.util.DotFileReader import DotFileReader

class TemplateReader:
  
  PACKAGE = 'blues_lib.template'

  @classmethod
  def read(cls, dot_path:str) -> dict:
    extension:str = 'conf'
    slash_path:str = DotFileReader.get_slash_path(dot_path,extension)
    return ResourceReader.read_hocon(cls.PACKAGE, slash_path)
