import re
from blues_lib.util.ResourceReader import ResourceReader
from blues_lib.util.DotFileReader import DotFileReader
from blues_lib.hocon.replacer.BaseReplacer import BaseReplacer

class IncludeReplacer(BaseReplacer):

  '''
  include 文件内容替换
  "%{include schema.except.stdout.200_list}" 内置json schema文件
  "%{include template.metadata.crawler.html}" 内置hocon template文件
  '''  
  INCLUDE_PATTERN = r"^%\{include\s+(schema|template)\.([a-zA-Z0-9_.-]+)\}$"
  
  def _replace_node_var(self, value:str)->str:
    """替换单个字符串中的占位符（要求完全匹配）"""
    # 检查是否为完整的 include 变量
    match = re.match(self.INCLUDE_PATTERN, value)
    if not match:
      return value

    root_name = match.group(1)  # 提取根目录部分
    dot_path = match.group(2)  # 提取文件dot路径 
    package = f'blues_lib.{root_name}' # pad the package name
    return self._read_template(package,dot_path)
    
  def _read_template(self,package:str,dot_path:str)->dict:
    extension:str = 'conf' # must be conf file
    slash_path:str = DotFileReader.get_slash_path(dot_path,extension)
    return ResourceReader.read_hocon(package, slash_path)
