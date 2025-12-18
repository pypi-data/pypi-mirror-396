from blues_lib.util.NestedDataReader import NestedDataReader
from blues_lib.util.NestedDataWriter import NestedDataWriter
from blues_lib.util.NestedDataUpdater import NestedDataUpdater

class NestedDataMapping:
  """嵌套数据映射类，用于在源数据和目标数据之间进行基于路径的映射"""
  @classmethod
  def map(cls,source_data: any, source_path: str, target_data: any, target_path: str, map_method='assign', before_map:str='') -> bool:
    """
    将源数据中指定路径的值映射到目标数据的指定路径
    参数: 源数据、源路径、目标数据、目标路径、映射方法（'assign'或'update'）、映射前lambda函数(将源数据转换后再进行映射)
    返回: 映射是否成功
    """
    # 从源数据读取值
    value = NestedDataReader.read_by_path(source_data,source_path)
    value = cls.get_lambda_value(value,before_map)

    # 写入目标数据
    if map_method == 'update':
      return NestedDataUpdater.write_by_path(target_data,target_path,value)
    else:
      return NestedDataWriter.write_by_path(target_data,target_path,value)

  @classmethod
  def get_lambda_value(cls,source_value:any,before_map:str)->any:
    """
    根据lambda表达式转换源值
    参数: 源值、lambda表达式字符串
    返回: 转换后的值
    """
    if not before_map:
      return source_value

    func = eval(before_map)
    return func(source_value)