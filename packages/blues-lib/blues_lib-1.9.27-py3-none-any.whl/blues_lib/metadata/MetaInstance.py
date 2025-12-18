from blues_lib.util.ResourceReader import ResourceReader
from blues_lib.util.DotFileReader import DotFileReader

from blues_lib.metadata import instances  # 对应 instances 目录

class MetaInstance:

  @classmethod
  def get(cls, dot_path:str) -> dict:
    extension:str = 'conf'
    slash_path:str = DotFileReader.get_slash_path(dot_path,extension)
    return ResourceReader.read_hocon(instances, slash_path)
